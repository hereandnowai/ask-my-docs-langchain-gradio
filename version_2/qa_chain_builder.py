import os
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from llm_utils import llm
from metadata_schema import DOCUMENT_DESCRIPTION, metadata_field_info
from vector_store_manager import get_vector_store_instance

def get_qa_chain():
    """Builds and returns a SelfQueryRetriever."""
    vector_store_instance = get_vector_store_instance()
    if vector_store_instance is None:
        return None

    return SelfQueryRetriever.from_llm(
        llm,
        vector_store_instance,
        DOCUMENT_DESCRIPTION,
        metadata_field_info,
        verbose=True,
        search_kwargs={"k": 100} # Retrieve up to 100 documents
    )

def get_answer(question):
    """Handles the question asking logic."""
    if not question:
        return "Please enter a question.", ""
    
    retriever = get_qa_chain()
    if retriever is None:
        return "The knowledge base has not been created yet. Please process your PDFs first.", ""

    try:
        # Use the retriever to get relevant documents
        retrieved_docs = retriever.invoke(question)
        print(f"\nRetrieved Documents ({len(retrieved_docs)}):\n")
        for i, doc in enumerate(retrieved_docs):
            print(f"Document {i+1}:\n  Page Content (first 100 chars): {doc.page_content[:100]}...\n  Metadata: {doc.metadata}\n")

        # If the query is aggregative, calculate the result
        if any(word in question.lower() for word in ["total", "sum", "count", "average"]):
            total_value = 0
            invoice_count = 0
            seen_invoices = set()

            for doc in retrieved_docs:
                invoice_id = (doc.metadata.get("invoice_number"), doc.metadata.get("source"))
                if invoice_id not in seen_invoices:
                    total_value += doc.metadata.get("total_value", 0)
                    invoice_count += 1
                    seen_invoices.add(invoice_id)

            answer = f"Found {invoice_count} invoices. The total value is {total_value:.2f}."
            sources = "\n".join([f"- {os.path.basename(doc.metadata.get('source', 'Unknown'))}" for doc in retrieved_docs])
            return answer, sources

        # Otherwise, use the standard QA chain with LCEL
        else:
            prompt_template = '''
    Use the following pieces of context from the uploaded documents to answer the question at the end.
    If you don't know the answer based on the provided context, just say that you don't know. Do not make up an answer.
    Keep the answer concise and helpful.

    Context:
    {context}

    Question: {question}

    Helpful Answer:
    '''
            QA_PROMPT = PromptTemplate.from_template(prompt_template)

            rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()} 
                | QA_PROMPT 
                | llm 
                | StrOutputParser()
            )
            
            answer = rag_chain.invoke(question)
            sources = "\n".join(
                [f"- {os.path.basename(doc.metadata.get('source', 'Unknown'))}, page {doc.metadata.get('page', 'N/A')}"
                 for doc in retrieved_docs]
            )
            return answer, sources

    except Exception as e:
        print(f"Error during Q&A: {e}")
        return "An error occurred while generating the answer.", ""
