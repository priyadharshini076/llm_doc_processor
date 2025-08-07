from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import io

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_embeddings(chunks):
    return model.encode(chunks).tolist()
