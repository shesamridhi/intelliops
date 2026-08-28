from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas import AgentQuery, AgentResponse
from app.ai_agent import run_agent

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/query", response_model=AgentResponse)
def query_agent(payload: AgentQuery, db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = run_agent(payload.prompt, db)
    return AgentResponse(**result)
