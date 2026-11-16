from tests.conftest import GENUINE, SCAM


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["llm_available"] is False


def test_check_scam_is_high_risk_with_exact_phrases(client):
    res = client.post("/check", json={"text": SCAM, "source": "web"})
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"] == "high_risk" and body["verdict_label"] == "High risk"
    payment = next(r for r in body["rules"] if r["id"] == "payment_request")
    span = payment["matches"][0]
    assert SCAM[span["start"] : span["end"]] == span["text"]
    assert len(body["checklist"]) == 5 and body["llm_used"] is False
    assert 0 <= body["score"] <= 1 and body["top_terms"]


def test_check_genuine_never_says_safe(client):
    body = client.post("/check", json={"text": GENUINE}).json()
    assert body["verdict"] == "consistent"
    assert body["verdict_label"] == "Looks consistent with genuine postings"
    assert "safe" not in body["explanation"].lower()
    assert any(item["id"] == "report" for item in body["checklist"])


def test_short_message_is_marked_less_reliable(client):
    body = client.post(
        "/check", json={"text": "Hi, join our team. Interview on Monday at 11."}
    ).json()
    assert body["model_reliable"] is False and body["model_note"]


def test_optional_email_and_url_are_checked(client):
    body = client.post(
        "/check",
        json={
            "text": "We are pleased to offer you the trainee role.",
            "email": "hr@gmail.com",
            "url": "bit.ly/offer-letter",
        },
    ).json()
    ids = {r["id"] for r in body["rules"]}
    assert {"personal_email", "suspicious_link"} <= ids


def test_validation_errors(client):
    assert client.post("/check", json={"text": "too short"}).status_code == 422
    assert client.post("/check", json={"text": "x" * 20_001}).status_code == 422
    assert client.post("/check", json={"text": SCAM, "email": "not-an-email"}).status_code == 422
    assert client.post("/check", json={"text": SCAM, "lang": "fr"}).status_code == 422
    assert client.post("/check", json={}).status_code == 422


def test_oversized_body_is_rejected(client):
    res = client.post(
        "/check", content=b"{" + b" " * 70_000 + b"}", headers={"content-type": "application/json"}
    )
    assert res.status_code == 413


def test_rate_limit(client):
    codes = [client.post("/check", json={"text": GENUINE}).status_code for _ in range(10)]
    assert codes[:8] == [200] * 8 and codes[-1] == 429


def test_usage_counts_store_no_text(client):
    from legitcheck.api.main import app

    client.post("/events/first-use", json={"source": "web"})
    client.post("/check", json={"text": SCAM, "source": "extension"})
    stats = client.get("/stats").json()
    assert stats["people"] >= 1 and stats["by_verdict"]["high_risk"] >= 1

    with app.state.usage.engine.connect() as conn:
        from sqlalchemy import text

        rows = conn.execute(text("SELECT * FROM usage_daily")).all()
    assert all("Nexora" not in str(row) for row in rows)
    assert {len(row) for row in rows} == {4}


def test_cors_allows_frontend_and_extension(client):
    for origin in ("http://localhost:3000", "chrome-extension://" + "a" * 32):
        res = client.options(
            "/check", headers={"Origin": origin, "Access-Control-Request-Method": "POST"}
        )
        assert res.headers.get("access-control-allow-origin") == origin
    res = client.options(
        "/check",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in res.headers


def test_openapi_docs(client):
    assert "/check" in client.get("/openapi.json").json()["paths"]
