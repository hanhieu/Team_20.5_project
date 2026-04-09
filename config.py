import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
CHROMA_PATH = ".chromadb"
COLLECTION_NAME = "xanhsm_qa"
EMBEDDING_MODEL = "keepitreal/vietnamese-sbert"
TOP_K = 2  # per search (user_type + all), max ~4 unique chunks total
