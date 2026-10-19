# auto-mpg-regression

用线性回归预测汽车城市循环油耗(mpg)的 FastAPI 服务，含完整 MLOps/DevOps 流程：
DVC 数据版本(v1/v2)、MLflow 实验跟踪、pytest 测试、ruff lint、Docker、GitHub Actions CI/CD。

## 应用接口

- `POST /predict`：输入 7 个车辆参数，返回预测油耗(mpg)
- `GET /health`：健康检查，返回模型加载状态
- `GET /model-info`：返回模型类型、版本、特征列表等元信息
- `GET /`：首页说明

### 本地运行
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000/docs 可看到 Swagger 交互文档。

## 分支方案与合并路径

```
feature/* ──► dev ──► staging ──► main
```

- `dev`：公共开发基线，功能分支合并回这里
- `staging`：预发环境分支，合并后自动构建 staging 镜像
- `main`：生产环境分支，合并后自动构建 production 镜像
- 三个分支均为受保护分支，开启 **Require status checks**：CI 全绿才允许合并

## 流水线触发矩阵

| 事件 | 触发 job | 内容 |
| --- | --- | --- |
| PR → dev / staging / main | `ci` | ruff check + pytest + docker build |
| push → staging | `ci` + `deploy-staging` | 上述检查 + staging secrets 生成 .env + 构建 staging 镜像 |
| push → main | `ci` + `deploy-production` | 上述检查 + production secrets 生成 .env + 构建 production 镜像 |

## 项目结构

```
├── app/                  # FastAPI 服务
│   ├── main.py           # 入口：/predict /health /model-info
│   ├── schemas.py        # Pydantic 请求/响应模型
│   ├── model_loader.py   # 模型加载单例
│   └── model/
│       └── linear_regression.pkl   # 生产模型
├── ml/                   # 训练与实验
│   ├── train.py          # 训练脚本 + MLflow 记录
│   └── README_data.md    # 数据版本说明
├── data/                 # DVC 跟踪的数据（CSV 不入库）
│   ├── auto_mpg_v1.csv.dvc
│   └── auto_mpg_v2.csv.dvc
├── tests/                # pytest 测试
│   ├── conftest.py
│   └── api/test_predict_api.py
├── .github/workflows/ci.yml   # CI/CD 流水线
├── Dockerfile            # 生产级镜像构建
├── .dockerignore
├── requirements.txt      # 运行时依赖
├── requirements-dev.txt   # 开发/CI 依赖
├── pyproject.toml        # ruff 配置
└── README.md
```

## 本地 Docker 验证

```bash
docker build --build-arg APP_ENV=development --build-arg MODEL_VERSION=local-dev -t mpg-app:local .
docker run -d --name mpg-app -p 127.0.0.1:8000:8000 mpg-app:local
curl http://127.0.0.1:8000/health
```

## 安全说明

- 所有凭证只存 GitHub Secrets，`.env` 在流水线中现生成、不入库
- SAS 令牌只存 `.dvc/config.local`（DVC 默认排除出 Git）
- 原始数据只进 DVC/Azure，不进 Git、不进镜像
