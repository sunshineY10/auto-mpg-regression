"""请求/响应数据模型:FastAPI 自动做类型校验和 422 错误返回。"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    """单次油耗预测请求,7 个原始特征。"""
    cylinders: int = Field(..., ge=3, le=16, description="气缸数")
    displacement: float = Field(..., gt=0, le=1000, description="排量(立方英寸)")
    horsepower: float = Field(..., gt=0, le=1000, description="马力")
    weight: float = Field(..., gt=0, le=10000, description="车重(磅)")
    acceleration: float = Field(..., gt=0, le=60, description="加速时间(0-60mph秒)")
    model_year: int = Field(..., ge=1900, le=2100, description="车型年份,如 1982")
    origin: int = Field(..., ge=1, le=3, description="产地:1=美国 2=欧洲 3=日本")

    @field_validator("model_year")
    @classmethod
    def _normalize_year(cls, v: int) -> int:
        """统一成 2 位年份(70~99),和训练数据口径一致。"""
        if v >= 100:
            return v - 1900
        return v


class PredictResponse(BaseModel):
    mpg: float
    unit: str = "mpg"
    model_version: str
    app_env: str


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool
