import streamlit as st
from fpdf import FPDF
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from io import BytesIO
import tempfile

def get_message_content(message):
    """Safely extract content from various message formats."""
    if isinstance(message, (HumanMessage, AIMessage)):
        return message.content
    elif isinstance(message, dict):
        return message.get('content', message.get('text', ''))
    elif isinstance(message, str):
        return message
    elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], dict):
        return message[0].get('text', '')
    else:
        return str(message)

@tool
def save_last_bot_response():
    """Save the last bot response and displayed image to a PDF file and provide a download link."""
    if not st.session_state.message_history.messages:
        return "No messages in history to save."

    # Retrieve the last AI message
    last_message = None
    for msg in reversed(st.session_state.message_history.messages):
        if isinstance(msg, AIMessage):
            last_message = get_message_content(msg)
            break

    if not last_message:
        return "No AI messages in history to save."

    # Ensure last_message is a string
    if isinstance(last_message, list):
        last_message = ' '.join(map(str, last_message))
    else:
        last_message = str(last_message)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, last_message.encode('latin-1', 'replace').decode('latin-1'))

    # Check if an image is displayed and add it to the PDF
    if 'displayed_image' in st.session_state:
        image = st.session_state.displayed_image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_image_file:
            image.save(tmp_image_file.name)
            pdf.image(tmp_image_file.name, x=10, y=pdf.get_y() + 10, w=100)

    # Save PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file_path = tmp_file.name

    # Read the PDF file into memory
    with open(tmp_file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    # Provide download link
    st.download_button(label="Download PDF", data=pdf_data, file_name="yourpdf.pdf", mime="application/pdf")

    return "PDF generated. Click the button to download."

# Example usage in a Streamlit app
if __name__ == "__main__":
    st.title("Chat History PDF Saver")
    if st.button("Save Last Bot Response"):
        save_last_bot_response()