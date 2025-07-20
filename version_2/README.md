<div align="center">
  <a href="https://hereandnowai.com">
    <img src="https://raw.githubusercontent.com/hereandnowai/images/refs/heads/main/logos/HNAI%20Title%20-Teal%20%26%20Golden%20Logo%20-%20DESIGN%203%20-%20Raj-07.png" alt="HERE AND NOW AI Logo" width="400"/>
  </a>
  <br/>
  <h1>Ask My Docs: Multi-PDF Q&A with LangChain & Gemini</h1>
  <p><i>designed with passion for innovation</i></p>
</div>

---

This project is an open-source, retrieval-augmented generation (RAG) application that allows you to ask questions about multiple PDF documents simultaneously. It uses a Gradio frontend for an intuitive user experience and a LangChain backend powered by Google's Gemini model to deliver accurate, source-cited answers.

### Built by [HERE AND NOW AI](https://hereandnowai.com)
This application was designed and developed by the team at **HERE AND NOW AI**, a company dedicated to crafting innovative AI solutions. We are passionate about creating powerful, user-friendly applications that leverage the latest advancements in artificial intelligence.

---

## Features
- **Upload Multiple PDFs**: Easily upload one or more PDF files through the web interface.
- **Persistent Knowledge**: Your documents are saved and indexed, allowing you to build a knowledge base over time.
- **Ask Questions**: Pose questions to your documents in natural language.
- **Source Attribution**: The model provides answers and cites the specific source document(s) and page numbers.
- **Powered by Gemini**: Utilizes Google's `gemini-1.5-flash` model for high-quality, efficient answers.
- **Clean Slate**: A "Clear All Data" button allows you to reset the knowledge base and start fresh at any time.

## Getting Started

### Prerequisites
- Python 3.9+
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hereandnowai/ask-my-docs-langchain-gradio.git
    cd ask-my-docs-langchain-gradio
    ```

2.  **Create and activate a virtual environment:**

    -   **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    -   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    - Create a file named `.env` in the root directory by copying the example:
      ```
      # (Use 'copy' on Windows)
      cp .env.example .env
      ```
    - Add your Gemini API key to the `.env` file:
      ```
      GEMINI_API_KEY="YOUR_API_KEY_HERE"
      ```

## How to Use

1.  **Start the application:**
    ```bash
    python app.py
    ```

2.  **Open your browser** and navigate to the local URL provided (usually `http://127.0.0.1:7860`).

3.  **Upload PDFs**: Drag and drop or click to upload the PDF files you want to query.

4.  **Create/Update Knowledge Base**: Click the **"Create/Update Knowledge Base"** button. This processes all uploaded PDFs and makes them ready for questions.

5.  **Ask a Question**: Type your question in the text box and click **"Get Answer"**.

6.  **View Results**: The application will display the question, the generated answer, and the sources from which the answer was derived.

7.  **Clear Data**: To start over, click the **"Clear All Data"** button. This will delete all uploaded PDFs and the existing knowledge base.

---

## Connect with Us
Stay up to date with our latest projects and innovations:

- **Website**: [hereandnowai.com](https://hereandnowai.com)
- **GitHub**: [@hereandnowai](https://github.com/hereandnowai)
- **LinkedIn**: [HERE AND NOW AI](https://www.linkedin.com/company/hereandnowai/)
- **X (Twitter)**: [@hereandnow_ai](https://x.com/hereandnow_ai)
- **Instagram**: [@hereandnow_ai](https://instagram.com/hereandnow_ai)
- **YouTube**: [@hereandnow_ai](https://youtube.com/@hereandnow_ai)
- **Blog**: [Our Blog](https://hereandnowai.com/blog)

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
