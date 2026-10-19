"""模型加载单例:服务启动时一次性加载,后续推理复用。"""
from __future__ import annotations
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline

_MODEL_PATH = Path(__file__).resolve().parent / "model" / "linear_regression.pkl"
_MODEL: Pipeline | object | None = None


def get_model():
    global _MODEL
    if _MODEL is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(f"模型文件不存在: {_MODEL_PATH}")
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def is_loaded() -> bool:
    return _MODEL is not None
