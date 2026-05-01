"""NeuroPilot AI — FastAPI backend with WebSocket, JWT auth, CORS, and real-time updates."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import config
from agent.brain import brain_system
from security.biometrics import security_system
from security.auth_middleware import AuthManager, get_current_user
from security.continuous_auth import ContinuousAuthenticator

logger = logging.getLogger(__name__)


# ── Startup / Shutdown ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize security systems on startup."""
    warnings = config.validate()
    for w in warnings:
        logger.warning(w)

    app.state.auth_manager = AuthManager(
        secret=config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
        expiry_minutes=config.JWT_EXPIRY_MINUTES,
        max_attempts=config.MAX_AUTH_ATTEMPTS,
        lockout_seconds=config.AUTH_LOCKOUT_SECONDS,
    )
    app.state.continuous_auth = ContinuousAuthenticator(
        threshold=config.CONTINUOUS_AUTH_THRESHOLD
    )
    logger.info("NeuroPilot AI backend started")
    yield
    logger.info("NeuroPilot AI backend shutting down")


app = FastAPI(
    title="NeuroPilot AI API",
    version="2.0.0",
    description="Autonomous computer-use agent with zero-trust security",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────
class TaskRequest(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=500,
                             description="Task instruction for the agent")

class AuthFaceRequest(BaseModel):
    image_path: str = Field(default="data/screenshots/latest.png")

class ActivityEvent(BaseModel):
    activity_type: str = Field(..., pattern="^(keystroke|mouse_move)$")
    data: dict = Field(default_factory=dict)


# ── Public endpoints ──────────────────────────────────────
@app.get("/")
def read_root():
    return {"status": "NeuroPilot AI is running", "version": "2.0.0"}


@app.post("/auth/face")
def auth_face(req: AuthFaceRequest, request: Request):
    """Authenticate via face biometrics — returns JWT on success."""
    client_ip = request.client.host if request.client else "unknown"
    auth_mgr: AuthManager = request.app.state.auth_manager
    auth_mgr.check_rate_limit(client_ip)

    result = security_system.verify_face(req.image_path)
    if result["authenticated"]:
        auth_mgr.clear_failed_attempts(client_ip)
        token = auth_mgr.create_token(
            user_id=result["user_id"],
            auth_methods=["face"],
            risk_level="low" if result["confidence"] > 0.8 else "medium",
        )
        return {"status": "Authenticated", "token": token, "risk_level": "low"}

    auth_mgr.record_failed_attempt(client_ip)
    raise HTTPException(401, "Face authentication failed")


@app.post("/auth/multi")
def auth_multi(request: Request):
    """Multi-factor authentication (face + voice + device integrity)."""
    client_ip = request.client.host if request.client else "unknown"
    auth_mgr: AuthManager = request.app.state.auth_manager
    auth_mgr.check_rate_limit(client_ip)

    result = security_system.multi_factor_auth(
        face_image=str(config.SCREENSHOTS_DIR / "latest.png")
    )
    if result["overall_authenticated"]:
        auth_mgr.clear_failed_attempts(client_ip)
        methods = [k for k, v in result["factors"].items()
                   if isinstance(v, dict) and v.get("authenticated")]
        token = auth_mgr.create_token(
            user_id="primary_user",
            auth_methods=methods,
            risk_level=result["risk_level"],
        )
        return {"status": "Authenticated", "token": token, **result}

    auth_mgr.record_failed_attempt(client_ip)
    raise HTTPException(401, detail="Multi-factor auth failed")


# ── Protected endpoints (require JWT) ─────────────────────
@app.post("/execute")
def execute_task(req: TaskRequest, background_tasks: BackgroundTasks,
                 user: dict = Depends(get_current_user)):
    if brain_system.is_running:
        raise HTTPException(409, "Agent is busy — stop current task first")
    background_tasks.add_task(brain_system.start_task, req.instruction)
    return {"status": "Started", "task": req.instruction, "user": user["sub"]}


@app.post("/stop")
def stop_task(user: dict = Depends(get_current_user)):
    brain_system.stop_task()
    return {"status": "Stopped"}


@app.get("/status")
def get_status():
    """Public status endpoint — no auth required for dashboard polling."""
    return {
        "is_running": brain_system.is_running,
        "current_task": brain_system.current_task,
    }


# ── Continuous auth ───────────────────────────────────────
@app.post("/auth/activity")
def record_activity(event: ActivityEvent,
                    user: dict = Depends(get_current_user)):
    """Record user behavior for continuous authentication."""
    cont_auth: ContinuousAuthenticator = app.state.continuous_auth
    cont_auth.record_activity(user["sub"], event.activity_type, event.data)
    confidence = cont_auth.calculate_confidence(user["sub"])
    return {
        "confidence": round(confidence, 3),
        "risk_score": cont_auth.get_risk_score(user["sub"]),
    }


@app.get("/auth/risk/{user_id}")
def get_risk_score(user_id: str):
    cont_auth: ContinuousAuthenticator = app.state.continuous_auth
    return {"risk_score": cont_auth.get_risk_score(user_id)}


# ── WebSocket for real-time updates ───────────────────────
@app.websocket("/ws/agent")
async def websocket_agent(ws: WebSocket):
    """Real-time agent status stream via WebSocket."""
    await ws.accept()
    brain_system.register_ws(ws)
    logger.info("WebSocket client connected")
    try:
        while True:
            data = await ws.receive_text()  # keep connection alive
            if data == "ping":
                await ws.send_json({"event": "pong"})
    except WebSocketDisconnect:
        brain_system.unregister_ws(ws)
        logger.info("WebSocket client disconnected")


# ── Memory / History ──────────────────────────────────────
@app.get("/history")
def get_history(limit: int = 50, user: dict = Depends(get_current_user)):
    from agent.memory import memory_system
    return {"history": memory_system.get_history(limit)}
