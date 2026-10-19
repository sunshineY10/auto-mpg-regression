"""
模型单元测试：模型可加载、预测值稳定、行为单调、特征契约一致。
"""
from __future__ import annotations

import pytest

from app.features import FEATURE_COLUMNS, payload_to_features, to_frame
from app.model import get_model
from ml.data_pipeline import V2_FEATURE_COLUMNS


# 基准样本：1982 福特 Ranger 参数，无泄漏评估下实测预测值 29.16，容差±1.5
SAMPLE = {
    "cylinders": 4,
    "displacement": 120.0,
    "horsepower": 79.0,
    "weight": 2625.0,
    "acceleration": 18.6,
    "model_year": 1982,
    "origin": 1,
}
EXPECTED_MPG = 29.16
TOLERANCE = 1.5


def test_model_file_loads():
    """边界1：生产模型文件存在且可加载。"""
    model = get_model()
    assert hasattr(model, "predict")


def test_fixed_sample_prediction_within_tolerance():
    """边界2：固定样本的预测值稳定在预期附近，防止模型文件被误替换。"""
    predicted = float(get_model().predict(to_frame(payload_to_features(SAMPLE)))[0])
    assert predicted == pytest.approx(EXPECTED_MPG, abs=TOLERANCE)


def test_heavier_car_predicted_lower_mpg():
    """边界3：单调性——其他条件相同，车越重预测油耗越高（mpg数值越低）。"""
    light = get_model().predict(to_frame(payload_to_features(SAMPLE)))[0]
    heavy_payload = {**SAMPLE, "weight": SAMPLE["weight"] + 800}
    heavy = get_model().predict(to_frame(payload_to_features(heavy_payload)))[0]
    assert heavy < light


def test_newer_car_predicted_higher_mpg():
    """边界4：单调性——训练域内（1977 vs 1982）年代越新预测油耗越高。"""
    old_payload = {**SAMPLE, "model_year": 1977}
    older = get_model().predict(to_frame(payload_to_features(old_payload)))[0]
    newer = get_model().predict(to_frame(payload_to_features(SAMPLE)))[0]
    assert newer > older


def test_feature_contract_matches_pipeline():
    """边界5：服务端特征顺序必须与训练管道产出的列顺序一致，防契约漂移。"""
    assert FEATURE_COLUMNS == V2_FEATURE_COLUMNS


def test_origin_one_hot_expansion():
    """边界6：origin 整数应正确展开为 one-hot 三列。"""
    assert payload_to_features({**SAMPLE, "origin": 2})[-3:] == [0.0, 1.0, 0.0]
    assert payload_to_features({**SAMPLE, "origin": 3})[-3:] == [0.0, 0.0, 1.0]
