# Ask My Docs - LangChain & Gradio

This project is an open-source, retrieval-augmented generation (RAG) application that allows you to ask questions about multiple PDF documents.

It uses a Gradio frontend for file uploads and Q&A, and a LangChain backend powered by Gemini for processing and answering questions.

## Features

- **Upload Multiple PDFs**: Easily upload one or more PDF files through the web interface.
- **Ask Questions**: Pose questions to your documents.
- **Source Attribution**: The model provides answers and cites the source document(s) and page numbers.
- **Powered by Gemini**: Utilizes Google's Gemini model for high-quality answers.
- **Modular & Extensible**: Built with LangChain runnables for future customization.

## Getting Started

### Prerequisites

- Python 3.9+
- A Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ask-my-docs-langchain-gradio.git
    cd ask-my-docs-langchain-gradio
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    - Create a file named `.env` in the root directory.
    - Add your Gemini API key to it:
      ```
      GEMINI_API_KEY="YOUR_API_KEY_HERE"
      ```

### Running the Application

1.  **Start the Gradio app:**
    ```bash
    python app.py
    ```

2.  **Open your browser** and navigate to the local URL provided (usually `http://127.0.0.1:7860`).

## How to Use

1.  **Upload PDFs**: Drag and drop or click to upload the PDF files you want to query.
2.  **Ask a Question**: Type your question in the text box.
3.  **Submit**: Click the "Ask" button.
4.  **View Results**: The application will display the question, the generated answer, and the sources from which the answer was derived.