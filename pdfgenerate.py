import streamlit as st
from fpdf import FPDF
from io import BytesIO
from langchain.tools import tool
from langchain_core.messages import AIMessage

def extract_text(message):
    """Recursively extract text from the message, handling dicts and lists."""
    if isinstance(message, dict):
        # Recursively extract from dictionary, prioritizing 'text' field if available
        return extract_text(message.get('text', ''))
    elif isinstance(message, list):
        # Join list elements after extracting text from each
        return ' '.join([extract_text(item) for item in message])
    elif isinstance(message, str):
        return message
    return str(message)  # Fallback for any non-str message


@tool
def save_last_bot_response():
    """Save the last bot response to a PDF file and provide a download button. Call this tool when user says 'save'"""
    # Access the StreamlitChatMessageHistory from session state
    message_history = st.session_state.get('message_history', None)

    # Check if message_history is available
    if message_history is None:
        st.error("No message history found in session state.")
        return "No message history found."

    # Retrieve the last AI message
    last_message = None
    for msg in reversed(message_history.messages):
        if isinstance(msg, AIMessage):
            last_message = msg.content
            break

    # If no AI message found, use a placeholder message
    if not last_message:
        last_message = "No AI messages in history to save."

    # Use the extract_text function to clean the message content
    last_message_cleaned = extract_text(last_message)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, last_message_cleaned.encode('latin-1', 'replace').decode('latin-1'))

    # Save PDF to a BytesIO object
    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    # Provide download button
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="yourpdf.pdf",
        mime="application/pdf"
    )

    return "PDF generated. Click the download button to save it."