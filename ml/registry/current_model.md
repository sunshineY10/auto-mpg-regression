# 生产模型登记卡 (current_model)

- 注册模型名：AutoMPG_LinearRegression
- 生产版本号：version 8（对应 run: export-best-model）
- 模型形式：sklearn Pipeline(中位数填充 -> 独热编码 -> LinearRegression)
- 评估方法：固定身份划分（79 条独立测试记录）；中位数/编码均在 Pipeline 内按训练折拟合（无泄漏）；选型依据训练折 5 折 CV
- 训练数据：data/auto_mpg_v1.csv（DVC v1，md5 4f2321b47a64d9849f9325d64ceb5361）；
  训练行数 319 = 313 完整记录 + 6 条马力缺失（训练折中位数 95.0 填补）
- 代码版本：git commit SHA: ab5a3147d4ee25dfabdd95c4a9bdacdef8d48c6c
- 导出文件：models/best_model.pkl（随服务进入部署，约 2.1KB）
- 指标（79 条独立测试集）：RMSE 3.2691 / MAE 2.4890 / R² 0.7906
  （诚实对照：baseline 为 3.2727 / 2.4198 / 0.7902，RMSE 与 R² 持平略好、MAE 略差）
- 加载方式：joblib.load(models/best_model.pkl)，输入须为带列名的 DataFrame
  （列序见 app.py 的 FEATURE_ORDER）
