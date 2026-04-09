import json
import logging
import time

import chainlit as cl
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, TOP_K
from rag.retriever import retrieve
from bot.tools.fare_data import FARE_TOOL_DEFINITION, execute_tool
from bot.tools.query_rewriter import rewrite_query

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_TEMPLATE = '''<persona>
Bạn là trợ lý ảo hỗ trợ trả lời các câu hỏi liên quan đến dịch vụ taxi công nghệ thuần điện và giao đồ ăn XanhSM.
Nhiệm vụ của bạn là trả lời câu hỏi của hành khách, tài xế taxi, tài xế bike, hoặc nhà hàng dựa trên thông tin được cung cấp.
Hãy trả lời câu hỏi lịch sự và thân thiện như một tư vấn viên chuyên nghiệp.
</persona>

<user_profile>
Loại người dùng: {user_type_label}
</user_profile>

<rules>
- Trả lời bằng ngôn ngữ nguời dùng đã sử dụng trong câu hỏi.
- Nếu câu hỏi không rõ, hãy hỏi lại khách hàng để làm rõ câu hỏi.
- Nếu loại người dùng là "Chưa xác định" VÀ câu trả lời có sự khác biệt giữa tài xế bike và tài xế taxi (ví dụ: lương, chính sách, quyền lợi), hãy hỏi người dùng họ là tài xế bike hay tài xế taxi trước khi trả lời.
- Trả lời câu hỏi dựa trên thông tin được cung cấp trong phần <context> bên dưới. Không sử dụng kiến thức bên ngoài phần này.
- Thông tin [Chính thức] là nguồn đáng tin cậy, ưu tiên sử dụng để trả lời.
- Thông tin [Cộng đồng] là bình luận từ người dùng trên mạng xã hội, KHÔNG phải câu trả lời chính thức. Chỉ dùng để hiểu thêm ngữ cảnh, KHÔNG được trích dẫn hoặc lặp lại nội dung này như câu trả lời.
- Khi người dùng hỏi về giá cước, phí đi xe, chi phí chuyến đi tại một thành phố cụ thể, hãy sử dụng tool lookup_fare để tra cứu và trình bày kết quả rõ ràng.
</rules>

<context>
{context}
</context>

<constraints>
- Nếu không tìm thấy thông tin liên quan trong phần <context>, hãy trả lời rằng bạn không tìm thấy thông tin, không bịa câu trả lời.
- Từ chối mọi câu hỏi không liên quan đến dịch vụ của XanhSM (VD: viết code, làm bài tập, tư vấn tài chính, chính trị).
</constraints>
'''

BOT_NAME = "XanhSM"

TOOLS = [FARE_TOOL_DEFINITION]


async def handle_chat(user_message: str, user_type: str):
    t0 = time.monotonic()
    logger.info("[CHAT] user_type=%s | msg=%r", user_type, user_message[:100])

    history: list[dict] = cl.user_session.get("history") or []
    rag_query = await rewrite_query(user_message, history)

    chunks = retrieve(rag_query, user_type, top_k=TOP_K)

    if chunks:
        parts = []
        for c in chunks:
            label = "[Cộng đồng]" if c["category"] == "community" else "[Chính thức]"
            parts.append(f"{label}\nQ: {c['question']}\nA: {c['answer']}")
        context = "\n\n".join(parts)
    else:
        context = "(Không tìm thấy thông tin liên quan.)"
        logger.warning("[CHAT] No RAG chunks found for query=%r", user_message[:80])

    user_type_labels = {
        "tai_xe_bike": "Tài xế Bike",
        "tai_xe_taxi": "Tài xế Taxi",
        "nguoi_dung": "Hành khách",
        "nha_hang": "Nhà hàng",
    }
    user_type_label = user_type_labels.get(user_type, "Chưa xác định")
    system_prompt = SYSTEM_TEMPLATE.format(context=context, user_type_label=user_type_label)

    history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": system_prompt}] + history

    msg = cl.Message(content="", author=BOT_NAME)
    await msg.send()

    full_response = await _chat_with_tools(messages, msg)

    await msg.update()

    elapsed = time.monotonic() - t0
    logger.info(
        "[CHAT] done | %.2fs | history_turns=%d | response_len=%d",
        elapsed, len(history), len(full_response),
    )

    history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("history", history)


async def _chat_with_tools(messages: list[dict], msg: cl.Message) -> str:
    """
    Gọi OpenAI với tool support (streaming).
    - Lượt 1: stream và thu thập tool calls nếu có.
    - Nếu model gọi tool: thực thi → lượt 2 stream câu trả lời cuối.
    - Nếu không có tool call: trả về nội dung lượt 1.
    """
    # --- Lượt 1 ---
    stream = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        stream=True,
    )

    tool_calls_acc: dict[int, dict] = {}  # index → {"id", "name", "arguments"}
    first_response_content = ""
    finish_reason = None
    assistant_message_dict: dict = {"role": "assistant", "content": None, "tool_calls": []}

    async for chunk in stream:
        choice = chunk.choices[0]
        if choice.finish_reason:
            finish_reason = choice.finish_reason
        delta = choice.delta

        # Stream văn bản bình thường
        if delta.content:
            first_response_content += delta.content
            await msg.stream_token(delta.content)

        # Thu thập tool call chunks
        if delta.tool_calls:
            for tc_chunk in delta.tool_calls:
                idx = tc_chunk.index
                if idx not in tool_calls_acc:
                    tool_calls_acc[idx] = {"id": "", "name": "", "arguments": ""}
                if tc_chunk.id:
                    tool_calls_acc[idx]["id"] += tc_chunk.id
                if tc_chunk.function and tc_chunk.function.name:
                    tool_calls_acc[idx]["name"] += tc_chunk.function.name
                if tc_chunk.function and tc_chunk.function.arguments:
                    tool_calls_acc[idx]["arguments"] += tc_chunk.function.arguments

    # Không có tool call → trả về luôn
    if finish_reason != "tool_calls" or not tool_calls_acc:
        return first_response_content

    # --- Thực thi tool calls ---
    tool_calls_list = []
    tool_result_messages = []

    for idx in sorted(tool_calls_acc):
        tc = tool_calls_acc[idx]
        tool_calls_list.append({
            "id": tc["id"],
            "type": "function",
            "function": {"name": tc["name"], "arguments": tc["arguments"]},
        })
        try:
            args = json.loads(tc["arguments"])
        except json.JSONDecodeError:
            args = {}

        logger.info("[TOOL] calling %s args=%r", tc["name"], args)
        result = execute_tool(tc["name"], args)

        tool_result_messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": result,
        })

    # Lắp assistant message có tool_calls vào history
    assistant_message_dict["tool_calls"] = tool_calls_list
    if first_response_content:
        assistant_message_dict["content"] = first_response_content

    updated_messages = messages + [assistant_message_dict] + tool_result_messages

    # --- Lượt 2: stream câu trả lời cuối ---
    stream2 = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=updated_messages,
        stream=True,
    )

    final_response = ""
    async for chunk in stream2:
        delta = chunk.choices[0].delta.content
        if delta:
            final_response += delta
            await msg.stream_token(delta)

    return final_response
