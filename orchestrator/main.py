"""FastAPI entry point for the Financial Research System."""
import logging, sys
from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

from shared.logging_config import configure_logging
from shared.models import ResearchRequest, FinalReport
from orchestrator.pipeline import ResearchPipeline

configure_logging()
logger = structlog.get_logger(__name__)

pipeline: ResearchPipeline = None
_store: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    pipeline = ResearchPipeline()
    logger.info("financial_research_system_starting")
    yield
    logger.info("financial_research_system_stopping")


app = FastAPI(
    title="Financial Research System",
    description="Multi-Agent Financial Research — Project 4, Chapter 20, Prompt to Production by Maneesh Kumar",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "financial-research-system", "version": "1.0.0"}


@app.post("/api/v1/research")
async def start_research(request: ResearchRequest) -> dict:
    """Start a research pipeline. Returns completed report with run_id."""
    try:
        report = await pipeline.run(request)
        result = report.model_dump()
        result["created_at"] = report.created_at.isoformat()
        _store[request.run_id] = result
        return {"run_id": request.run_id, "status": "completed", "report": result}
    except Exception as exc:
        logger.error("research_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/report/{run_id}")
async def get_report(run_id: str) -> dict:
    if run_id not in _store:
        raise HTTPException(status_code=404, detail=f"Report {run_id} not found")
    return _store[run_id]


@app.get("/api/v1/status/{run_id}")
async def get_status(run_id: str) -> dict:
    status = "completed" if run_id in _store else "not_found"
    return {"run_id": run_id, "status": status}
