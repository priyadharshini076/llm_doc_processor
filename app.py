from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
import openai
from embedder import get_pdf_text
from query_handler import format_prompt, ask_llm
from sentence_transformers import SentenceTransformer
from vector_store import embed_and_upsert, search
import json
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Webhook configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret")

# FastAPI setup
app = FastAPI(
    title="HackRx Document QA API",
    version="1.0.0",
    description="Answer questions from PDF documents using RAG-based approach."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bearer token security
bearer_scheme = HTTPBearer()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Webhook utility functions
async def send_webhook(event_type: str, data: Dict[str, Any], webhook_url: Optional[str] = None):
    """
    Send webhook notification to configured URL
    """
    if not webhook_url and not WEBHOOK_URL:
        return
    
    target_url = webhook_url or WEBHOOK_URL
    
    payload = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Secret": WEBHOOK_SECRET,
        "User-Agent": "LLM-Doc-Processor/1.0"
    }
    
    try:
        response = requests.post(
            target_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return False

# Webhook configuration models
class WebhookConfig(BaseModel):
    url: str
    events: List[str] = ["document_processed", "query_answered", "error"]
    secret: Optional[str] = None

class WebhookEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]

# ---------------------
# ✅ Root Route
# ---------------------
@app.get("/")
def root():
    return {"message": "PDF Query Bot with OpenAI + Pinecone is running!"}

# ---------------------
# ✅ Webhook Configuration Endpoints
# ---------------------
@app.post("/webhook/configure")
async def configure_webhook(config: WebhookConfig):
    """
    Configure webhook URL and events to listen for
    """
    global WEBHOOK_URL, WEBHOOK_SECRET
    
    WEBHOOK_URL = config.url
    if config.secret:
        WEBHOOK_SECRET = config.secret
    
    # Test webhook
    test_success = await send_webhook("webhook_configured", {
        "url": config.url,
        "events": config.events
    })
    
    return {
        "status": "configured",
        "webhook_url": config.url,
        "events": config.events,
        "test_success": test_success
    }

@app.get("/webhook/status")
async def get_webhook_status():
    """
    Get current webhook configuration
    """
    return {
        "webhook_url": WEBHOOK_URL,
        "webhook_secret": WEBHOOK_SECRET[:10] + "..." if WEBHOOK_SECRET else None,
        "configured": bool(WEBHOOK_URL)
    }

@app.delete("/webhook/disable")
async def disable_webhook():
    """
    Disable webhook notifications
    """
    global WEBHOOK_URL
    WEBHOOK_URL = None
    return {"status": "webhook_disabled"}

# ---------------------
# ✅ Upload + Query Route with Webhook
# ---------------------
@app.post("/process/")
async def process_file(query: str = Form(...), file: UploadFile = File(...)):
    try:
        file_data = await file.read()
        text = get_pdf_text(file_data)

        # Embed and store vectors
        embed_and_upsert(text, model)

        # Query handling
        query_vector = model.encode(query).tolist()
        relevant_chunks = search(query_vector, top_k=5)
        prompt = format_prompt(query, relevant_chunks)
        response = ask_llm(prompt)

        result = {
            "query": query,
            "answer": response,
            "relevant_clauses": relevant_chunks,
            "file_name": file.filename,
            "file_size": len(file_data)
        }

        # Send webhook notification
        await send_webhook("document_processed", {
            "file_name": file.filename,
            "file_size": len(file_data),
            "query": query,
            "answer": response
        })

        return result
    except Exception as e:
        error_data = {
            "error": str(e),
            "file_name": file.filename if 'file' in locals() else "unknown"
        }
        
        # Send error webhook
        await send_webhook("error", error_data)
        
        return {"error": str(e)}

# ---------------------
# ✅ HackRx API (PDF URL + Questions) with Webhook
# ---------------------
class HackRxInput(BaseModel):
    documents: str
    questions: List[str]
    webhook_url: Optional[str] = None

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
        for i, question in enumerate(payload.questions):
            query_vector = model.encode(question).tolist()
            relevant_chunks = search(query_vector, top_k=5)
            prompt = format_prompt(question, relevant_chunks)
            answer = ask_llm(prompt)
            answers.append(answer)
            
            # Send webhook for each question answered
            await send_webhook("query_answered", {
                "question_index": i,
                "question": question,
                "answer": answer,
                "document_url": payload.documents
            }, payload.webhook_url)

        # Send completion webhook
        await send_webhook("document_processed", {
            "document_url": payload.documents,
            "questions_count": len(payload.questions),
            "answers": answers
        }, payload.webhook_url)

        return {"answers": answers}

    except Exception as e:
        error_data = {
            "error": str(e),
            "document_url": payload.documents,
            "questions": payload.questions
        }
        
        # Send error webhook
        await send_webhook("error", error_data, payload.webhook_url)
        
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------
# ✅ Manual Webhook Trigger
# ---------------------
@app.post("/webhook/trigger")
async def trigger_webhook(event: WebhookEvent, webhook_url: Optional[str] = None):
    """
    Manually trigger a webhook event
    """
    success = await send_webhook(event.event_type, event.data, webhook_url)
    return {
        "event_type": event.event_type,
        "sent": success,
        "webhook_url": webhook_url or WEBHOOK_URL
    }
