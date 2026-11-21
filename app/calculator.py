"""Deterministic FinOps, TCO (12m), Payback, and ROI calculation engine."""

from __future__ import annotations

from dataclasses import dataclass

from app.catalog import CLOUD_PROVIDERS, LLM_MODELS, USE_CASES


USD_TO_BRL = 5.50
SELF_HOSTED_GPU_MONTHLY_USD = 1450.0


@dataclass
class SimulationInput:
    use_case_id: str
    cloud_id: str
    model_id: str
    monthly_requests: int
    hourly_team_cost_brl: float
    implementation_cost_brl: float


@dataclass
class SimulationResult:
    use_case_name: str
    cloud_name: str
    model_name: str
    monthly_infra_usd: float
    monthly_llm_usd: float
    monthly_total_usd: float
    monthly_total_brl: float
    tco_12m_brl: float
    monthly_hours_saved: float
    monthly_gross_savings_brl: float
    monthly_net_savings_brl: float
    payback_months: float | None
    roi_12m_pct: float
    build_vs_managed_note: str


def run_finops_simulation(inp: SimulationInput) -> SimulationResult:
    if inp.use_case_id not in USE_CASES:
        raise ValueError(f"Use case inválido: {inp.use_case_id}")
    if inp.cloud_id not in CLOUD_PROVIDERS:
        raise ValueError(f"Cloud inválida: {inp.cloud_id}")
    if inp.model_id not in LLM_MODELS:
        raise ValueError(f"Modelo inválido: {inp.model_id}")

    uc = USE_CASES[inp.use_case_id]
    cloud = CLOUD_PROVIDERS[inp.cloud_id]
    model = LLM_MODELS[inp.model_id]

    # Scale compute gently with volume
    volume_factor = 1.0 + max(0, (inp.monthly_requests - 20_000) / 100_000) * 0.35
    infra_usd = cloud.monthly_base_infra_usd * volume_factor * cloud.egress_multiplier

    if model.deployment == "self_hosted":
        llm_usd = SELF_HOSTED_GPU_MONTHLY_USD
        build_note = (
            "Self-Hosted GPU só compensa acima de ~150k requisições/mês ou sob exigência regulatória de air-gap; "
            "para PoCs iniciais, modelos gerenciados reduzem o TCO em >60%."
        )
    else:
        total_in = inp.monthly_requests * uc["avg_input_tokens"]
        total_out = inp.monthly_requests * uc["avg_output_tokens"]
        llm_usd = (
            (total_in / 1_000_000) * model.input_per_1m_usd
            + (total_out / 1_000_000) * model.output_per_1m_usd
        )
        build_note = (
            f"Modelo gerenciado ({model.name}) via {cloud.ai_service}: "
            f"custo variável proporcional ao uso, zero overhead de GPU ociosa e time-to-value de {uc['implementation_weeks']} semanas."
        )

    monthly_total_usd = infra_usd + llm_usd
    monthly_total_brl = monthly_total_usd * USD_TO_BRL
    tco_12m_brl = inp.implementation_cost_brl + (monthly_total_brl * 12)

    automated_reqs = inp.monthly_requests * uc["automation_rate"]
    monthly_hours_saved = (automated_reqs * uc["minutes_saved_per_request"]) / 60.0
    monthly_gross_savings_brl = monthly_hours_saved * inp.hourly_team_cost_brl
    monthly_net_savings_brl = monthly_gross_savings_brl - monthly_total_brl

    if monthly_net_savings_brl > 0:
        payback_months: float | None = round(inp.implementation_cost_brl / monthly_net_savings_brl, 1)
    else:
        payback_months = None

    total_12m_benefit = monthly_gross_savings_brl * 12
    roi_12m_pct = round(((total_12m_benefit - tco_12m_brl) / max(tco_12m_brl, 1.0)) * 100, 1)

    return SimulationResult(
        use_case_name=uc["name"],
        cloud_name=cloud.name,
        model_name=model.name,
        monthly_infra_usd=round(infra_usd, 2),
        monthly_llm_usd=round(llm_usd, 2),
        monthly_total_usd=round(monthly_total_usd, 2),
        monthly_total_brl=round(monthly_total_brl, 2),
        tco_12m_brl=round(tco_12m_brl, 2),
        monthly_hours_saved=round(monthly_hours_saved, 1),
        monthly_gross_savings_brl=round(monthly_gross_savings_brl, 2),
        monthly_net_savings_brl=round(monthly_net_savings_brl, 2),
        payback_months=payback_months,
        roi_12m_pct=roi_12m_pct,
        build_vs_managed_note=build_note,
    )
