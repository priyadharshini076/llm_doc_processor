from PyPDF2 import PdfReader
import io

def get_pdf_text(file_bytes):
    """
    Extract text from a PDF (all pages).
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text
