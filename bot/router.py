import chainlit as cl
from bot.handlers.chat import handle_chat


async def route(message: cl.Message):
    user_type = cl.user_session.get("user_type")
    await handle_chat(message.content, user_type)
