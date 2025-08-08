# LLM Document Processor with Webhook Support

A FastAPI-based document processing system that uses RAG (Retrieval-Augmented Generation) to answer questions from PDF documents, with comprehensive webhook support for real-time notifications.

## Features

- 📄 PDF document processing and text extraction
- 🔍 Vector-based document search using FAISS
- 🤖 OpenAI-powered question answering
- 🔗 Webhook notifications for real-time updates
- 🔐 Bearer token authentication
- 🌐 CORS support for web applications

## Webhook Events

The system sends webhook notifications for the following events:

### 1. `document_processed`
Triggered when a document is successfully processed and embedded.

**Payload:**
```json
{
  "event_type": "document_processed",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "data": {
    "file_name": "document.pdf",
    "file_size": 1024000,
    "query": "What is the main topic?",
    "answer": "The main topic is..."
  }
}
```

### 2. `query_answered`
Triggered when each question is answered (for batch processing).

**Payload:**
```json
{
  "event_type": "query_answered",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "data": {
    "question_index": 0,
    "question": "What is the main topic?",
    "answer": "The main topic is...",
    "document_url": "https://example.com/document.pdf"
  }
}
```

### 3. `error`
Triggered when an error occurs during processing.

**Payload:**
```json
{
  "event_type": "error",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "data": {
    "error": "Failed to process document",
    "file_name": "document.pdf"
  }
}
```

### 4. `webhook_configured`
Triggered when webhook is successfully configured.

**Payload:**
```json
{
  "event_type": "webhook_configured",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "data": {
    "url": "https://your-webhook-url.com/webhook",
    "events": ["document_processed", "query_answered", "error"]
  }
}
```

## API Endpoints

### Webhook Configuration

#### Configure Webhook
```http
POST /webhook/configure
Content-Type: application/json

{
  "url": "https://your-webhook-url.com/webhook",
  "events": ["document_processed", "query_answered", "error"],
  "secret": "your_webhook_secret"
}
```

#### Get Webhook Status
```http
GET /webhook/status
```

#### Disable Webhook
```http
DELETE /webhook/disable
```

#### Manual Webhook Trigger
```http
POST /webhook/trigger
Content-Type: application/json

{
  "event_type": "custom_event",
  "data": {
    "custom_field": "custom_value"
  }
}
```

### Document Processing

#### Process File with Query
```http
POST /process/
Content-Type: multipart/form-data

file: [PDF file]
query: "What is the main topic?"
```

#### HackRx API (Batch Processing)
```http
POST /api/v1/hackrx/run
Authorization: Bearer f5c145545a0ff24b475d29eecc69cccc524203c5e724eb3538d6a4df3e5a5f49
Content-Type: application/json

{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic?",
    "What are the key findings?"
  ],
  "webhook_url": "https://your-webhook-url.com/webhook"
}
```

## Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
WEBHOOK_URL=https://your-webhook-url.com/webhook
WEBHOOK_SECRET=your_webhook_secret
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Testing Webhooks

### Option 1: Use the Webhook Receiver

1. Start the webhook receiver:
```bash
python webhook_receiver.py
```

2. Configure webhook in your main app:
```bash
curl -X POST http://localhost:8000/webhook/configure \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:8001/webhook",
    "events": ["document_processed", "query_answered", "error"]
  }'
```

3. View received webhooks:
```bash
curl http://localhost:8001/webhooks
```

### Option 2: Use Webhook Testing Services

- **Webhook.site**: https://webhook.site
- **RequestBin**: https://requestbin.com
- **ngrok**: For local development

## Webhook Security

The system includes several security features:

1. **Webhook Secret**: Configure a secret that's sent in the `X-Webhook-Secret` header
2. **Timeout**: 10-second timeout for webhook requests
3. **Error Handling**: Failed webhooks don't affect the main processing
4. **User-Agent**: Identifies the source as "LLM-Doc-Processor/1.0"

## Example Usage

### Python Client Example

```python
import requests

# Configure webhook
webhook_config = {
    "url": "https://your-webhook-url.com/webhook",
    "events": ["document_processed", "query_answered", "error"]
}

response = requests.post(
    "http://localhost:8000/webhook/configure",
    json=webhook_config
)
print(response.json())

# Process document
files = {"file": open("document.pdf", "rb")}
data = {"query": "What is the main topic?"}

response = requests.post(
    "http://localhost:8000/process/",
    files=files,
    data=data
)
print(response.json())
```

### JavaScript Client Example

```javascript
// Configure webhook
const webhookConfig = {
  url: "https://your-webhook-url.com/webhook",
  events: ["document_processed", "query_answered", "error"]
};

fetch("http://localhost:8000/webhook/configure", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(webhookConfig)
})
.then(response => response.json())
.then(data => console.log(data));

// Process document
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("query", "What is the main topic?");

fetch("http://localhost:8000/process/", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Error Handling

Webhook failures are handled gracefully:

- Failed webhooks don't affect document processing
- Errors are logged but don't stop the main flow
- Timeout protection prevents hanging requests
- Retry logic can be easily added if needed

## Monitoring

Monitor webhook delivery by:

1. Checking webhook receiver logs
2. Using webhook testing services
3. Implementing webhook status endpoints
4. Adding retry mechanisms for failed deliveries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
