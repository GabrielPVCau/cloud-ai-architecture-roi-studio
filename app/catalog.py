"""Reference pricing catalog for Multicloud (AWS, Azure, GCP) and Enterprise LLMs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CloudProviderSpec:
    id: str
    name: str
    compute_service: str
    ai_service: str
    db_service: str
    monthly_base_infra_usd: float
    egress_multiplier: float


@dataclass(frozen=True)
class LLMModelSpec:
    id: str
    name: str
    deployment: str  # managed | self_hosted
    input_per_1m_usd: float
    output_per_1m_usd: float
    avg_latency_ms: int


CLOUD_PROVIDERS: dict[str, CloudProviderSpec] = {
    "aws": CloudProviderSpec(
        id="aws",
        name="Amazon Web Services (AWS)",
        compute_service="ECS Fargate / Lambda",
        ai_service="AWS Bedrock",
        db_service="Amazon RDS PostgreSQL + pgvector",
        monthly_base_infra_usd=290.0,
        egress_multiplier=1.05,
    ),
    "azure": CloudProviderSpec(
        id="azure",
        name="Microsoft Azure",
        compute_service="Azure Container Apps",
        ai_service="Azure AI Foundry / OpenAI",
        db_service="Azure Database for PostgreSQL",
        monthly_base_infra_usd=310.0,
        egress_multiplier=1.03,
    ),
    "gcp": CloudProviderSpec(
        id="gcp",
        name="Google Cloud Platform (GCP)",
        compute_service="Cloud Run",
        ai_service="Vertex AI (Gemini)",
        db_service="Cloud SQL PostgreSQL",
        monthly_base_infra_usd=265.0,
        egress_multiplier=1.00,
    ),
}

LLM_MODELS: dict[str, LLMModelSpec] = {
    "gemini-flash": LLMModelSpec(
        id="gemini-flash",
        name="Gemini 2.5 Flash (Managed)",
        deployment="managed",
        input_per_1m_usd=0.15,
        output_per_1m_usd=0.60,
        avg_latency_ms=420,
    ),
    "gpt-4o-mini": LLMModelSpec(
        id="gpt-4o-mini",
        name="GPT-4o mini (Managed)",
        deployment="managed",
        input_per_1m_usd=0.15,
        output_per_1m_usd=0.60,
        avg_latency_ms=510,
    ),
    "claude-sonnet": LLMModelSpec(
        id="claude-sonnet",
        name="Claude Sonnet (Managed High-Reasoning)",
        deployment="managed",
        input_per_1m_usd=3.00,
        output_per_1m_usd=15.00,
        avg_latency_ms=1150,
    ),
    "llama-self-hosted": LLMModelSpec(
        id="llama-self-hosted",
        name="Llama 3.3 70B (Self-Hosted GPU)",
        deployment="self_hosted",
        input_per_1m_usd=0.0,
        output_per_1m_usd=0.0,
        avg_latency_ms=680,
    ),
}

USE_CASES: dict[str, dict] = {
    "rag_support": {
        "name": "Copiloto RAG + Atendimento B2B",
        "avg_input_tokens": 1800,
        "avg_output_tokens": 450,
        "automation_rate": 0.65,
        "minutes_saved_per_request": 6.0,
        "implementation_weeks": 4,
    },
    "doc_triage": {
        "name": "Triagem & Extração Documental com LGPD",
        "avg_input_tokens": 3200,
        "avg_output_tokens": 600,
        "automation_rate": 0.72,
        "minutes_saved_per_request": 9.0,
        "implementation_weeks": 5,
    },
    "sales_rfp": {
        "name": "Acelerador de Propostas & RFPs Comerciais",
        "avg_input_tokens": 4500,
        "avg_output_tokens": 1200,
        "automation_rate": 0.55,
        "minutes_saved_per_request": 25.0,
        "implementation_weeks": 6,
    },
}
