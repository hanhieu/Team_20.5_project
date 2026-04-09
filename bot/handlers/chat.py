import logging
import time

import chainlit as cl
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, TOP_K
from rag.retriever import retrieve

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_TEMPLATE = (
    "Bạn là trợ lý hỗ trợ khách hàng Xanh SM. "
    "Chỉ trả lời dựa trên thông tin dưới đây. "
    "Nếu không có thông tin phù hợp, hãy nói rằng bạn không có thông tin về vấn đề này.\n\n"
    "{context}"
)


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
