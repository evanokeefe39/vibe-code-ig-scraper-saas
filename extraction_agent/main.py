from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from pydantic import create_model
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from fastapi import FastAPI, HTTPException, Header, Depends
import os
import uuid
import logging
from dotenv import load_dotenv
from enum import Enum

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== Env + API key ==================
if not os.getenv("OPENROUTER_API_KEY"):
    raise RuntimeError("OPENROUTER_API_KEY required")

API_KEY = os.getenv("EXTRACTION_AGENT_API_KEY")

def require_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API key")

# ================== Schema ==================
class FieldType(str, Enum):
    INT = "int"; STR = "str"; FLOAT = "float"; BOOL = "bool"
    LIST_INT = "list[int]"; LIST_STR = "list[str]"
    LIST_FLOAT = "list[float]"; LIST_BOOL = "list[bool]"

TYPE_MAP = {
    FieldType.INT: int, FieldType.STR: str, FieldType.FLOAT: float, FieldType.BOOL: bool,
    FieldType.LIST_INT: (list[int]), FieldType.LIST_STR: (list[str]),
    FieldType.LIST_FLOAT: (list[float]), FieldType.LIST_BOOL: (list[bool]),
}

class ModelField(BaseModel):
    name: str
    type: FieldType
    description: str | None = None

def create_dynamic_model(fields: List[ModelField]):
    return create_model("Row", **{
        f.name: (TYPE_MAP[f.type], Field(default=None, description=f.description))
        for f in fields
    })

# ================== LLM ==================
model = OpenAIChatModel(
    os.getenv("OPENAI_MODEL_NAME", "x-ai/grok-code-fast-1"),
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
)

schema_agent = Agent(
    model=model,
    output_type=list[ModelField],
    system_prompt="Convert user requirements into a list of ModelField objects. Return only valid JSON."
)

# ================== Sessions ==================
sessions: Dict[str, Dict[str, Any]] = {}

# ================== FastAPI ==================
app = FastAPI(title="Extraction → EAV (auto entity_id)", version="4.0")

class CreateSessionRequest(BaseModel):
    user_id: int
    run_id: int
    requirements: str

class CreateSessionResponse(BaseModel):
    session_id: str

class ExtractRequest(BaseModel):
    session_id: str
    user_id: int
    run_id: int
    text: str

# Auto-generates entity_id per extracted object (not per video)
def to_eav(items: List[BaseModel], user_id: str, run_id: str) -> List[dict]:
    rows = []
    for item in items:
        entity_id = str(uuid.uuid4())  # ← one UUID per real-world entity
        for field, value in item.__dict__.items():
            if value is not None:
                rows.append({
                    "user_id": user_id,
                    "run_id": run_id,
                    "entity_id": entity_id,
                    "attribute": field,
                    "value": value
                })
    return rows

@app.post("/sessions", response_model=CreateSessionResponse, dependencies=[Depends(require_key)])
async def create_session(p: CreateSessionRequest):
    sid = str(uuid.uuid4())
    schema = await schema_agent.run(p.requirements)
    Model = create_dynamic_model(schema.output)

    agent = Agent(
        model=model,
        output_type=list[Model],
        system_prompt="Extract ALL entities from the text according to the exact schema. Return a list of rows. Never hallucinate fields."
    )

    sessions[sid] = {
        "user_id": p.user_id,
        "run_id": p.run_id,
        "agent": agent
    }
    logger.info(f"Session {sid} created for: {p.user_id=} {p.run_id=} — {len(schema.output)} fields")

    logger.info(f"{sessions=}")
    return CreateSessionResponse(session_id=sid)

@app.post("/sessions/extract", dependencies=[Depends(require_key)])
async def extract( p: ExtractRequest):
    logger.info(f"{sessions=}")
    logger.info(f"{p.session_id=} typeof: {type(p.session_id)}")
    logger.info(f"retrieving session: {p.session_id} from sessions: {sessions}")
    s = sessions.get(p.session_id)
    logger.info(f"session info: {s}")

    if not s:
        raise HTTPException(404, "Session not found")
    if s["user_id"] != p.user_id or s["run_id"] != p.run_id:
        raise HTTPException(403, "Forbidden")
    
    result = await s["agent"].run(p.text)
    eav = to_eav(result.output, p.user_id, p.run_id)

    return {"eav_rows": eav}   # ← pure EAV list for n8n bulk insert

@app.get("/")
async def root():
    return {"service": "Extraction → EAV", "active_sessions": len(sessions)}