# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file FastAPI server (`main.py`) that wraps the Anthropic API to provide a multi-turn chat REST API. The API is stateless — conversation history is passed by the client on each request.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (auto-reload on file changes)
uvicorn main:app --reload

# Run against a specific port
uvicorn main:app --reload --port 8001
```

There is no test suite configured. Interactive docs are available at `http://localhost:8000/docs` when the server is running.

## Architecture

Everything lives in `main.py`. Key decisions:

- **Model**: `claude-opus-4-8` with `thinking={"type": "adaptive"}` and `max_tokens=8096`
- **Stateless history**: Clients pass the full `history: list[Message]` in each request and receive an updated list back; no server-side session storage
- **Streaming vs. non-streaming**: `/chat` uses `client.messages.stream()` internally but collects the final message before returning; `/chat/stream` yields SSE chunks using `StreamingResponse` with an async generator
- **Thinking blocks**: The `/chat` endpoint skips `thinking`-type blocks when extracting the assistant's text response, taking only the first `text`-type content block

## Environment

Requires `ANTHROPIC_API_KEY` in a `.env` file (see `.env.example`). The key is loaded via `python-dotenv` at startup.
