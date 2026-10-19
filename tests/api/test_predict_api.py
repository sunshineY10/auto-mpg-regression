"""API 冒烟测试:验证 /health 和 /predict 基本可用。"""
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["model_loaded"] is True


def test_predict_standard_case():
    payload = {
        "cylinders": 4,
        "displacement": 120,
        "horsepower": 79,
        "weight": 2625,
        "acceleration": 18.6,
        "model_year": 1982,
        "origin": 1,
    }
    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["unit"] == "mpg"
        assert 20.0 < body["mpg"] < 40.0
        assert body["model_version"]
        assert body["app_env"]


def test_predict_rejects_bad_input():
    # 负车重应触发 422 校验失败
    payload = {
        "cylinders": 4,
        "displacement": 120,
        "horsepower": 79,
        "weight": -100,
        "acceleration": 18.6,
        "model_year": 1982,
        "origin": 1,
    }
    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
        assert r.status_code == 422
