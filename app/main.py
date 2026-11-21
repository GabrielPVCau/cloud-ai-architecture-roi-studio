"""FastAPI server for Cloud & AI Architecture, FinOps & ROI Pre-Sales Studio."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.calculator import SimulationInput, run_finops_simulation
from app.catalog import CLOUD_PROVIDERS, LLM_MODELS, USE_CASES
from app.proposal_gen import generate_executive_proposal, generate_mermaid_architecture


STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"

app = FastAPI(
    title="Cloud & AI Architecture, FinOps & ROI Pre-Sales Studio",
    version="1.0.0",
    description="Interactive multicloud (AWS/Azure/GCP) FinOps, TCO, Payback, Mermaid Architecture, and Pre-Sales Proposal simulator.",
)


class SimulateRequest(BaseModel):
    use_case_id: str = Field(default="rag_support")
    cloud_id: str = Field(default="aws")
    model_id: str = Field(default="gemini-flash")
    monthly_requests: int = Field(default=25000, ge=500, le=5_000_000)
    hourly_team_cost_brl: float = Field(default=65.0, ge=15.0, le=1000.0)
    implementation_cost_brl: float = Field(default=45000.0, ge=5000.0, le=2_000_000.0)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return STATIC_INDEX.read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "clouds": list(CLOUD_PROVIDERS), "models": list(LLM_MODELS)}


@app.get("/api/catalog")
def catalog() -> dict:
    return {
        "clouds": {k: asdict(v) for k, v in CLOUD_PROVIDERS.items()},
        "models": {k: asdict(v) for k, v in LLM_MODELS.items()},
        "use_cases": USE_CASES,
    }


@app.post("/api/simulate")
def simulate(req: SimulateRequest) -> dict:
    try:
        inp = SimulationInput(**req.model_dump())
        res = run_finops_simulation(inp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Also compare all 3 clouds side-by-side for Multicloud FinOps decision
    multicloud_comparison = []
    for cid in CLOUD_PROVIDERS:
        alt = run_finops_simulation(
            SimulationInput(
                use_case_id=inp.use_case_id,
                cloud_id=cid,
                model_id=inp.model_id,
                monthly_requests=inp.monthly_requests,
                hourly_team_cost_brl=inp.hourly_team_cost_brl,
                implementation_cost_brl=inp.implementation_cost_brl,
            )
        )
        multicloud_comparison.append(
            {
                "cloud_id": cid,
                "cloud_name": alt.cloud_name,
                "monthly_total_usd": alt.monthly_total_usd,
                "tco_12m_brl": alt.tco_12m_brl,
                "roi_12m_pct": alt.roi_12m_pct,
            }
        )

    return {
        "finops": asdict(res),
        "multicloud_comparison": multicloud_comparison,
        "mermaid_architecture": generate_mermaid_architecture(inp),
        "executive_proposal": generate_executive_proposal(inp, res),
    }
