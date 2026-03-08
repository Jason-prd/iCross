# iCross 部署指南

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v2.0 |
| **最后更新** | 2026-02-18 |
| **适用环境** | 开发、测试、生产 |
| **部署方式** | Docker容器化、Kubernetes编排 |
| **文档负责人** | DevOps工程师 |

## 1. 部署架构概述

### 1.1 架构分层
```
┌─────────────────────────────────────────────────────┐
│                    负载均衡层 (Load Balancer)          │
├─────────────────────────────────────────────────────┤
│                    API网关层 (API Gateway)            │
├─────────────────────────────────────────────────────┤
│                 业务服务层 (Business Services)         │
├─────────────────────────────────────────────────────┤
│                 数据存储层 (Data Storage)             │
├─────────────────────────────────────────────────────┤
│                 监控与日志层 (Monitoring & Logging)   │
└─────────────────────────────────────────────────────┘
```

### 1.2 部署环境
| 环境 | 用途 | 访问地址 | 特点 |
|------|------|----------|------|
| **开发环境** | 开发者本地开发 | localhost | 单机部署，快速启动 |
| **测试环境** | 功能测试、集成测试 | test.icross.com | 模拟生产环境 |
| **预发环境** | 发布前验证 | staging.icross.com | 与生产环境一致 |
| **生产环境** | 线上服务 | icross.com | 高可用，多副本 |

## 2. 开发环境部署

### 2.1 环境要求
- **操作系统**：Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **Docker**：Docker Desktop 4.0+ 或 Docker Engine 20.10+
- **Docker Compose**：2.0+
- **内存**：8GB+ RAM
- **磁盘空间**：20GB+ 可用空间

### 2.2 快速开始

#### 步骤1：克隆代码仓库
```bash
git clone https://github.com/your-org/icross.git
cd icross
```

#### 步骤2：配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（根据实际情况修改）
nano .env
```

关键环境变量配置：
```env
# 应用配置
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-development-secret-key

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=icross_development
POSTGRES_USER=icross
POSTGRES_PASSWORD=icross123

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=iCross Development
```

#### 步骤3：启动开发环境
```bash
# 使用Docker Compose启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

#### 步骤4：初始化数据库
```bash
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 在容器内执行数据库迁移
alembic upgrade head

# 创建初始数据
python scripts/create_initial_data.py

# 退出容器
exit
```

#### 步骤5：访问应用
- **前端应用**：http://localhost:3000
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **数据库管理**：http://localhost:8080 (pgAdmin)

### 2.3 开发环境服务说明

#### docker-compose.dev.yml 结构
```yaml
version: '3.8'

services:
  # 后端服务
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://icross:icross123@postgres:5432/icross_development
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - backend_node_modules:/app/node_modules
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  # 前端服务
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules
    command: npm run dev

  # 数据库
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=icross_development
      - POSTGRES_USER=icross
      - POSTGRES_PASSWORD=icross123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 数据库管理工具
  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "8080:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@icross.com
      - PGADMIN_DEFAULT_PASSWORD=admin123
    volumes:
      - pgadmin_data:/var/lib/pgadmin

volumes:
  postgres_data:
  redis_data:
  pgadmin_data:
  backend_node_modules:
  frontend_node_modules:
```

### 2.4 开发工具配置

#### Visual Studio Code 开发配置
`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "typescript.preferences.importModuleSpecifier": "non-relative",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  }
}
```

#### 预提交钩子配置
```bash
# 安装pre-commit
pip install pre-commit

# 安装git钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.272
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 3. 测试环境部署

### 3.1 测试环境配置

#### 环境变量配置 `.env.test`
```env
# 应用配置
APP_ENV=testing
APP_DEBUG=false
APP_SECRET_KEY=your-test-secret-key

# 数据库配置
POSTGRES_HOST=postgres-test
POSTGRES_PORT=5432
POSTGRES_DB=icross_testing
POSTGRES_USER=icross_test
POSTGRES_PASSWORD=test123456

# Redis配置
REDIS_HOST=redis-test
REDIS_PORT=6379
REDIS_PASSWORD=test123

# 外部服务配置
OPENAI_API_KEY=sk-test-xxx
OZON_API_KEY=test-ozon-key
AMAZON_SP_API_CLIENT_ID=test-amazon-client-id
```

#### 启动测试环境
```bash
# 构建测试镜像
docker-compose -f docker-compose.test.yml build

# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行测试
docker-compose -f docker-compose.test.yml exec backend pytest

# 运行集成测试
docker-compose -f docker-compose.test.yml exec backend pytest -m integration

# 运行端到端测试
docker-compose -f docker-compose.test.yml exec frontend npm run test:e2e
```

### 3.2 测试数据库管理

#### 测试数据准备
```bash
# 创建测试数据库
docker-compose -f docker-compose.test.yml exec postgres-test psql -U icross_test -d icross_testing -c "CREATE DATABASE icross_testing;"

# 运行迁移
docker-compose -f docker-compose.test.yml exec backend alembic upgrade head

# 加载测试数据
docker-compose -f docker-compose.test.yml exec backend python scripts/load_test_data.py
```

#### 测试数据清理
```sql
-- 测试完成后清理数据
TRUNCATE TABLE users, products, orders, inventory, customers CASCADE;
```

### 3.3 自动化测试流水线

#### GitHub Actions 配置 `.github/workflows/test.yml`
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: icross_testing
          POSTGRES_USER: icross_test
          POSTGRES_PASSWORD: test123456
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -e ".[dev]"
    
    - name: Lint with ruff
      run: |
        cd backend
        ruff check .
    
    - name: Type check with mypy
      run: |
        cd backend
        mypy .
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://icross_test:test123456@localhost:5432/icross_testing
        REDIS_URL: redis://localhost:6379/0
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

## 4. 生产环境部署

### 4.1 生产环境架构

#### 高可用架构
```
┌─────────────────────────────────────────────────────────┐
│                   AWS ALB / Cloud Load Balancer          │
├─────────────────────────────────────────────────────────┤
│                 Ingress Controller (Traefik)             │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 前端服务  │ │ API网关   │ │ 用户服务  │ │ 商品服务  │   │
│  │  (3副本) │ │  (2副本)  │ │  (2副本) │ │  (3副本) │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 订单服务  │ │ 库存服务  │ │ CRM服务   │ │ Agent服务 │   │
│  │  (3副本) │ │  (2副本)  │ │  (2副本) │ │  (2副本) │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│                  Redis Cluster (3节点)                   │
├─────────────────────────────────────────────────────────┤
│              PostgreSQL HA (主从复制)                    │
│                 MinIO Cluster (3节点)                    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 生产环境准备

#### 基础设施要求
- **Kubernetes集群**：v1.24+，3个节点以上
- **存储类**：支持动态卷供应
- **负载均衡器**：云提供商负载均衡器
- **域名和SSL证书**：配置HTTPS
- **监控系统**：Prometheus + Grafana
- **日志系统**：ELK Stack 或 Loki

#### 生产环境配置 `.env.production`
```env
# 应用配置
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=${APP_SECRET_KEY}
APP_DOMAIN=icross.com
APP_HTTPS=true

# 数据库配置
POSTGRES_HOST=${POSTGRES_HOST}
POSTGRES_PORT=5432
POSTGRES_DB=icross_production
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_SSL_MODE=require

# Redis配置
REDIS_HOST=${REDIS_HOST}
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_SSL=true

# 对象存储
MINIO_ENDPOINT=${MINIO_ENDPOINT}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
MINIO_BUCKET=icross-prod

# 外部API
OPENAI_API_KEY=${OPENAI_API_KEY}
AMAZON_SP_API_CLIENT_ID=${AMAZON_SP_API_CLIENT_ID}
AMAZON_SP_API_CLIENT_SECRET=${AMAZON_SP_API_CLIENT_SECRET}
OZON_API_KEY=${OZON_API_KEY}
```

### 4.3 Kubernetes 部署

#### 命名空间配置
```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: icross
  labels:
    name: icross
```

#### 配置管理
```yaml
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: icross-config
  namespace: icross
data:
  app.env: |
    APP_ENV=production
    APP_DEBUG=false
    APP_DOMAIN=icross.com
    APP_HTTPS=true
    LOG_LEVEL=INFO
```

#### 密钥管理
```yaml
# kubernetes/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: icross-secrets
  namespace: icross
type: Opaque
stringData:
  app-secret-key: ${APP_SECRET_KEY}
  postgres-password: ${POSTGRES_PASSWORD}
  redis-password: ${REDIS_PASSWORD}
  openai-api-key: ${OPENAI_API_KEY}
  amazon-sp-api-client-secret: ${AMAZON_SP_API_CLIENT_SECRET}
```

#### 后端服务部署
```yaml
# kubernetes/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: icross
  labels:
    app: backend
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
      tier: backend
  template:
    metadata:
      labels:
        app: backend
        tier: backend
    spec:
      containers:
      - name: backend
        image: registry.icross.com/backend:${IMAGE_TAG}
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: connection-string
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: connection-string
        - name: APP_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: app-secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: icross
spec:
  selector:
    app: backend
    tier: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### 前端服务部署
```yaml
# kubernetes/frontend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: icross
  labels:
    app: frontend
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
      tier: frontend
  template:
    metadata:
      labels:
        app: frontend
        tier: frontend
    spec:
      containers:
      - name: frontend
        image: registry.icross.com/frontend:${IMAGE_TAG}
        ports:
        - containerPort: 3000
        env:
        - name: VITE_API_BASE_URL
          value: "https://api.icross.com"
        - name: VITE_APP_TITLE
          value: "iCross"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: icross
spec:
  selector:
    app: frontend
    tier: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

#### Ingress 配置
```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: icross-ingress
  namespace: icross
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - icross.com
    - api.icross.com
    secretName: icross-tls
  rules:
  - host: icross.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.icross.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

### 4.4 数据库部署

#### PostgreSQL HA 配置
```yaml
# kubernetes/postgres/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: icross
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: icross_production
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 60
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "gp2"
      resources:
        requests:
          storage: 50Gi
```

#### 数据库备份配置
```yaml
# kubernetes/postgres/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: icross
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h postgres -U $POSTGRES_USER $POSTGRES_DB | gzip > /backup/icross-$(date +%Y%m%d-%H%M%S).sql.gz
              aws s3 cp /backup/*.sql.gz s3://icross-backups/postgres/
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: POSTGRES_DB
              value: icross_production
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-secret
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-secret
                  key: secret-access-key
            - name: AWS_DEFAULT_REGION
              value: us-east-1
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            emptyDir: {}
```

### 4.5 监控与日志

#### Prometheus 监控配置
```yaml
# kubernetes/monitoring/prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
  namespace: icross
  labels:
    app: backend
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### Grafana 仪表板配置
```json
{
  "dashboard": {
    "title": "iCross Production Metrics",
    "panels": [
      {
        "title": "API请求率",
        "targets": [{
          "expr": "rate(http_requests_total[5m])",
          "legendFormat": "{{method}} {{endpoint}}"
        }]
      },
      {
        "title": "数据库连接池",
        "targets": [{
          "expr": "pg_stat_database_numbackends{datname=\"icross_production\"}",
          "legendFormat": "{{datname}}"
        }]
      }
    ]
  }
}
```

#### 日志收集配置
```yaml
# kubernetes/logging/fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: icross
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.icross.svc.cluster.local
      port 9200
      logstash_format true
      logstash_prefix kubernetes
    </match>
```

## 5. 持续集成与部署 (CI/CD)

### 5.1 GitHub Actions 工作流

#### 构建和推送镜像 `.github/workflows/build.yml`
```yaml
name: Build and Push

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ secrets.REGISTRY_URL }}/icross
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/backend:${{ steps.meta.outputs.version }}
        labels: ${{ steps.meta.outputs.labels }}
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/frontend:${{ steps.meta.outputs.version }}
        labels: ${{ steps.meta.outputs.labels }}
```

#### 部署到Kubernetes `.github/workflows/deploy.yml`
```yaml
name: Deploy to Kubernetes

on:
  workflow_run:
    workflows: ["Build and Push"]
    types:
      - completed

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.26.0'
    
    - name: Configure Kubernetes
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > $HOME/.kube/config
    
    - name: Update image tags
      run: |
        sed -i "s|image: registry.icross.com/backend:.*|image: registry.icross.com/backend:${{ github.sha }}|g" kubernetes/backend/deployment.yaml
        sed -i "s|image: registry.icross.com/frontend:.*|image: registry.icross.com/frontend:${{ github.sha }}|g" kubernetes/frontend/deployment.yaml
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f kubernetes/namespace.yaml
        kubectl apply -f kubernetes/configmap.yaml
        kubectl apply -f kubernetes/secret.yaml
        kubectl apply -f kubernetes/backend/
        kubectl apply -f kubernetes/frontend/
        kubectl apply -f kubernetes/ingress.yaml
        kubectl rollout status deployment/backend -n icross --timeout=5m
        kubectl rollout status deployment/frontend -n icross --timeout=5m
```

### 5.2 蓝绿部署策略

#### 蓝绿部署脚本
```bash
#!/bin/bash
# blue-green-deploy.sh

set -e

# 参数
SERVICE=$1
NEW_VERSION=$2
NAMESPACE=icross

# 验证参数
if [ -z "$SERVICE" ] || [ -z "$NEW_VERSION" ]; then
  echo "Usage: $0 <service> <new-version>"
  exit 1
fi

# 获取当前部署版本
CURRENT_VERSION=$(kubectl get deployment $SERVICE -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)

echo "当前版本: $CURRENT_VERSION"
echo "新版本: $NEW_VERSION"

# 创建绿色部署
GREEN_DEPLOYMENT="$SERVICE-green"
kubectl get deployment $SERVICE -n $NAMESPACE -o yaml | \
  sed "s/name: $SERVICE/name: $GREEN_DEPLOYMENT/g" | \
  sed "s|image: .*|image: registry.icross.com/$SERVICE:$NEW_VERSION|g" | \
  kubectl apply -f -

# 等待绿色部署就绪
echo "等待绿色部署就绪..."
kubectl rollout status deployment/$GREEN_DEPLOYMENT -n $NAMESPACE --timeout=5m

# 切换流量
echo "切换流量到绿色部署..."
kubectl patch service $SERVICE -n $NAMESPACE -p '{"spec":{"selector":{"app":"'$SERVICE'","version":"'$NEW_VERSION'"}}}'

# 验证新版本
echo "验证新版本..."
sleep 30
curl -f https://api.icross.com/health || (echo "新版本健康检查失败" && exit 1)

# 清理蓝色部署
echo "清理旧版本..."
kubectl delete deployment $SERVICE-blue -n $NAMESPACE

echo "蓝绿部署完成"
```

## 6. 运维管理

### 6.1 日常运维任务

#### 健康检查
```bash
# 检查所有Pod状态
kubectl get pods -n icross

# 检查服务状态
kubectl get svc -n icross

# 检查Ingress状态
kubectl get ingress -n icross

# 检查节点状态
kubectl get nodes
```

#### 日志查看
```bash
# 查看后端日志
kubectl logs -l app=backend -n icross --tail=100

# 查看特定Pod日志
kubectl logs deployment/backend -n icross

# 实时日志
kubectl logs -l app=backend -n icross -f

# 查看错误日志
kubectl logs -l app=backend -n icross --tail=100 | grep ERROR
```

#### 性能监控
```bash
# 查看资源使用
kubectl top pods -n icross
kubectl top nodes

# 查看Pod详细状态
kubectl describe pod backend-xxx -n icross

# 检查事件
kubectl get events -n icross --sort-by='.lastTimestamp'
```

### 6.2 故障排查

#### 数据库连接问题
```bash
# 检查数据库连接
kubectl exec deployment/backend -n icross -- python -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
"

# 检查Redis连接
kubectl exec deployment/backend -n icross -- python -c "
import redis
try:
    r = redis.from_url('$REDIS_URL')
    r.ping()
    print('Redis连接成功')
except Exception as e:
    print(f'Redis连接失败: {e}')
"
```

#### 网络问题排查
```bash
# 检查服务发现
kubectl run -it --rm debug --image=busybox -n icross -- nslookup backend.icross.svc.cluster.local

# 检查网络连通性
kubectl run -it --rm debug --image=busybox -n icross -- wget -O- http://backend:8000/health

# 检查DNS解析
kubectl run -it --rm debug --image=busybox -n icross -- nslookup api.icross.com
```

### 6.3 备份与恢复

#### 数据库备份
```bash
# 手动备份数据库
kubectl exec deployment/postgres -n icross -- pg_dump -U icross icross_production > backup-$(date +%Y%m%d).sql

# 备份到S3
aws s3 cp backup-$(date +%Y%m%d).sql s3://icross-backups/database/

# 验证备份
gzip -t backup-$(date +%Y%m%d).sql.gz
```

#### 数据库恢复
```bash
# 从备份恢复
kubectl exec -i deployment/postgres -n icross -- psql -U icross icross_production < backup-20260218.sql

# 从S3恢复
aws s3 cp s3://icross-backups/database/backup-20260218.sql.gz .
gunzip backup-20260218.sql.gz
kubectl exec -i deployment/postgres -n icross -- psql -U icross icross_production < backup-20260218.sql
```

## 7. 安全配置

### 7.1 网络安全
```yaml
# kubernetes/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: icross
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 7.2 密钥管理
```bash
# 使用Hashicorp Vault管理密钥
vault secrets enable -path=icross kv-v2

# 存储密钥
vault kv put icross/database username=icross password=$(openssl rand -base64 32)
vault kv put icross/redis password=$(openssl rand -base64 32)
vault kv put icross/api-keys openai=$(openssl rand -base64 32)

# Kubernetes集成
vault write auth/kubernetes/role/backend \
  bound_service_account_names=backend \
  bound_service_account_namespaces=icross \
  policies=icross \
  ttl=24h
```

### 7.3 安全扫描
```yaml
# Trivy安全扫描
- name: Scan container images
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'registry.icross.com/backend:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

## 8. 性能优化

### 8.1 资源优化
```yaml
# 资源请求和限制优化
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 8.2 自动扩缩容
```yaml
# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: icross
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 8.3 缓存优化
```yaml
# Redis缓存配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: icross
data:
  redis.conf: |
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000
```

## 9. 成本优化

### 9.1 资源优化策略
```bash
# 识别未使用资源
kubectl get deployments -n icross --no-headers | while read line; do
  deployment=$(echo $line | awk '{print $1}')
  replicas=$(echo $line | awk '{print $2}')
  if [ $replicas -eq 0 ]; then
    echo "未使用的部署: $deployment"
  fi
done

# 调整资源请求
kubectl set resources deployment/backend -n icross --requests=cpu=100m,memory=128Mi
```

### 9.2 使用Spot实例
```yaml
# 节点选择器
spec:
  template:
    spec:
      nodeSelector:
        eks.amazonaws.com/capacityType: SPOT
      tolerations:
      - key: eks.amazonaws.com/capacityType
        operator: Equal
        value: SPOT
        effect: NoSchedule
```

## 10. 附录

### 10.1 常用命令速查

#### Kubernetes命令
```bash
# 部署管理
kubectl apply -f kubernetes/
kubectl delete -f kubernetes/
kubectl rollout status deployment/backend

# 故障排查
kubectl describe pod backend-xxx
kubectl logs backend-xxx
kubectl exec -it backend-xxx -- bash

# 资源管理
kubectl get pods,svc,ingress,deployments
kubectl top pods
kubectl get events
```

#### Docker命令
```bash
# 镜像管理
docker build -t backend:latest ./backend
docker push registry.icross.com/backend:latest
docker pull registry.icross.com/backend:latest

# 容器管理
docker-compose up -d
docker-compose down
docker-compose logs -f

# 清理
docker system prune -a
```

### 10.2 故障恢复清单

#### 服务不可用
1. 检查Kubernetes集群状态
2. 检查Pod状态和日志
3. 检查服务发现和网络策略
4. 检查数据库连接
5. 检查外部依赖服务

#### 性能下降
1. 检查资源使用率
2. 检查数据库查询性能
3. 检查缓存命中率
4. 检查网络延迟
5. 检查外部API响应时间

#### 数据不一致
1. 检查数据库复制状态
2. 检查缓存一致性
3. 检查消息队列积压
4. 检查事务处理
5. 检查数据迁移状态

### 10.3 紧急联系人
- **运维团队**：ops@icross.com
- **技术支持**：support@icross.com
- **安全事件**：security@icross.com
- **云提供商**：AWS Support / 阿里云支持

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v2.0 | 2026-02-18 | 完整部署指南，覆盖所有环境 | AI Assistant |
| v1.0 | 2026-02-14 | 初始部署指南草案 | DevOps团队 |

*本文档将随着部署流程演进持续更新。*
