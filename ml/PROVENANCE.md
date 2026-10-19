# 溯源说明 (PROVENANCE)

数据：UCI Auto MPG（Quinlan，1993，DOI 10.24432/C5859H）
└─ v1（data-v1，md5 4f2321b4...）原始 CSV，398 行
   └─ v2（data-v2，md5 3e4175cf...）ml/data_pipeline.py 清洗制品，397 行
      （制品用途：记录清洗长什么样；训练不照搬全数据 IQR 删行）

代码：git commit <SHA>（每次 run 的 tag code_version 可查）

评估：从 v1 固定身份划分（6 缺失入训练、313 完整训练 + 6 填补 = 319 训练 / 79 测试）；
中位数/缩放都在 Pipeline 内按折拟合；linear 与 Ridge α 都用训练折 5 折 CV 选型

模型：MLflow Registry AutoMPG_LinearRegression version 8
└─ run：improved-v1-linear
   └─ 导出：models/best_model.pkl

服务：app.py 启动时 joblib.load 该文件；MODEL_VERSION 环境变量标识版本

复现实验：git checkout <commit> && dvc pull && python ml/train.py --data data/auto_mpg_v1.csv --stage improved ...
