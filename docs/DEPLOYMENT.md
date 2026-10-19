# 部署说明（DEPLOYMENT）

本项目的「交付」到构建镜像为止（项目不要求真正发布/部署到外部服务器）。

## staging 环境

- **触发**：合并到 `staging` 分支
- **流程**：`deploy-staging` job 用 GitHub Secret `STAGING_MODEL_VERSION` 生成 staging `.env`
  （`APP_ENV=staging`、`MODEL_VERSION=<secret值>`），随后执行：
  ```bash
  docker build \
    --build-arg APP_ENV=staging \
    --build-arg MODEL_VERSION="$MODEL_VERSION" \
    -t <repo>:staging .
  ```
- **所需 secrets**：`STAGING_MODEL_VERSION`

## production 环境

- **触发**：合并到 `main` 分支
- **流程**：`deploy-production` job 用 GitHub Secret `PRODUCTION_MODEL_VERSION` 生成 production `.env`
  （`APP_ENV=production`、`MODEL_VERSION=<secret值>`），随后执行：
  ```bash
  docker build \
    --build-arg APP_ENV=production \
    --build-arg MODEL_VERSION="$MODEL_VERSION" \
    -t <repo>:production .
  ```
- **所需 secrets**：`PRODUCTION_MODEL_VERSION`

## 两阶段差异

| 项 | staging | production |
|---|---|---|
| 源分支 | `staging` | `main` |
| APP_ENV | `staging` | `production` |
| MODEL_VERSION secret | `STAGING_MODEL_VERSION` | `PRODUCTION_MODEL_VERSION` |
| 镜像 tag | `:staging` | `:production` |

## 本地验证镜像

```bash
# 构建
docker build --build-arg APP_ENV=development --build-arg MODEL_VERSION=local-dev \
  -t mpg-app:local .

# 启动
docker run -d --name mpg-app -p 127.0.0.1:8000:8000 mpg-app:local

# 健康检查
curl -s http://127.0.0.1:8000/health
# {"status":"ok","model_loaded":true}

# 预测测试
curl -s -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"cylinders":4,"displacement":120,"horsepower":79,"weight":2625,"acceleration":18.6,"model_year":1982,"origin":1}'
# {"mpg":29.4,"unit":"mpg","model_version":"local-dev","app_env":"development"}

# 停止
docker stop mpg-app && docker rm mpg-app
```

## 安全说明

- 所有凭证只存 GitHub Secrets；`.env` 在流水线中现生成、不入库
- SAS 令牌只存 `.dvc/config.local`（DVC 默认排除出 Git）
- 原始数据只进 DVC/Azure，不进 Git、不进镜像
- 容器以非 root 用户运行（UID 10001），符合生产安全规范
