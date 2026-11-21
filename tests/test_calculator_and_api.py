"""Automated tests for FinOps calculator, Multicloud comparison, Mermaid & API."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_catalog():
    h = client.get("/api/health")
    assert h.status_code == 200
    assert set(h.json()["clouds"]) == {"aws", "azure", "gcp"}

    c = client.get("/api/catalog")
    assert c.status_code == 200
    assert "rag_support" in c.json()["use_cases"]


def test_simulate_managed_aws_positive_roi():
    res = client.post(
        "/api/simulate",
        json={
            "use_case_id": "rag_support",
            "cloud_id": "aws",
            "model_id": "gemini-flash",
            "monthly_requests": 25000,
            "hourly_team_cost_brl": 65.0,
            "implementation_cost_brl": 45000.0,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["finops"]["monthly_net_savings_brl"] > 0
    assert body["finops"]["payback_months"] is not None
    assert body["finops"]["roi_12m_pct"] > 0
    assert len(body["multicloud_comparison"]) == 3
    assert "flowchart LR" in body["mermaid_architecture"]
    assert "AWS Bedrock" in body["mermaid_architecture"]


def test_self_hosted_gpu_higher_monthly_cost_than_managed_at_low_volume():
    managed = client.post(
        "/api/simulate",
        json={"cloud_id": "gcp", "model_id": "gemini-flash", "monthly_requests": 10000},
    ).json()
    self_hosted = client.post(
        "/api/simulate",
        json={"cloud_id": "gcp", "model_id": "llama-self-hosted", "monthly_requests": 10000},
    ).json()
    assert self_hosted["finops"]["monthly_llm_usd"] > managed["finops"]["monthly_llm_usd"]
