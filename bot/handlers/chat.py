import logging
import time

import chainlit as cl
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, TOP_K
from rag.retriever import retrieve

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_TEMPLATE = '''<persona>
Bạn là trợ lý ảo hỗ trợ trả lời các câu hỏi liên quan đến dịch vụ taxi công nghệ thuần điện và giao đồ ăn XanhSM.
Nhiệm vụ của bạn là trả lời câu hỏi của hành khách, tài xế taxi, tài xế bike, hoặc nhà hàng dựa trên thông tin được cung cấp.
Hãy trả lời câu hỏi lịch sự và thân thiện như một tư vấn viên chuyên nghiệp.
</persona>

<rules>
- Trả lời bằng ngôn ngữ nguời dùng đã sử dụng trong câu hỏi.
- Nếu câu hỏi không rõ, hãy hỏi lại khách hàng để làm rõ câu hỏi.
- Trả lời câu hỏi dựa trên thông tin được cung cấp trong phần <context> bên dưới. Không sử dụng kiến thức bên ngoài phần này.
- Thông tin [Chính thức] là nguồn đáng tin cậy, ưu tiên sử dụng để trả lời.
- Thông tin [Cộng đồng] là bình luận từ người dùng trên mạng xã hội, KHÔNG phải câu trả lời chính thức. Chỉ dùng để hiểu thêm ngữ cảnh, KHÔNG được trích dẫn hoặc lặp lại nội dung này như câu trả lời.
</rules>

<context>
{context}
</context>

<constraints>
- Nếu không tìm thấy thông tin liên quan trong phần <context>, hãy trả lời rằng bạn không tìm thấy thông tin, không bịa câu trả lời.
- Từ chối mọi câu hỏi không liên quan đến dịch vụ của XanhSM (VD: viết code, làm bài tập, tư vấn tài chính, chính trị).
</constraints>
'''


async def handle_chat(user_message: str, user_type: str):
    t0 = time.monotonic()
    logger.info("[CHAT] user_type=%s | msg=%r", user_type, user_message[:100])

    chunks = retrieve(user_message, user_type, top_k=TOP_K)

    if chunks:
        parts = []
        for c in chunks:
            label = "[Cộng đồng]" if c["category"] == "community" else "[Chính thức]"
            parts.append(f"{label}\nQ: {c['question']}\nA: {c['answer']}")
        context = "\n\n".join(parts)
    else:
        context = "(Không tìm thấy thông tin liên quan.)"
        logger.warning("[CHAT] No RAG chunks found for query=%r", user_message[:80])

    system_prompt = SYSTEM_TEMPLATE.format(context=context)

    history: list[dict] = cl.user_session.get("history") or []
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": system_prompt}] + history

    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    stream = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            full_response += delta
            await msg.stream_token(delta)

    await msg.update()

    elapsed = time.monotonic() - t0
    logger.info(
        "[CHAT] done | %.2fs | history_turns=%d | response_len=%d",
        elapsed, len(history), len(full_response),
    )

    history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("history", history)
