# iCross 跨境电商智能商业操作系统

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-blue)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-blue)](https://www.typescriptlang.org)

**iCross** 是一个面向跨境电商企业的智能商业操作系统，提供从店铺管理、商品上架、订单处理到库存管理、智能采购、AI内容生成等全链路解决方案。系统采用微服务架构，支持多租户、多平台、多语言，为企业提供高效、智能、可扩展的跨境电商管理平台。

## ✨ 核心特性

- **🛒 多平台店铺管理**: 统一管理 Amazon、Ozon、Shopify 等多平台店铺
- **📦 智能商品管理**: AI驱动商品信息生成、优化和翻译
- **📊 实时订单处理**: 自动化订单同步、处理和发货
- **📈 智能库存管理**: 预测性补货、库存优化和预警
- **🤖 AI Agent工作流**: 自动化业务流程，智能决策支持
- **🌐 多语言支持**: 支持中、英、俄、西等多种语言
- **🔒 企业级安全**: 多租户隔离、数据加密、合规审计

## 🏗️ 系统架构

iCross 采用现代化微服务架构，前后端分离设计：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用       │    │   API网关       │    │   业务服务       │
│   React 18      │────│   Traefik       │────│   FastAPI       │
│   TypeScript    │    │   Rate Limiting │    │   Microservices │
│   Ant Design    │    │   Authentication│    │   Celery Tasks  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
               ┌─────▼─────┐       ┌─────▼─────┐
               │   PostgreSQL      │   Redis   │
               │   数据库集群       │   缓存队列  │
               │   TimescaleDB     │   Pub/Sub │
               └───────────┘       └───────────┘
                     │                   │
               ┌─────▼─────┐       ┌─────▼─────┐
               │   MinIO   │       │  Weaviate │
               │  对象存储  │       │  向量数据库│
               └───────────┘       └───────────┘
```

### 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| **后端框架** | FastAPI + SQLAlchemy | 高性能异步API框架 |
| **前端框架** | React 18 + TypeScript | 现代化前端开发 |
| **UI组件库** | Ant Design 5.x | 企业级设计系统 |
| **数据库** | PostgreSQL 15 + TimescaleDB | 关系型数据库，时序数据扩展 |
| **缓存/队列** | Redis 7.x | 缓存、消息队列、会话存储 |
| **向量数据库** | Weaviate | AI向量搜索和存储 |
| **对象存储** | MinIO/S3 | 文件、图片存储 |
| **容器编排** | Kubernetes + Docker | 容器化部署 |
| **监控告警** | Prometheus + Grafana | 指标监控和可视化 |
| **日志收集** | Loki + Grafana | 分布式日志收集 |

## 🚀 快速开始

### 环境要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **Docker**: Docker Desktop 4.0+ 或 Docker Engine 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.10+ (仅开发需要)
- **Node.js**: 18+ (仅开发需要)

### 使用Docker快速启动

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-org/icross.git
   cd icross
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置数据库连接等参数
   ```

3. **启动所有服务**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **访问应用**
   - 前端应用: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs
   - 监控面板: http://localhost:9090 (Grafana)

5. **初始化数据**
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend \
     python scripts/create_initial_data.py
   ```

### Ozon平台集成快速开始

iCross已集成完整的Ozon Seller API客户端，支持与Ozon电商平台的无缝对接。

1. **配置Ozon API凭证**
   在 `.env` 文件中添加：
   ```env
   # Ozon API配置
   OZON_CLIENT_ID=your-client-id
   OZON_API_KEY=your-api-key
   ```

2. **安装Ozon API库**
   ```bash
   # 从本地目录安装
   docker-compose -f docker-compose.dev.yml exec backend \
     pip install -e /app/python-ozon-api-main
   ```

3. **测试Ozon连接**
   ```bash
   # 通过API测试连接
   curl -X GET "http://localhost:8000/api/v1/ozon/test-connection" \
     -H "Authorization: Bearer <your-token>"
   ```

4. **使用Ozon集成API**
   - 获取商品列表: `GET /api/v1/ozon/products`
   - 获取分类树: `GET /api/v1/ozon/categories`
   - 健康检查: `GET /api/v1/ozon/health`

详细集成指南请参考 [Ozon API集成文档](docs/OZON_API_INTEGRATION.md)。

### 开发环境搭建

详细开发环境配置请参考 [开发指南](docs/DEVELOPMENT_GUIDE.md)。

## 📚 详细文档

### 产品设计文档
- **[产品路线图](docs/product_design/ROADMAP.md)** - 四阶段发布计划
- **[v1.0 基础平台设计](docs/product_design/v1.0/BASIC_PLATFORM_DESIGN.md)** - 核心ERP功能
- **[v2.0 AIGC与采购自动化](docs/product_design/v2.0/AIGC_PURCHASING_DESIGN.md)** - AI内容生成与智能采购
- **[v3.0 AI Agent与智能运营](docs/product_design/v3.0/AI_AGENT_SMART_OPS_DESIGN.md)** - AI工作流与智能决策
- **[v4.0 生态扩展](docs/product_design/v4.0/ECOSYSTEM_EXPANSION_DESIGN.md)** - 金融服务与全球扩展

### 技术文档
- **[架构设计](docs/ARCHITECTURE.md)** - 系统架构和技术选型
- **[API设计](docs/API_DESIGN.md)** - 详细的API接口规范
- **[数据库设计](docs/DATABASE_SCHEMA.md)** - 完整的数据模型和表结构
- **[开发指南](docs/DEVELOPMENT_GUIDE.md)** - 开发环境、编码规范、工作流程
- **[部署指南](docs/DEPLOYMENT_GUIDE.md)** - 开发、测试、生产环境部署
- **[测试策略](docs/TESTING_STRATEGY.md)** - 单元测试、集成测试、E2E测试
- **[安全与合规](docs/SECURITY_COMPLIANCE.md)** - 安全策略和合规要求
- **[Ozon API集成](docs/OZON_API_INTEGRATION.md)** - Ozon平台API集成指南

### 业务文档
- **[产品需求文档](docs/PRD.md)** - 详细的产品需求和业务规则
- **[AI助手指南](AGENTS.md)** - AI开发助手的使用指南

## 🗺️ 发布计划

iCross 采用四阶段迭代开发模式：

| 版本 | 阶段 | 核心功能 | 预计时间 |
|------|------|----------|----------|
| **v1.0** | 基础平台阶段 | 多租户、店铺集成、商品/订单/库存管理、基础CRM | 12-16周 |
| **v2.0** | AIGC与采购自动化 | AI商品内容生成、智能采购、高级库存管理 | v1.0 + 3个月 |
| **v3.0** | AI Agent与智能运营 | AI Agent引擎、工作流设计器、智能推荐、移动App | v2.0 + 4个月 |
| **v4.0** | 生态扩展阶段 | 金融服务、多平台扩展、物流生态、开放平台 | v3.0 + 6个月 |

详细路线图请查看 [ROADMAP.md](docs/product_design/ROADMAP.md)。

## 🧪 测试与质量

项目采用全面的测试策略确保代码质量：

- **单元测试**: 使用pytest和vitest覆盖核心业务逻辑
- **集成测试**: 测试API端点和服务集成
- **端到端测试**: 使用Playwright测试完整用户流程
- **性能测试**: 使用Locust进行负载测试
- **安全测试**: 定期进行安全扫描和渗透测试

运行测试：
```bash
# 后端测试
cd backend && pytest

# 前端测试
cd frontend && pnpm test

# 端到端测试
pnpm test:e2e
```

## 🔧 开发工作流

1. **创建功能分支**: `git checkout -b feature/your-feature`
2. **开发功能**: 编写代码，遵循编码规范
3. **运行测试**: 确保所有测试通过
4. **提交代码**: 使用Conventional Commits格式
5. **创建PR**: 提交代码审查请求
6. **代码审查**: 至少2位审查者批准
7. **合并代码**: 通过CI/CD流水线部署

详细开发流程请参考 [开发指南](docs/DEVELOPMENT_GUIDE.md#4-开发工作流程)。

## 🛡️ 安全与合规

iCross 遵循企业级安全标准：

- **数据加密**: 传输层TLS，存储数据加密
- **身份认证**: JWT令牌，多因素认证支持
- **访问控制**: RBAC角色权限控制
- **审计日志**: 完整操作审计追踪
- **合规性**: GDPR、CCPA等数据保护法规
- **漏洞管理**: 定期安全扫描和修复

详细安全策略请查看 [安全与合规文档](docs/SECURITY_COMPLIANCE.md)。

## 🤝 贡献指南

我们欢迎社区贡献！请查看以下指南：

1. **报告问题**: 在GitHub Issues中描述问题
2. **功能请求**: 提交功能建议和用例
3. **代码贡献**: Fork仓库，创建功能分支，提交PR
4. **文档改进**: 帮助改进文档和示例

详细贡献指南请参考 [开发指南贡献部分](docs/DEVELOPMENT_GUIDE.md#9-贡献指南)。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

- **项目主页**: https://github.com/your-org/icross
- **问题反馈**: https://github.com/your-org/icross/issues
- **文档网站**: https://docs.icross.com (建设中)
- **商业支持**: contact@icross.com

## 🙏 致谢

感谢所有贡献者和用户对 iCross 项目的支持！特别感谢：

- 开源社区提供的优秀技术栈
- 跨境电商企业的实际业务需求反馈
- 开发团队的辛勤工作和创新

---

**© 2026 iCross Team. All rights reserved.**

*最后更新: 2026-02-18*