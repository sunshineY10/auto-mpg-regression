"""MPG 油耗预测 FastAPI 服务入口。
启动: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
import os
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.model_loader import get_model, is_loaded
from app.schemas import HealthResponse, PredictRequest, PredictResponse

APP_ENV = os.getenv("APP_ENV", "development")
MODEL_VERSION = os.getenv("MODEL_VERSION", "local-dev")

FEATURE_ORDER = [
    "cylinders", "displacement", "horsepower", "weight",
    "acceleration", "model_year", "origin",
]

app = FastAPI(title="MPG Prediction Service", version=MODEL_VERSION)


@app.on_event("startup")
def _startup() -> None:
    # 启动时预热加载模型,失败直接让容器退出
    get_model()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=is_loaded())


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    model = get_model()
    row = {k: getattr(req, k) for k in FEATURE_ORDER}
    X = pd.DataFrame([row], columns=FEATURE_ORDER)
    mpg = float(model.predict(X)[0])
    return PredictResponse(
        mpg=round(mpg, 2),
        unit="mpg",
        model_version=MODEL_VERSION,
        app_env=APP_ENV,
    )


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        "<h3>MPG Prediction Service</h3>"
        "<p>POST <code>/predict</code> with JSON body, GET <code>/health</code> to check status.</p>"
    )
