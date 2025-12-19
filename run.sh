#!/bin/bash
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run FastAPI app (Bot runs inside via Webhook)
uvicorn bot.main:app --reload --port 8000
