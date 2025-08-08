import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Create FastAPI app
app = FastAPI()

# Example request model
class PromptRequest(BaseModel):
    prompt: str

# Example route
@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=200
        )
        return {"response": response.choices[0].message["content"].strip()}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Health check endpoint
@app.get("/")
async def health():
    return {"status": "ok"}

# This is the critical part for Render to detect your service
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT or fallback for local
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
