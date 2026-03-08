# iCross 开发指南

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v2.0 |
| **最后更新** | 2026-02-18 |
| **适用对象** | 开发工程师、技术负责人 |
| **技术栈** | Python 3.10+, FastAPI, React 18, TypeScript |
| **文档负责人** | 技术主管 |

## 1. 项目结构与架构

### 1.1 项目目录结构
```
icross/
├── backend/                    # 后端服务
│   ├── app/                   # 应用代码
│   │   ├── api/              # API路由
│   │   │   ├── v1/           # API版本1
│   │   │   │   ├── endpoints/ # 端点定义
│   │   │   │   └── routers/   # 路由定义
│   │   ├── core/             # 核心模块
│   │   │   ├── config/       # 配置管理
│   │   │   ├── database/     # 数据库连接
│   │   │   ├── security/     # 安全相关
│   │   │   └── exceptions/   # 异常定义
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── services/         # 业务服务
│   │   ├── tasks/            # 异步任务
│   │   ├── utils/            # 工具函数
│   │   └── dependencies/     # FastAPI依赖项
│   ├── tests/                # 测试代码
│   ├── alembic/              # 数据库迁移
│   ├── scripts/              # 脚本文件
│   ├── requirements.txt      # Python依赖
│   ├── pyproject.toml        # Python项目配置
│   └── Dockerfile            # Docker镜像配置
├── frontend/                  # 前端应用
│   ├── src/                  # 源代码
│   │   ├── api/              # API客户端
│   │   ├── components/       # React组件
│   │   │   ├── common/       # 通用组件
│   │   │   ├── layout/       # 布局组件
│   │   │   └── features/     # 功能组件
│   │   ├── hooks/            # 自定义Hook
│   │   ├── pages/            # 页面组件
│   │   ├── stores/           # 状态管理
│   │   ├── types/            # TypeScript类型
│   │   ├── utils/            # 工具函数
│   │   ├── styles/           # 样式文件
│   │   └── constants/        # 常量定义
│   ├── tests/                # 前端测试
│   ├── public/               # 静态资源
│   ├── package.json          # 项目依赖
│   ├── vite.config.ts        # Vite配置
│   ├── tsconfig.json         # TypeScript配置
│   └── Dockerfile            # Docker镜像配置
├── docs/                     # 项目文档
├── kubernetes/               # K8s部署配置
├── docker-compose.yml        # 本地开发配置
├── .github/                  # GitHub Actions工作流
├── .gitignore               # Git忽略文件
├── README.md                # 项目说明
└── AGENTS.md                # AI助手指南
```

### 1.2 架构模式

#### 后端架构
- **分层架构**：Controller → Service → Repository → Model
- **依赖注入**：FastAPI依赖注入系统
- **领域驱动设计**：按业务领域组织代码
- **CQRS模式**：命令和查询分离（部分模块）

#### 前端架构
- **组件化架构**：React函数组件 + Hooks
- **状态管理**：Zustand（轻量级状态管理）
- **路由管理**：React Router v6
- **API集成**：React Query（数据获取和缓存）

## 2. 开发环境设置

### 2.1 环境要求
- **Python**: 3.10+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

### 2.2 后端开发环境

#### 安装Python依赖
```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐使用uv）
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装依赖
pip install -e ".[dev]"

# 或使用uv（更快）
uv pip install -e ".[dev]"
```

#### 配置开发环境
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
# 使用你喜欢的编辑器编辑.env文件
```

#### 数据库初始化
```bash
# 运行数据库迁移
alembic upgrade head

# 创建初始数据
python scripts/create_initial_data.py

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.3 前端开发环境

#### 安装Node.js依赖
```bash
# 进入前端目录
cd frontend

# 安装依赖（推荐使用pnpm）
pnpm install

# 或使用npm/yarn
npm install
# 或
yarn install
```

#### 启动开发服务器
```bash
# 启动开发服务器
pnpm dev

# 或使用npm/yarn
npm run dev
# 或
yarn dev
```

#### 构建生产版本
```bash
# 构建生产版本
pnpm build

# 预览构建结果
pnpm preview
```

### 2.4 使用Docker开发

#### 快速启动开发环境
```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f backend

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

#### 进入容器开发
```bash
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.dev.yml exec frontend bash
```

## 3. 代码规范与质量标准

### 3.1 Python代码规范

#### 格式化工具
```bash
# 使用black格式化代码
black .

# 使用isort排序导入
isort .

# 使用ruff检查和修复
ruff check . --fix
```

#### 类型检查
```bash
# 使用mypy进行类型检查
mypy .
```

#### 代码质量
```bash
# 使用pylint进行代码质量检查
pylint app/

# 使用bandit进行安全扫描
bandit -r app/
```

#### 配置文件示例
`pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
target-version = "py310"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
]
ignore = [
    "E501",  # line too long, handled by black
]
```

### 3.2 TypeScript/React代码规范

#### 格式化工具
```bash
# 使用Prettier格式化代码
pnpm format

# 使用ESLint检查和修复
pnpm lint:fix
```

#### 类型检查
```bash
# TypeScript类型检查
pnpm type-check
```

#### 配置文件示例
`eslint.config.js`:
```javascript
import js from '@eslint/js'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'

export default [
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
      'react': react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...typescript.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
]
```

`prettier.config.js`:
```javascript
export default {
  semi: false,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  endOfLine: 'lf',
}
```

### 3.3 命名规范

#### Python命名规范
- **类名**：`CamelCase`，如 `UserService`, `OrderRepository`
- **函数名**：`snake_case`，如 `get_user_by_id`, `create_order`
- **变量名**：`snake_case`，如 `user_id`, `order_total`
- **常量名**：`UPPER_SNAKE_CASE`，如 `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE`
- **模块名**：`snake_case`，如 `user_service.py`, `order_models.py`

#### TypeScript命名规范
- **组件名**：`PascalCase`，如 `UserProfile`, `OrderList`
- **函数名**：`camelCase`，如 `getUserById`, `createOrder`
- **变量名**：`camelCase`，如 `userId`, `orderTotal`
- **常量名**：`UPPER_SNAKE_CASE`，如 `MAX_RETRY_COUNT`, `API_BASE_URL`
- **接口名**：`PascalCase`，如 `IUser`, `IOrder`
- **类型名**：`PascalCase`，如 `UserType`, `OrderStatus`

### 3.4 注释规范

#### Python文档字符串
```python
def calculate_order_total(order_items: List[OrderItem]) -> Decimal:
    """
    计算订单总金额。
    
    参数:
        order_items: 订单商品列表
        
    返回:
        订单总金额（包含税费和运费）
        
    异常:
        ValueError: 当订单商品列表为空时
        
    示例:
        >>> items = [OrderItem(price=100, quantity=2)]
        >>> calculate_order_total(items)
        Decimal('200.00')
    """
    if not order_items:
        raise ValueError("订单商品列表不能为空")
    
    total = sum(item.price * item.quantity for item in order_items)
    return total
```

#### TypeScript注释
```typescript
/**
 * 获取用户详细信息
 * @param userId 用户ID
 * @param includeOrders 是否包含订单信息
 * @returns 用户详细信息，包含订单列表（如果指定）
 * @throws {ApiError} 当用户不存在或权限不足时
 * @example
 * const user = await getUserDetails('user_123', true)
 * console.log(user.orders.length)
 */
async function getUserDetails(
  userId: string,
  includeOrders: boolean = false
): Promise<UserWithOrders> {
  // 实现代码
}
```

## 4. 开发工作流程

### 4.1 Git工作流

#### 分支策略
- **main**：生产环境代码，受保护分支
- **develop**：开发分支，功能集成
- **feature/***：功能开发分支
- **bugfix/***：Bug修复分支
- **release/***：发布分支
- **hotfix/***：热修复分支

#### 提交规范
使用Conventional Commits规范：
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

类型说明：
- **feat**：新功能
- **fix**：Bug修复
- **docs**：文档更新
- **style**：代码格式（不影响功能）
- **refactor**：代码重构
- **test**：测试相关
- **chore**：构建过程或辅助工具变动

示例：
```bash
git commit -m "feat(user): 添加用户注册功能"
git commit -m "fix(auth): 修复登录token过期问题"
git commit -m "docs(api): 更新API文档"
```

### 4.2 功能开发流程

#### 1. 创建功能分支
```bash
# 从develop分支创建新功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication
```

#### 2. 开发功能
```bash
# 编写代码，遵循编码规范
# 编写测试用例
# 更新相关文档
```

#### 3. 提交代码
```bash
# 添加更改
git add .

# 提交更改
git commit -m "feat(auth): 添加用户认证功能"

# 或使用交互式提交
git commit
```

#### 4. 推送到远程
```bash
# 推送分支到远程仓库
git push origin feature/user-authentication
```

#### 5. 创建Pull Request
- 在GitHub上创建PR
- 描述功能变更
- 关联相关Issue
- 请求代码审查

#### 6. 代码审查
- 至少需要2个审查者批准
- 通过自动化测试
- 解决审查意见

#### 7. 合并到develop
```bash
# 合并前更新分支
git checkout feature/user-authentication
git pull origin develop

# 解决冲突（如果有）
# 运行测试
pytest

# 推送更新
git push origin feature/user-authentication

# 在GitHub上合并PR
```

### 4.3 发布流程

#### 1. 创建发布分支
```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

#### 2. 版本准备
```bash
# 更新版本号
# 更新CHANGELOG.md
# 运行完整测试套件
```

#### 3. 合并到main
```bash
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags
```

#### 4. 合并回develop
```bash
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop
```

#### 5. 删除发布分支
```bash
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

## 5. 测试策略

### 5.1 测试金字塔
```
        E2E测试 (10%)
        集成测试 (20%)
        单元测试 (70%)
```

### 5.2 后端测试

#### 单元测试
```python
# tests/unit/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService()
    
    def test_create_user(self, user_service):
        """测试创建用户"""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_create_user_duplicate_email(self, user_service):
        """测试重复邮箱创建用户"""
        user_data = UserCreate(
            email="duplicate@example.com",
            password="password123",
            name="Test User"
        )
        
        # 第一次创建应该成功
        user_service.create_user(user_data)
        
        # 第二次创建应该失败
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(user_data)
        
        assert "邮箱已存在" in str(exc_info.value)
```

#### 集成测试
```python
# tests/integration/test_user_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestUserAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_create_user_endpoint(self, client):
        """测试用户创建API端点"""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "api_test@example.com",
                "password": "password123",
                "name": "API Test User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "api_test@example.com"
        assert data["name"] == "API Test User"
        assert "id" in data
        assert "password" not in data  # 密码不应返回
    
    def test_get_user_endpoint(self, client):
        """测试获取用户API端点"""
        # 先创建用户
        create_response = client.post(
            "/api/v1/users",
            json={
                "email": "get_test@example.com",
                "password": "password123",
                "name": "Get Test User"
            }
        )
        user_id = create_response.json()["id"]
        
        # 获取用户
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "get_test@example.com"
```

#### 测试配置
`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    slow: 慢速测试
    db: 需要数据库的测试
```

### 5.3 前端测试

#### 单元测试（组件测试）
```typescript
// tests/unit/UserProfile.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import UserProfile from '@/components/UserProfile'
import { describe, it, expect, vi } from 'vitest'

describe('UserProfile', () => {
  const mockUser = {
    id: 'user_123',
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'https://example.com/avatar.jpg',
  }

  const mockOnEdit = vi.fn()

  it('显示用户信息', () => {
    render(<UserProfile user={mockUser} onEdit={mockOnEdit} />)
    
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
    expect(screen.getByAltText('John Doe的头像')).toHaveAttribute('src', mockUser.avatar)
  })

  it('点击编辑按钮触发回调', () => {
    render(<UserProfile user={mockUser} onEdit={mockOnEdit} />)
    
    const editButton = screen.getByRole('button', { name: /编辑/i })
    fireEvent.click(editButton)
    
    expect(mockOnEdit).toHaveBeenCalledWith(mockUser.id)
  })
})
```

#### 集成测试（API测试）
```typescript
// tests/integration/userApi.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { userApi } from '@/api/user'
import { mockServer } from '@/mocks/server'

describe('User API', () => {
  beforeEach(() => {
    mockServer.listen()
  })

  afterEach(() => {
    mockServer.resetHandlers()
  })

  afterAll(() => {
    mockServer.close()
  })

  it('获取用户列表', async () => {
    const users = await userApi.getUsers({
      page: 1,
      limit: 10,
    })

    expect(users).toHaveLength(10)
    expect(users[0]).toHaveProperty('id')
    expect(users[0]).toHaveProperty('name')
    expect(users[0]).toHaveProperty('email')
  })

  it('创建用户', async () => {
    const newUser = {
      name: 'New User',
      email: 'new@example.com',
      password: 'password123',
    }

    const createdUser = await userApi.createUser(newUser)

    expect(createdUser).toHaveProperty('id')
    expect(createdUser.name).toBe(newUser.name)
    expect(createdUser.email).toBe(newUser.email)
    expect(createdUser).not.toHaveProperty('password')
  })
})
```

#### 测试配置
`vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/types.ts',
      ],
    },
  },
})
```

### 5.4 端到端测试

#### Playwright配置
```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('登录功能', () => {
  test('用户成功登录', async ({ page }) => {
    // 访问登录页面
    await page.goto('/login')
    
    // 填写登录表单
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    
    // 点击登录按钮
    await page.click('button[type="submit"]')
    
    // 验证登录成功
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('.user-name')).toHaveText('Test User')
  })

  test('登录失败显示错误信息', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('input[name="email"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    
    // 验证错误信息
    await expect(page.locator('.error-message')).toHaveText('邮箱或密码错误')
    await expect(page).toHaveURL('/login') // 应停留在登录页面
  })
})
```

## 6. 性能优化指南

### 6.1 后端性能优化

#### 数据库优化
```python
# 避免N+1查询问题
# 错误示例
users = session.query(User).all()
for user in users:
    orders = session.query(Order).filter(Order.user_id == user.id).all()  # N+1查询

# 正确示例
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.orders)).all()
```

#### 缓存策略
```python
from app.core.cache import cache

@cache(ttl=300)  # 缓存5分钟
def get_user_by_id(user_id: str) -> Optional[User]:
    """获取用户信息，使用缓存"""
    return session.query(User).filter(User.id == user_id).first()

# 使用Redis缓存热点数据
async def get_dashboard_data(tenant_id: str) -> Dict:
    cache_key = f"dashboard:{tenant_id}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # 从数据库获取数据
    data = await calculate_dashboard_data(tenant_id)
    
    # 缓存结果
    await redis.setex(cache_key, 300, json.dumps(data))
    
    return data
```

#### 异步处理
```python
from celery import Celery
from app.core.config import settings

celery = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery.task
def generate_product_report(product_id: str):
    """异步生成商品报告"""
    # 耗时操作
    report = generate_report(product_id)
    
    # 发送通知
    send_notification(f"商品报告已生成: {product_id}")
    
    return report.id
```

### 6.2 前端性能优化

#### 代码分割
```typescript
// 路由级代码分割
import { lazy } from 'react'

const Dashboard = lazy(() => import('@/pages/Dashboard'))
const Products = lazy(() => import('@/pages/Products'))
const Orders = lazy(() => import('@/pages/Orders'))

// 组件懒加载
const ProductImageGallery = lazy(() => import('@/components/ProductImageGallery'))
```

#### 图片优化
```typescript
// 使用图片懒加载
import { LazyLoadImage } from 'react-lazy-load-image-component'

function ProductCard({ product }) {
  return (
    <div className="product-card">
      <LazyLoadImage
        src={product.image}
        alt={product.name}
        effect="blur"
        placeholderSrc="/placeholder.jpg"
      />
      {/* 其他内容 */}
    </div>
  )
}

// 使用WebP格式
const getOptimizedImageUrl = (url: string, width: number, height: number) => {
  return `https://images.icross.com/${width}x${height},webp/${url}`
}
```

#### 状态管理优化
```typescript
// 使用React.memo避免不必要的重渲染
const ProductList = React.memo(function ProductList({ products }) {
  return (
    <div>
      {products.map(product => (
        <ProductItem key={product.id} product={product} />
      ))}
    </div>
  )
})

// 使用useMemo和useCallback
function ProductFilter({ filters, onFilterChange }) {
  const memoizedFilters = useMemo(() => {
    return Object.entries(filters).filter(([_, value]) => value !== null)
  }, [filters])

  const handleFilterChange = useCallback((key, value) => {
    onFilterChange(key, value)
  }, [onFilterChange])

  // 组件实现
}
```

## 7. 安全开发指南

### 7.1 输入验证
```python
from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class UserCreate(BaseModel):
    """用户创建请求模型"""
    email: EmailStr
    password: constr(min_length=8, max_length=100)
    name: constr(min_length=2, max_length=100)
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')]  # E.164格式
    
    class Config:
        extra = "forbid"  # 禁止额外字段

# 在API中使用
@app.post("/users")
async def create_user(user: UserCreate):
    # Pydantic已经验证了输入
    user_data = user.dict()
    # 业务逻辑...
```

### 7.2 SQL注入防护
```python
# 永远不要这样做
query = f"SELECT * FROM users WHERE email = '{email}'"

# 应该使用参数化查询
from sqlalchemy import text
query = text("SELECT * FROM users WHERE email = :email")
result = session.execute(query, {"email": email})

# 或使用ORM
user = session.query(User).filter(User.email == email).first()
```

### 7.3 XSS防护
```typescript
// 使用React的自动转义
function UserComment({ comment }) {
  // 安全：React会自动转义HTML
  return <div>{comment}</div>
}

// 如果需要渲染HTML，使用dangerouslySetInnerHTML并清理
import DOMPurify from 'dompurify'

function RichContent({ html }) {
  const cleanHtml = DOMPurify.sanitize(html)
  
  return (
    <div 
      dangerouslySetInnerHTML={{ __html: cleanHtml }}
    />
  )
}
```

### 7.4 认证与授权
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
) -> User:
    """获取当前用户依赖"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证凭证已过期",
        )
    
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return user

# 使用依赖
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## 8. 调试与问题排查

### 8.1 后端调试

#### 日志记录
```python
import logging
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用日志
def process_order(order_id: str):
    logger.info(f"开始处理订单: {order_id}")
    
    try:
        # 业务逻辑
        result = do_something()
        logger.info(f"订单处理完成: {order_id}")
        return result
    except Exception as e:
        logger.error(f"订单处理失败: {order_id}, 错误: {str(e)}", exc_info=True)
        raise
```

#### 调试器使用
```python
# 使用pdb调试
import pdb

def complex_function():
    # ... 代码
    pdb.set_trace()  # 设置断点
    # ... 代码

# 或使用breakpoint()（Python 3.7+）
def another_function():
    # ... 代码
    breakpoint()  # 进入调试器
    # ... 代码
```

### 8.2 前端调试

#### 浏览器开发者工具
- **Console**：查看日志和错误
- **Network**：监控API请求和响应
- **Sources**：调试JavaScript代码
- **Performance**：分析性能问题
- **Application**：查看存储和缓存

#### React开发者工具
- 安装React Developer Tools浏览器扩展
- 检查组件树和状态
- 分析组件性能

#### 日志记录
```typescript
// 创建日志工具
class Logger {
  private static instance: Logger
  
  static getInstance() {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }
  
  info(message: string, data?: any) {
    console.log(`[INFO] ${message}`, data || '')
  }
  
  error(message: string, error?: Error) {
    console.error(`[ERROR] ${message}`, error || '')
  }
  
  warn(message: string, data?: any) {
    console.warn(`[WARN] ${message}`, data || '')
  }
  
  debug(message: string, data?: any) {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, data || '')
    }
  }
}

export const logger = Logger.getInstance()

// 使用
logger.info('用户登录成功', { userId: '123' })
logger.error('API请求失败', error)
```

## 9. 贡献指南

### 9.1 如何贡献

#### 报告问题
1. 在GitHub Issues中搜索是否已有相关问题
2. 创建新Issue，描述问题和重现步骤
3. 提供环境信息（版本、操作系统等）
4. 添加相关日志或截图

#### 提交代码
1. Fork项目仓库
2. 创建功能分支
3. 编写代码并添加测试
4. 运行测试确保通过
5. 提交Pull Request

#### 代码审查
1. 确保代码符合项目规范
2. 添加适当的测试
3. 更新相关文档
4. 检查性能影响
5. 验证安全性

### 9.2 开发约定

#### 代码审查清单
- [ ] 代码符合项目编码规范
- [ ] 添加了适当的测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 考虑了性能影响
- [ ] 检查了安全性问题
- [ ] 处理了边界情况
- [ ] 代码可读性好

#### 提交消息模板
```
<type>(<scope>): <subject>

<body>

<footer>
```

示例：
```
feat(auth): 添加多因素认证支持

- 添加TOTP多因素认证
- 支持备份代码
- 添加相关API端点
- 更新用户设置界面

Closes #123
Related to #456
```

## 10. 第三方平台集成

### 10.1 Ozon平台集成

iCross系统已集成完整的Ozon Seller API客户端库，支持与Ozon电商平台的无缝对接。

#### 10.1.1 集成架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  iCross业务层    │    │  Ozon适配层     │    │  Ozon API客户端  │
│  ProductService │────│  OzonAdapter    │────│  OzonAPI        │
│  OrderService   │    │  · 数据转换      │    │  · 原生API调用   │
│  InventoryService│    │  · 错误处理      │    │  · 限流重试      │
└─────────────────┘    │  · 日志记录      │    └─────────────────┘
                       └─────────────────┘
```

#### 10.1.2 已实现功能
- **商品管理**: 商品列表获取、导入、更新、删除、归档
- **分类管理**: 分类树获取、属性查询
- **图片管理**: 商品图片上传、信息查询
- **条码管理**: 条码生成、添加
- **订单管理** (待扩展): 订单同步、状态更新

#### 10.1.3 快速开始
1. **配置环境变量**:
   ```env
   OZON_CLIENT_ID=your-client-id
   OZON_API_KEY=your-api-key
   ```

2. **使用适配器**:
   ```python
   from app.integrations.ozon.adapter import OzonIntegrationAdapter
   
   async with OzonIntegrationAdapter() as adapter:
       # 获取商品列表
       products = await adapter.get_products(limit=100)
       
       # 获取分类树
       categories = await adapter.get_categories()
   ```

3. **定时同步**:
   ```python
   # 使用Celery定时任务同步数据
   from app.integrations.ozon.tasks import sync_products_task
   
   # 手动触发同步
   sync_products_task.delay()
   ```

#### 10.1.4 详细文档
完整集成指南请参考 [Ozon API集成文档](OZON_API_INTEGRATION.md)。

### 10.2 Amazon平台集成 (规划中)
- **SP-API集成**: 使用Amazon Selling Partner API
- **功能规划**: 商品同步、订单管理、库存更新
- **技术方案**: AWS SigV4签名、OAuth2.0授权

### 10.3 Shopify平台集成 (规划中)
- **REST API集成**: Shopify Admin API
- **功能规划**: 店铺管理、商品同步、订单处理
- **技术方案**: GraphQL支持、Webhook事件处理

### 10.4 其他平台扩展
- **AliExpress**: 速卖通API集成 (v4.0规划)
- **Walmart**: 沃尔玛API集成
- **Lazada**: 来赞达API集成
- **Mercado Libre**: 美客多API集成

## 11. 学习资源

### 11.1 技术栈文档
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Ant Design**: https://ant.design/

### 11.2 设计模式
- **领域驱动设计（DDD）**: https://domainlanguage.com/ddd/
- **Clean Architecture**: https://blog.cleancoder.com/
- **微服务模式**: https://microservices.io/

### 11.3 性能优化
- **Web性能优化**: https://web.dev/learn/
- **数据库优化**: https://use-the-index-luke.com/
- **缓存策略**: https://redis.io/docs/

### 11.4 安全最佳实践
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Web安全指南**: https://cheatsheetseries.owasp.org/
- **API安全**: https://github.com/OWASP/API-Security

## 12. 附录

### A. 常用工具推荐

#### 开发工具
- **IDE**: VS Code, PyCharm, WebStorm
- **终端**: Windows Terminal, iTerm2
- **数据库工具**: DBeaver, pgAdmin, TablePlus
- **API测试**: Postman, Insomnia, Bruno

#### 代码质量
- **Python**: black, isort, ruff, mypy, bandit
- **TypeScript**: ESLint, Prettier, TypeScript
- **Git**: pre-commit, commitlint

#### 监控与调试
- **日志**: structlog, loguru
- **监控**: Sentry, Datadog, New Relic
- **性能**: Py-Spy, Chrome DevTools

### B. 常见问题解答

#### Q: 如何添加新的API端点？
A: 
1. 在 `app/api/v1/endpoints/` 创建新文件
2. 定义Pydantic模型
3. 实现业务逻辑
4. 在 `app/api/v1/routers/` 中添加路由
5. 编写测试用例

#### Q: 如何添加新的数据库表？
A:
1. 在 `app/models/` 创建模型类
2. 创建Alembic迁移脚本
3. 运行迁移：`alembic upgrade head`
4. 更新相关服务和API

#### Q: 前端如何添加新页面？
A:
1. 在 `src/pages/` 创建页面组件
2. 在路由配置中添加路由
3. 创建相关组件和样式
4. 添加页面测试

#### Q: 如何部署本地修改？
A:
1. 运行测试确保通过
2. 提交代码到功能分支
3. 创建Pull Request
4. 通过代码审查后合并
5. CI/CD管道自动部署

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v2.1 | 2026-02-18 | 添加第三方平台集成章节，更新Ozon API集成指南 | AI Assistant |
| v2.0 | 2026-02-18 | 完整开发指南，覆盖全流程 | AI Assistant |
| v1.0 | 2026-02-14 | 初始开发指南草案 | 技术团队 |

*本文档将随着开发实践演进持续更新。*
