from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="Webhook Receiver", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store received webhooks
received_webhooks = []

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receive webhook notifications from the LLM document processor
    """
    body = await request.json()
    
    # Add timestamp
    body["received_at"] = datetime.utcnow().isoformat()
    
    # Store webhook
    received_webhooks.append(body)
    
    print(f"📥 Received webhook: {body['event_type']}")
    print(f"📋 Data: {json.dumps(body, indent=2)}")
    
    return {"status": "received", "event_type": body.get("event_type")}

@app.get("/webhooks")
async def get_webhooks():
    """
    Get all received webhooks
    """
    return {
        "count": len(received_webhooks),
        "webhooks": received_webhooks
    }

@app.delete("/webhooks/clear")
async def clear_webhooks():
    """
    Clear all stored webhooks
    """
    global received_webhooks
    received_webhooks.clear()
    return {"status": "cleared", "count": 0}

@app.get("/")
async def root():
    return {
        "message": "Webhook Receiver is running!",
        "endpoints": {
            "POST /webhook": "Receive webhook notifications",
            "GET /webhooks": "View all received webhooks",
            "DELETE /webhooks/clear": "Clear stored webhooks"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
