"""Auto MPG 数据流水线:从 UCI 原始数据生成 v1(原样)与 v2(清洗+编码)两个数据集版本。
v1 = 原始数据直接转成规范 CSV,一行未删(horsepower 列的 "?" 原样保留);
v2 = 在 v1 基础上做数据清洗:"?" -> 中位数填补、origin one-hot 编码、按 IQR 剔除 mpg 异常行。
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

# auto-mpg.data 没有表头,各列顺序如下(car_name 带双引号,内部可含空格)
RAW_COLUMNS = [
    "mpg",
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
    "origin",
    "car_name",
]

# v2 的特征列顺序。训练(ml/train.py)与服务(app/features.py)必须遵守同一份契约
V2_FEATURE_COLUMNS = [
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
    "origin_1",
    "origin_2",
    "origin_3",
]


# ---------------------------------------------------------------- 可复用清洗函数
def read_raw(raw_path: Path) -> pd.DataFrame:
    """读取无表头、空白分隔的原始数据"""
    return pd.read_csv(raw_path, sep=r"\s+", header=None, names=RAW_COLUMNS)


def coerce_horsepower(df: pd.DataFrame) -> pd.DataFrame:
    """horsepower 的 "?" -> NaN,再转成数值列"""
    out = df.copy()
    out["horsepower"] = pd.to_numeric(out["horsepower"], errors="coerce")
    return out


def impute_horsepower(df: pd.DataFrame, median: float | None = None):
    """用中位数填补 horsepower 缺失"""
    out = df.copy()
    if median is None:
        median = float(out["horsepower"].median())
    out["horsepower"] = out["horsepower"].fillna(median)
    return out, float(median)


def encode_origin(df: pd.DataFrame) -> pd.DataFrame:
    """origin(1/2/3 类别)one-hot 展开为 origin_1/2/3 三列"""
    out = pd.get_dummies(df, columns=["origin"], prefix="origin", dtype=int)
    for col in ("origin_1", "origin_2", "origin_3"):
        if col not in out.columns:
            out[col] = 0
    return out


def iqr_bounds(df: pd.DataFrame):
    """在目标 mpg 上计算 IQR 阈值"""
    q1, q3 = df["mpg"].quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def apply_iqr(df: pd.DataFrame, lower: float, upper: float) -> pd.DataFrame:
    """只保留 mpg 落在 [lower, upper] 内的行"""
    return df[(df["mpg"] >= lower) & (df["mpg"] <= upper)]


# ---------------------------------------------------------------- 数据版本生成
def make_v1(raw_path: Path, out_path: Path) -> None:
    """v1:原始数据 -> 带表头的 CSV,内容保持原样"""
    df = read_raw(raw_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[v1] 读取 {raw_path} -> 写出 {out_path}")
    print(f"[v1] 行数={len(df)},列={list(df.columns)}")
    print(f"[v1] horsepower 含 '?' 的行数: {(df['horsepower'] == '?').sum()}")


def make_v2(v1_path: Path, out_path: Path) -> None:
    """v2:在 v1 基础上做清洗与编码,输出建模用的规整 CSV"""
    df = pd.read_csv(v1_path)
    n_raw = len(df)

    # 1) horsepower 的 "?" -> NaN -> 用中位数填补
    df = coerce_horsepower(df)
    n_missing = int(df["horsepower"].isna().sum())
    df, median_hp = impute_horsepower(df)

    # 2) origin one-hot 编码
    df = encode_origin(df)

    # 3) 按 IQR 准则剔除 mpg 异常行
    lower, upper = iqr_bounds(df)
    n_outliers = int(((df["mpg"] < lower) | (df["mpg"] > upper)).sum())
    df = apply_iqr(df, lower, upper)

    # 4) 只保留 target + 特征列,去掉 car_name
    df = df[["mpg"] + V2_FEATURE_COLUMNS]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[v2] 输入 {v1_path}({n_raw} 行)-> 输出 {out_path}({len(df)} 行)")
    print(f"[v2] 中位数填补 horsepower 缺失 {n_missing} 处(中位数={median_hp:.1f})")
    print(f"[v2] IQR 剔除 mpg 异常行 {n_outliers} 行(区间 [{lower:.2f}, {upper:.2f}])")
    print("[v2] origin 已 one-hot 编码为 origin_1/origin_2/origin_3")
    print(f"[v2] 最终列: {list(df.columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto MPG 数据版本流水线")
    sub = parser.add_subparsers(dest="stage", required=True)

    p_v1 = sub.add_parser("v1", help="原始数据 -> v1 规范 CSV")
    p_v1.add_argument("--raw", type=Path, required=True, help="UCI 下载的 auto-mpg.data")
    p_v1.add_argument("--out", type=Path, required=True, help="输出的 v1 CSV 路径")

    p_v2 = sub.add_parser("v2", help="v1 -> v2 清洗+编码")
    p_v2.add_argument("--in", dest="in_path", type=Path, required=True, help="v1 CSV 路径")
    p_v2.add_argument("--out", type=Path, required=True, help="输出的 v2 CSV 路径")

    args = parser.parse_args()
    if args.stage == "v1":
        make_v1(args.raw, args.out)
    else:
        make_v2(args.in_path, args.out)


if __name__ == "__main__":
    main()
