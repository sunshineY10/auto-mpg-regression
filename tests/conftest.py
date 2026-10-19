"""pytest 全局 fixture:在没有真实模型文件的环境(如 CI)下 mock 模型。"""
from unittest.mock import MagicMock

import pytest

import app.model_loader as model_loader


@pytest.fixture(autouse=True)
def mock_model(monkeypatch):
    """自动把模型替换成 mock,避免 CI 上没有 pkl 文件导致测试失败。"""
    fake_model = MagicMock()
    fake_model.predict.return_value = [29.4]
    monkeypatch.setattr(model_loader, "_MODEL", fake_model)
    monkeypatch.setattr(model_loader, "is_loaded", lambda: True)
    yield
