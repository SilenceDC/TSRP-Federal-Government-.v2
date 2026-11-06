"""Public website API. This endpoint deliberately retrieves public documents only."""
from __future__ import annotations

import os
from collections import defaultdict, deque
from time import monotonic

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tsrp_ai.answer import answer_question

app = FastAPI(title="TSRP AI API", version="0.1.0")
origins = [x.strip() for x in os.getenv("WEB_ALLOWED_ORIGINS", "").split(",") if x.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

_requests: dict[str, deque[float]] = defaultdict(deque)


class AskBody(BaseModel):
    question: str = Field(min_length=1, max_length=1500)


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "TSRP AI", "version": "0.1.0"}


@app.post("/api/ask")
async def ask(body: AskBody, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = monotonic()
    bucket = _requests[client_ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= 10:
        raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.")
    bucket.append(now)

    # The public website has no verified Discord identity yet: public documents only.
    result = await answer_question(body.question, requester_role_ids=set(), public_only=True)
    return {"answer": result}
