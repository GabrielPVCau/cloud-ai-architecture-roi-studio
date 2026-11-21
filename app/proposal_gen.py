"""Generates Mermaid reference architecture diagrams and Pre-Sales Executive Proposals."""

from __future__ import annotations

from app.calculator import SimulationInput, SimulationResult
from app.catalog import CLOUD_PROVIDERS, LLM_MODELS, USE_CASES


def generate_mermaid_architecture(inp: SimulationInput) -> str:
    cloud = CLOUD_PROVIDERS[inp.cloud_id]
    model = LLM_MODELS[inp.model_id]
    uc = USE_CASES[inp.use_case_id]
    return "\n".join(
        [
            "flowchart LR",
            f'    U["Usuários / CRM / ERP"] --> GW["API Gateway + OAuth 2.0 / JWT"]',
            f'    GW --> APP["{cloud.compute_service}<br/>Orquestrador ({uc["name"]})"]',
            '    APP --> LGPD["Camada Guardrails LGPD<br/>PII Masking + Rate Limit"]',
            f'    LGPD --> AI["{cloud.ai_service}<br/>{model.name}"]',
            f'    APP --> DB["{cloud.db_service}<br/>Dados + Embeddings"]',
            '    APP --> OBS["Observabilidade & FinOps<br/>Logs, Latência & Token Budget"]',
        ]
    )


def generate_executive_proposal(inp: SimulationInput, res: SimulationResult) -> dict:
    uc = USE_CASES[inp.use_case_id]
    cloud = CLOUD_PROVIDERS[inp.cloud_id]
    payback_txt = f"{res.payback_months} meses" if res.payback_months is not None else "Inviável neste volume (ajustar escopo)"
    return {
        "titulo": f"Proposta Técnico-Comercial: {res.use_case_name} ({cloud.name})",
        "resumo_executivo": (
            f"Arquitetura em {cloud.name} ({cloud.compute_service} + {cloud.ai_service}) projetada para "
            f"{inp.monthly_requests:,} requisições/mês, gerando economia líquida estimada de "
            f"R$ {res.monthly_net_savings_brl:,.2f}/mês, payback em {payback_txt} e ROI em 12 meses de {res.roi_12m_pct}%."
        ),
        "escopo_macro": [
            f"Semana 1–2: Technical Discovery, mapeamento AS-IS/TO-BE e PoC validada com dados mascarados (LGPD).",
            f"Semana 3–{uc['implementation_weeks']}: Deploy em {cloud.compute_service}, integração via APIs REST/Webhooks, observabilidade e Handover para Delivery.",
        ],
        "riscos_e_mitigacoes": [
            "Risco de vazamento de PII → Mitigação: mascaramento determinístico na borda antes do envio à LLM.",
            "Risco de explosão de custo de tokens → Mitigação: budget alerts, caching semântico e rate limiting por tenant.",
            "Risco de baixa adoção → Mitigação: critérios objetivos de PoC (groundedness >= 90%) e capacitação dos key users.",
        ],
        "premissas": [
            f"Volume base estimado em {inp.monthly_requests:,} requisições/mês com taxa de automação de {int(uc['automation_rate'] * 100)}%.",
            "Disponibilização de credenciais de sandbox/homologação e ponto focal de negócio pelo cliente na Semana 1.",
        ],
    }
