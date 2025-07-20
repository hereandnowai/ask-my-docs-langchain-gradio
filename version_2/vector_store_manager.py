import os
import shutil
import gradio as gr
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import PDFS_DIR, VECTOR_STORE_DIR, COLLECTION_NAME
from llm_utils import embeddings, llm
from metadata_extractor import extract_metadata_from_document

vector_store_instance = None

def get_vector_store_instance():
    global vector_store_instance
    if vector_store_instance is None:
        try:
            client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
            vector_store_instance = Chroma(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
            )
        except Exception as e:
            print(f"Failed to load vector store from disk: {e}")
            return None
    return vector_store_instance

def add_to_vector_store(files):
    """
    Adds new, non-duplicate PDFs to the vector store.
    Checks for existing filenames to prevent duplication.
    """
    global vector_store_instance
    new_pdf_paths = []
    skipped_files = []
    for file in files:
        dest_path = os.path.join(PDFS_DIR, os.path.basename(file.name))
        if os.path.exists(dest_path):
            skipped_files.append(os.path.basename(file.name))
            continue # Skip file if it already exists
        
        shutil.copy(file.name, dest_path)
        new_pdf_paths.append(dest_path)

    if not new_pdf_paths:
        status = "Status: All selected files already exist in the knowledge base."
        if skipped_files:
            status += f" Skipped: {', '.join(skipped_files)}"
        return status, gr.update(choices=get_pdf_list())

    print(f"Adding {len(new_pdf_paths)} new PDF(s) to the knowledge base...")
    documents = []
    failed_files = []
    for pdf_path in new_pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            doc_pages = loader.load()
            # Extract metadata from the first page
            metadata = extract_metadata_from_document(doc_pages[0].page_content, llm)
            for page in doc_pages:
                page.metadata.update(metadata)
                page.metadata["source"] = pdf_path # Ensure source is correctly set
            documents.extend(doc_pages)
        except Exception as e:
            print(f"Error loading {os.path.basename(pdf_path)}: {e}")
            failed_files.append(os.path.basename(pdf_path))

    if not documents:
        return "Status: Could not extract text from the new PDFs.", gr.update(choices=get_pdf_list())

    texts = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)

    # Load existing vector store or create if it doesn't exist
    if vector_store_instance is None:
        try:
            # Ensure the client and collection exist before trying to add to them
            client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
            vector_store_instance = Chroma(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
            )
            # Check if collection is empty, if so, use from_documents to create it
            if vector_store_instance._collection.count() == 0:
                 vector_store_instance = Chroma.from_documents(
                    documents=texts, embedding=embeddings, client=client,
                    collection_name=COLLECTION_NAME, persist_directory=VECTOR_STORE_DIR
                )
            else:
                vector_store_instance.add_documents(documents=texts)

        except Exception as e:
            print(f"Failed to load vector store, creating a new one: {e}")
            client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
            vector_store_instance = Chroma.from_documents(
                documents=texts, embedding=embeddings, client=client,
                collection_name=COLLECTION_NAME, persist_directory=VECTOR_STORE_DIR
            )
    else:
        vector_store_instance.add_documents(documents=texts)
    
    total_docs_in_chroma = vector_store_instance._collection.count()
    status = f"Status: Added {len(new_pdf_paths) - len(failed_files)} new PDF(s). Knowledge base now contains {total_docs_in_chroma} document(s) in ChromaDB."
    if skipped_files:
        status += f" Skipped {len(skipped_files)} existing file(s)."
    if failed_files:
        status += f" Failed to process: {', '.join(failed_files)}."
    return status, gr.update(choices=get_pdf_list())

def remove_selected_pdf(pdf_to_remove):
    """Removes a specific PDF file and its embeddings from the vector store."""
    global vector_store_instance
    if not pdf_to_remove:
        return "Status: No PDF selected for removal."

    pdf_path = os.path.join(PDFS_DIR, pdf_to_remove)
    
    if not os.path.exists(pdf_path):
        return f"Status: Error - {pdf_to_remove} not found."

    try:
        # 1. Remove from vector store
        if vector_store_instance is None and os.path.exists(VECTOR_STORE_DIR) and os.listdir(VECTOR_STORE_DIR):
             vector_store_instance = Chroma(
                client=chromadb.PersistentClient(path=VECTOR_STORE_DIR),
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
            )

        if vector_store_instance is not None:
            ids_to_delete = []
            all_docs = vector_store_instance._collection.get(include=["metadatas"])
            for i, meta in enumerate(all_docs['metadatas']):
                if meta.get('source') and os.path.basename(meta['source']) == pdf_to_remove:
                    ids_to_delete.append(all_docs['ids'][i])

            if ids_to_delete:
                vector_store_instance._collection.delete(ids=ids_to_delete)
                print(f"Removed {len(ids_to_delete)} vectors for {pdf_to_remove}.")

        # 2. Delete the file
        os.remove(pdf_path)
        
        return f"Status: Removed {pdf_to_remove}. Knowledge base updated.", gr.update(choices=get_pdf_list(), value=None)

    except Exception as e:
        print(f"Error removing {pdf_to_remove}: {e}")
        return f"Status: An error occurred while removing the file.", gr.update(choices=get_pdf_list())

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
    
    return "Status: All documents and knowledge base have been cleared.", gr.update(choices=[], value=None)

def get_pdf_list():
    """Returns a list of PDF filenames in the PDFs directory."""
    return [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]
