"""端到端冒烟:从健康检查到预测完整流程。"""
from fastapi.testclient import TestClient

from app.main import app


def test_full_flow():
    with TestClient(app) as client:
        # 1. 健康检查
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["model_loaded"] is True

        # 2. 模型信息
        r = client.get("/model-info")
        assert r.status_code == 200
        assert r.json()["model_type"] == "LinearRegression"

        # 3. 预测
        payload = {
            "cylinders": 4, "displacement": 120, "horsepower": 79,
            "weight": 2625, "acceleration": 18.6, "model_year": 1982, "origin": 1,
        }
        r = client.post("/predict", json=payload)
        assert r.status_code == 200
        assert 20.0 < r.json()["mpg"] < 40.0
