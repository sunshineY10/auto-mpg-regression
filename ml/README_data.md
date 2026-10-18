# Auto MPG 数据集说明(README_data)

## 1. 数据来源
- UCI Machine Learning Repository: Auto MPG
- 页面: https://archive.ics.uci.edu/dataset/9/auto+mpg (DOI: 10.24432/C5859H)
- 文件: auto-mpg.data(无表头、空白分隔,398 行 × 9 列)
- 引用: Quinlan, R. (1993). Auto MPG [Dataset]. UCI ML Repository.

## 2. v1 → v2 的变化(全部由 ml/data_pipeline.py 完成)
| 变化 | 说明 |
|---|---|
| 格式 | 无表头原始文件 → 带表头的规范 CSV(v1) |
| 缺失值 | v1 中 horsepower 的 6 个 "?" → v2 用中位数 93.5 填补(保留 6 行) |
| 类别编码 | origin(1/2/3) → origin_1/origin_2/origin_3 one-hot 三列 |
| 异常值 | 按 IQR 准则(区间 [0.25, 46.25])剔除 mpg 异常行 1 行 |
| 行数 | 398 → 397 |

## 3. commit hash 对应关系
| 版本 | git tag | 数据文件 | .dvc md5 | 提交说明 |
|---|---|---|---|---|
| v1 | data-v1 | data/auto_mpg_v1.csv | 自行填写 | Add raw Auto MPG dataset as v1 |
| v2 | data-v2 | data/auto_mpg_v2.csv | 自行填写 | Add cleaned dataset v2 |

> 复现方式:`git checkout <tag>` 后 `dvc pull` 即可取回对应版本的数据
> md5 查看命令：`cat data/auto_mpg_v1.csv.dvc`
