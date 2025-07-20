import gradio as gr
from vector_store_manager import add_to_vector_store, remove_selected_pdf, clear_all_data, get_pdf_list
from qa_chain_builder import get_answer

# --- GRADIO UI SETUP ---

def setup_gradio_ui():
    """Sets up and launches the Gradio web interface."""
    with gr.Blocks(theme=gr.themes.Soft(), title="Ask My Docs") as app:
        gr.Markdown("# Ask Questions to Your PDF Documents")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Manage Documents")
                file_uploader = gr.File(label="Upload PDFs", file_count="multiple", file_types=[".pdf"])
                process_button = gr.Button("Add to Knowledge Base", variant="primary")
                
                gr.Markdown("### 2. Current Documents")
                pdf_list_dropdown = gr.Dropdown(label="Select PDF to Remove", choices=get_pdf_list(), interactive=True)
                remove_button = gr.Button("Remove Selected PDF", variant="secondary")
                clear_button = gr.Button("Clear All Data", variant="stop")
                
                processing_status = gr.Markdown("Status: Ready. Upload PDFs and create the knowledge base.")

            with gr.Column(scale=2):
                gr.Markdown("### 3. Ask a Question")
                question_input = gr.Textbox(label="Question", placeholder="e.g., What is the main topic of the document?")
                ask_button = gr.Button("Get Answer", variant="secondary")
                
                gr.Markdown("---")
                gr.Markdown("### Answer")
                answer_output = gr.Markdown("Your answer will appear here...")
                gr.Markdown("### Sources")
                sources_output = gr.Markdown("Source documents will be listed here...")

        # Link UI components to the core logic functions
        process_button.click(
            add_to_vector_store, 
            inputs=[file_uploader], 
            outputs=[processing_status, pdf_list_dropdown]
        )
        ask_button.click(
            get_answer, 
            inputs=[question_input], 
            outputs=[answer_output, sources_output]
        )
        remove_button.click(
            remove_selected_pdf,
            inputs=[pdf_list_dropdown],
            outputs=[processing_status, pdf_list_dropdown]
        )
        clear_button.click(
            clear_all_data, 
            inputs=[], 
            outputs=[processing_status, pdf_list_dropdown]
        )
        
        app.load(get_pdf_list, outputs=pdf_list_dropdown)

    return app

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    gradio_app = setup_gradio_ui()
    gradio_app.launch(share=True, debug=True)
