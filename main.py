import os
from typing import AsyncIterator

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Claude Chat API")
client = anthropic.Anthropic()

MODEL = "claude-opus-4-8"


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class ChatResponse(BaseModel):
    response: str
    history: list[Message]


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages = [m.model_dump() for m in request.history]
    messages.append({"role": "user", "content": request.message})

    with client.messages.stream(
        model=MODEL,
        max_tokens=8096,
        thinking={"type": "adaptive"},
        messages=messages,
    ) as stream:
        final = stream.get_final_message()

    # Extract text from the response (skip thinking blocks)
    response_text = next(
        (block.text for block in final.content if block.type == "text"),
        "",
    )

    updated_history = [Message(**m) for m in messages]
    updated_history.append(Message(role="assistant", content=response_text))

    return ChatResponse(response=response_text, history=updated_history)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    messages = [m.model_dump() for m in request.history]
    messages.append({"role": "user", "content": request.message})

    async def event_generator() -> AsyncIterator[str]:
        with client.messages.stream(
            model=MODEL,
            max_tokens=8096,
            thinking={"type": "adaptive"},
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
