import logging

import chainlit as cl
import chainlit.data as cl_data
from bot.data_layer import LocalFeedbackDataLayer
from bot.handlers.onboarding import ask_user_type
from bot.router import route
from rag.vectorstore import get_collection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
# Suppress noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("chainlit").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ── Register custom data layer ────────────────────────────────────────────────
# This is REQUIRED for Chainlit to show 👍/👎 buttons on assistant messages.
# The layer stores feedback locally (data/feedback.jsonl) without any DB.
@cl.data_layer
def get_data_layer():
    return LocalFeedbackDataLayer()

# Warm up embedding model at import time so first request isn't slow
logger.info("[STARTUP] Loading embedding model...")
get_collection()
logger.info("[STARTUP] Embedding model ready.")


@cl.on_chat_start
async def on_chat_start():
    await ask_user_type()


@cl.on_message
async def on_message(message: cl.Message):
    await route(message)
