from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from config import API_KEY

try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-lite-preview-06-17", temperature=0, google_api_key=API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Google AI models. Check your API key and network connection. Error: {e}")
