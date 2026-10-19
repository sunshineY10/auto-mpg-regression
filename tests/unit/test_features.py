"""特征契约测试:确保训练与服务使用相同的特征列。"""
from ml.utils import FEATURE_COLUMNS


def test_feature_columns_count():
    assert len(FEATURE_COLUMNS) == 7


def test_feature_columns_order():
    assert FEATURE_COLUMNS == [
        "cylinders", "displacement", "horsepower", "weight",
        "acceleration", "model_year", "origin",
    ]
