import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY or API_KEY == "":
    raise ValueError(
        "GEMINI_API_KEY not found or not set. Please get a key from https://aistudio.google.com/app/apikey and set it in the .env file."
    )

PDFS_DIR = "PDFs"
VECTOR_STORE_DIR = "vector_store"
COLLECTION_NAME = "ask_my_docs_collection"

os.makedirs(PDFS_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
