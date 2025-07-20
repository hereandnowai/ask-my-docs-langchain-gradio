import os
import shutil
import gradio as gr
import chromadb
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# --- PROJECT SETUP ---
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    raise ValueError(
        "GEMINI_API_KEY not found or not set. Please get a key from https://aistudio.google.com/app/apikey and set it in the .env file."
    )

# --- CONSTANTS & DIRECTORIES ---
PDFS_DIR = "PDFs"
VECTOR_STORE_DIR = "vector_store"
COLLECTION_NAME = "ask_my_docs_collection"
os.makedirs(PDFS_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# --- STATE MANAGEMENT ---
vector_store_instance = None

# --- CORE LOGIC ---

def rebuild_vector_store(files):
    """Rebuilds the vector store from ALL PDFs in the PDFs directory."""
    global vector_store_instance
    if files:
        for file in files:
            shutil.copy(file.name, os.path.join(PDFS_DIR, os.path.basename(file.name)))

    pdf_files = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]
    if not pdf_files:
        return "Status: No PDF files found. Please upload at least one."

    print("Rebuilding knowledge base...")
    documents = []
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(os.path.join(PDFS_DIR, pdf_file))
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
    
    if not documents:
        return "Status: Could not extract text from any PDFs."

    texts = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
    
    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Collection deletion failed (might not exist): {e}")

    vector_store_instance = Chroma.from_documents(
        documents=texts, embedding=embeddings, client=client,
        collection_name=COLLECTION_NAME, persist_directory=VECTOR_STORE_DIR
    )
    return f"Status: Knowledge base created from {len(pdf_files)} PDF(s). Ready for questions."

def get_answer(question):
    """Handles the question asking logic."""
    if not question:
        return "Please enter a question.", ""
    
    qa_chain = get_qa_chain()
    if qa_chain is None:
        return "The knowledge base has not been created yet. Please process your PDFs first.", ""

    try:
        result = qa_chain.invoke({"query": question})
        answer = result.get("result", "No answer found.")
        sources = "\n".join(
            [f"- {os.path.basename(doc.metadata.get('source', 'Unknown'))}, page {doc.metadata.get('page', 'N/A')}"
             for doc in result.get("source_documents", [])]
        )
        return answer, sources
    except Exception as e:
        print(f"Error during Q&A: {e}")
        return "An error occurred while generating the answer.", ""

def clear_all_data():
    """Clears the vector store collection and all PDFs."""
    global vector_store_instance
    vector_store_instance = None
    
    try:
        client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        client.delete_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Could not clear collection (it might not exist): {e}")

    if os.path.exists(PDFS_DIR):
        shutil.rmtree(PDFS_DIR)
    os.makedirs(PDFS_DIR)
    
    return "Status: All documents and knowledge base have been cleared."

# --- LANGCHAIN SETUP ---

def get_qa_chain():
    """Builds and returns a RetrievalQA chain using the vector store."""
    global vector_store_instance
    if vector_store_instance is None:
        if not os.listdir(VECTOR_STORE_DIR): return None
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
            vector_store_instance = Chroma(
                client=chromadb.PersistentClient(path=VECTOR_STORE_DIR),
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
            )
        except Exception as e:
            print(f"Failed to load vector store from disk: {e}")
            return None

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=API_KEY)
    retriever = vector_store_instance.as_retriever(search_kwargs={"k": 5})
    
    prompt_template = """
    Use the following pieces of context from the uploaded documents to answer the question at the end.
    If you don't know the answer based on the provided context, just say that you don't know. Do not make up an answer.
    Keep the answer concise and helpful.

    Context:
    {context}

    Question: {question}

    Helpful Answer:
    """
    QA_PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    return RetrievalQA.from_chain_type(
        llm, retriever=retriever, chain_type_kwargs={"prompt": QA_PROMPT}, return_source_documents=True
    )

# --- GRADIO UI SETUP ---

def setup_gradio_ui():
    """Sets up and launches the Gradio web interface."""
    with gr.Blocks(theme=gr.themes.Soft(), title="Ask My Docs") as app:
        gr.Markdown("# Ask Questions to Your PDF Documents")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Manage Documents")
                file_uploader = gr.File(label="Upload PDFs", file_count="multiple", file_types=[".pdf"])
                process_button = gr.Button("Create/Update Knowledge Base", variant="primary")
                clear_button = gr.Button("Clear All Data", variant="stop")
                processing_status = gr.Markdown("Status: Ready. Upload PDFs and create the knowledge base.")

            with gr.Column(scale=2):
                gr.Markdown("### 2. Ask a Question")
                question_input = gr.Textbox(label="Question", placeholder="e.g., What is the main topic of the document?")
                ask_button = gr.Button("Get Answer", variant="secondary")
                
                gr.Markdown("---")
                gr.Markdown("### Answer")
                answer_output = gr.Markdown("Your answer will appear here...")
                gr.Markdown("### Sources")
                sources_output = gr.Markdown("Source documents will be listed here...")

        # Link UI components to the core logic functions
        process_button.click(rebuild_vector_store, inputs=[file_uploader], outputs=[processing_status])
        ask_button.click(get_answer, inputs=[question_input], outputs=[answer_output, sources_output])
        clear_button.click(clear_all_data, inputs=[], outputs=[processing_status])

    return app

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    gradio_app = setup_gradio_ui()
    gradio_app.launch(share=True, debug=True)