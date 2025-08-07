from fastapi import FastAPI, UploadFile, File, Form, Request, Header, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import requests

from embedder import get_pdf_text
from query_handler import format_prompt, ask_llm
from sentence_transformers import SentenceTransformer
from vector_store import embed_and_upsert, search

app = FastAPI(
    title="HackRx Document QA API",
    version="1.0.0",
    description="Answer questions from PDF documents using RAG-based approach."
)

# CORS for Swagger UI and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme for Swagger UI "Authorize" button
bearer_scheme = HTTPBearer()

model = SentenceTransformer("all-MiniLM-L6-v2")

# Root check
@app.get("/")
def root():
    return {"message": "PDF Query Bot with GPT-4 + Pinecone is running!"}

# Original upload + query route
@app.post("/process/")
async def process_file(query: str = Form(...), file: UploadFile = File(...)):
    try:
        file_data = await file.read()
        text = get_pdf_text(file_data)
        embed_and_upsert(text, model)
        query_vector = model.encode(query).tolist()
        relevant_chunks = search(query_vector, top_k=5)
        prompt = format_prompt(query, relevant_chunks)
        response = ask_llm(prompt)
        return {
            "query": query,
            "answer": response,
            "relevant_clauses": relevant_chunks
        }
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# ✅ HackRx API Route
# -------------------------
class HackRxInput(BaseModel):
    documents: str
    questions: List[str]

class HackRxOutput(BaseModel):
    answers: List[str]

@app.post("/api/v1/hackrx/run", response_model=HackRxOutput)
async def hackrx_handler(
    payload: HackRxInput,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    expected_token = "f5c145545a0ff24b475d29eecc69cccc524203c5e724eb3538d6a4df3e5a5f49"
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Step 1: Download PDF from URL
        pdf_response = requests.get(payload.documents)
        if pdf_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download PDF")

        text = get_pdf_text(pdf_response.content)

        # Step 2: Embed and store vectors
        embed_and_upsert(text, model)

        # Step 3: Answer each question
        answers = []
        for question in payload.questions:
            query_vector = model.encode(question).tolist()
            relevant_chunks = search(query_vector, top_k=5)
            prompt = format_prompt(question, relevant_chunks)
            answer = ask_llm(prompt)
            answers.append(answer)

        return {"answers": answers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
