# Claude Chat API

A FastAPI server for multi-turn conversations with the Claude API.

## Setup

1. **Clone and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your API key**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

## Endpoints

### `GET /health`
Returns server status.

### `POST /chat`
Send a message and receive a complete response. Then pass the returned `history` in subsequent requests to maintain conversation context.

**Request:**
```json
{
  "message": "What is the capital of France?",
  "history": []
}
```

**Response:**
```json
{
  "response": "The capital of France is Paris.",
  "history": [
    { "role": "user", "content": "What is the capital of France?" },
    { "role": "assistant", "content": "The capital of France is Paris." }
  ]
}
```

### `POST /chat/stream`
Same as `/chat` but streams the response as Server-Sent Events (SSE). Each event contains a text chunk, ending with `data: [DONE]`.

**Example with curl:**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a short story", "history": []}' \
  --no-buffer
```

## Multi-turn Conversation

The API is stateless — pass the `history` array from the previous response back into the next request:

```bash
# First turn
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My name is Diego", "history": []}'

# Second turn — include history from the first response
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my name?", "history": [...]}'
```

## Interactive Docs

FastAPI provides built-in API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
