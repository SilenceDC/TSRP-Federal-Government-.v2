"""Website API with anonymous public access and live Discord role checks."""
from __future__ import annotations

import os
import secrets
from collections import defaultdict, deque
from time import monotonic, time
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from itsdangerous import BadSignature, URLSafeTimedSerializer

from tsrp_ai.answer import answer_question

app = FastAPI(title="TSRP AI API", version="0.2.0")
origins = [x.strip() for x in os.getenv("WEB_ALLOWED_ORIGINS", "").split(",") if x.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

# Access tokens stay server-side. The browser receives only a signed opaque session ID.
SESSION_SECRET = os.getenv("SESSION_SECRET", "").strip()
serializer = URLSafeTimedSerializer(SESSION_SECRET) if SESSION_SECRET else None
_sessions: dict[str, dict] = {}
_oauth_states: dict[str, float] = {}
_requests: dict[str, deque[float]] = defaultdict(deque)


class AskBody(BaseModel):
    question: str = Field(min_length=1, max_length=1500)


def _oauth_config() -> tuple[str, str, str, str]:
    values = (
        os.getenv("DISCORD_CLIENT_ID", "").strip(),
        os.getenv("DISCORD_CLIENT_SECRET", "").strip(),
        os.getenv("DISCORD_GUILD_ID", "").strip(),
        os.getenv("DISCORD_REDIRECT_URI", "").strip(),
    )
    if not all(values) or not SESSION_SECRET or serializer is None:
        raise HTTPException(status_code=503, detail="Discord website login is not configured.")
    return values


def _session(request: Request) -> dict | None:
    if serializer is None:
        return None
    signed_id = request.cookies.get("tsrp_ai_session")
    if not signed_id:
        return None
    try:
        session_id = serializer.loads(signed_id, max_age=604800)
    except (BadSignature, TypeError):
        return None
    data = _sessions.get(session_id)
    if not data or data.get("expires_at", 0) <= time():
        _sessions.pop(session_id, None)
        return None
    return data


async def _discord_member(access_token: str, guild_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"https://discord.com/api/v10/users/@me/guilds/{guild_id}/member",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if response.status_code in (401, 403, 404):
        raise HTTPException(status_code=401, detail="Discord session expired or server membership could not be verified. Log in again.")
    response.raise_for_status()
    return response.json()


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "TSRP AI", "version": "0.2.0"}


@app.get("/auth/discord")
async def discord_login():
    client_id, _, _, redirect_uri = _oauth_config()
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = time() + 600
    # Prune expired one-time states.
    for key, expiry in list(_oauth_states.items()):
        if expiry <= time():
            _oauth_states.pop(key, None)
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "identify guilds.members.read",
        "state": state,
        "prompt": "consent",
    }
    return RedirectResponse("https://discord.com/oauth2/authorize?" + urlencode(params))


@app.get("/auth/discord/callback")
async def discord_callback(request: Request, code: str, state: str):
    client_id, client_secret, guild_id, redirect_uri = _oauth_config()
    expiry = _oauth_states.pop(state, None)
    if not expiry or expiry <= time():
        raise HTTPException(status_code=400, detail="Invalid or expired login state. Please try logging in again.")

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://discord.com/api/v10/oauth2/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_response.is_error:
            raise HTTPException(status_code=401, detail="Discord authorization failed. Please try again.")
        token_data = token_response.json()
        access_token = token_data.get("access_token", "")
        if not access_token:
            raise HTTPException(status_code=401, detail="Discord did not return an access token.")
        member_response = await client.get(
            f"https://discord.com/api/v10/users/@me/guilds/{guild_id}/member",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if member_response.status_code in (401, 403, 404):
            raise HTTPException(status_code=403, detail="You must be a member of the TSRP Discord server to use role-based website access.")
        member_response.raise_for_status()
        member = member_response.json()
        user_response = await client.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_response.raise_for_status()
        user = user_response.json()

    for old_id, old_session in list(_sessions.items()):
        if old_session.get("expires_at", 0) <= time():
            _sessions.pop(old_id, None)
    session_id = secrets.token_urlsafe(32)
    expires_in = max(60, int(token_data.get("expires_in", 604800)))
    _sessions[session_id] = {
        "access_token": access_token,
        "user_id": str(user.get("id", "")),
        "username": user.get("global_name") or user.get("username", "Discord member"),
        "guild_id": guild_id,
        "expires_at": time() + expires_in,
    }
    response = RedirectResponse(os.getenv("WEB_POST_LOGIN_URL", "/"), status_code=303)
    response.set_cookie(
        "tsrp_ai_session",
        serializer.dumps(session_id),
        max_age=min(expires_in, 604800),
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return response


@app.get("/api/me")
async def who_am_i(request: Request):
    session = _session(request)
    if not session:
        return {"authenticated": False, "divisions": []}
    _, _, guild_id, _ = _oauth_config()
    member = await _discord_member(session["access_token"], guild_id)
    return {
        "authenticated": True,
        "username": session["username"],
    }


@app.post("/auth/logout")
async def logout(request: Request):
    signed_id = request.cookies.get("tsrp_ai_session")
    if serializer and signed_id:
        try:
            session_id = serializer.loads(signed_id, max_age=604800)
            _sessions.pop(session_id, None)
        except (BadSignature, TypeError):
            pass
    response = JSONResponse({"ok": True})
    response.delete_cookie("tsrp_ai_session", path="/", secure=True, httponly=True, samesite="none")
    return response


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

    session = _session(request)
    if session:
        _, _, guild_id, _ = _oauth_config()
        # Re-check Discord membership and roles on every request; never trust browser-supplied roles.
        member = await _discord_member(session["access_token"], guild_id)
        role_ids = {str(role_id) for role_id in member.get("roles", [])}
        result = await answer_question(body.question, requester_role_ids=role_ids, public_only=False)
        return {"answer": result, "authenticated": True}

    # Anonymous visitors can retrieve public documents only.
    result = await answer_question(body.question, requester_role_ids=set(), public_only=True)
    return {"answer": result, "authenticated": False}
