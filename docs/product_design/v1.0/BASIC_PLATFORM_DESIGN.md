# iCross v1.0 基础平台阶段详细设计文档

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v1.0 |
| **最后更新** | 2026-02-18 |
| **对应产品版本** | iCross MVP v1.0 |
| **阶段名称** | 基础平台阶段 (Basic Platform Phase) |
| **时间周期** | 12-16周 |
| **文档负责人** | 产品经理 + 技术架构师 |

## 1. 概述

### 1.1 阶段目标
构建iCross基础ERP平台，实现跨境电商卖家最核心的业务管理功能：
- **多租户用户系统**：支持团队协作和权限管理
- **多平台店铺集成**：连接Ozon、Amazon、Shopify等主要电商平台
- **商品统一管理**：多平台商品同步和集中管理
- **订单统一处理**：自动化订单处理和基础发货流程
- **库存管理**：多仓库库存跟踪和预警
- **基础CRM**：客户信息管理和交易记录

### 1.2 核心价值主张
- **统一管理界面**：一个系统管理所有电商平台店铺，避免多平台切换
- **自动化同步**：自动同步商品、订单、库存数据，减少人工操作
- **团队协作**：多用户多角色支持，实现运营、客服、财务分工协作
- **数据集中**：跨平台数据聚合，提供统一业务视图
- **效率提升**：自动化流程减少人工错误，提升运营效率50%以上

### 1.3 目标用户
- **初创型卖家**：1-2人团队，月销售额 < 10万人民币，管理 < 500个SKU
- **成长型卖家**：3-5人团队，月销售额 10-50万人民币，管理 500-2000个SKU

### 1.4 成功指标
- 店铺连接成功率 > 90%
- 商品同步准确率 > 95%
- 订单处理效率提升 > 50%（相比手工处理）
- 用户满意度 > 4.2/5.0
- 内测用户数量：100个跨境电商卖家

## 2. 功能规格

### 2.1 多租户与用户管理系统

#### 2.1.1 功能描述
支持多租户SaaS架构，提供完整的用户注册、登录、团队管理、权限控制功能。

#### 2.1.2 功能列表
1. **用户注册与登录**
   - 邮箱/手机号注册
   - 邮箱验证/手机验证码验证
   - 密码登录（支持密码重置）
   - JWT令牌认证
   - 记住登录状态（7天）

2. **团队管理**
   - 团队创建（注册时自动创建）
   - 团队基本信息管理（名称、Logo、联系方式）
   - 团队设置（时区、货币、语言）
   - 团队数据隔离（不同团队数据完全隔离）

3. **用户管理**
   - 团队成员邀请（通过邮箱邀请）
   - 成员角色分配（预定义角色：超级管理员、团队管理员、运营、客服、财务、只读）
   - 成员权限管理（基于角色的细粒度权限控制）
   - 成员状态管理（激活/停用）
   - 个人信息管理（头像、昵称、联系方式）

4. **权限系统**
   - 模块级权限控制（商品、订单、库存、客户等模块）
   - 操作级权限控制（查看、创建、编辑、删除、导出）
   - 数据级权限控制（基于团队的数据隔离）
   - 权限继承和覆盖机制

5. **安全功能**
   - 密码强度验证
   - 登录失败锁定（5次失败锁定15分钟）
   - 登录IP白名单（可选）
   - 登录审计日志（记录所有登录尝试）
   - 会话管理（查看和终止活跃会话）

#### 2.1.3 技术规格
- **认证方式**：JWT (JSON Web Token)
- **密码哈希**：bcrypt (12轮)
- **会话管理**：Redis存储活跃会话
- **权限存储**：PostgreSQL RBAC表结构
- **审计日志**：PostgreSQL审计日志表

### 2.2 多店铺与跨平台集成

#### 2.2.1 功能描述
支持Ozon、Amazon、Shopify三个主要电商平台的API集成，实现多店铺统一管理。

#### 2.2.2 功能列表
1. **平台支持**
   - Ozon Seller API (优先级1)
   - Amazon Selling Partner API (SP-API) (优先级2)
   - Shopify Admin API (优先级3)

2. **店铺连接**
   - 平台选择（Ozon/Amazon/Shopify）
   - API密钥配置（Client ID、Client Secret、Access Token等）
   - 店铺信息获取（自动获取店铺名称、时区、货币等）
   - 连接测试（验证API连通性）
   - 连接状态监控（实时显示API健康状态）

3. **店铺管理**
   - 店铺列表显示（按平台分组）
   - 店铺基本信息管理（名称、Logo、备注）
   - 店铺状态管理（启用/停用）
   - 店铺分组管理（按品类、市场等分组）
   - 店铺标签管理（自定义标签）

4. **API配置管理**
   - API调用配额监控（显示各平台API调用次数和限制）
   - 同步频率配置（商品、订单、库存同步频率）
   - Webhook配置（支持Shopify Webhook）
   - API错误日志（记录API调用错误和重试）

5. **数据同步**
   - 手动同步（立即同步按钮）
   - 定时同步（默认配置：商品每2小时，订单每5分钟，库存每30分钟）
   - 增量同步（只同步变更数据，减少API调用）
   - 同步状态监控（显示最近同步时间和状态）
   - 同步错误处理（自动重试3次，失败告警）

#### 2.2.3 技术规格
- **Ozon集成**：使用python-ozon-api库，支持Ozon Seller API v2
- **Amazon集成**：使用亚马逊SP-API Python SDK，支持OAuth 2.0
- **Shopify集成**：使用Shopify Python API库，支持OAuth和Webhook
- **异步处理**：Celery任务队列处理同步任务
- **错误处理**：指数退避重试机制，错误告警通知

### 2.3 商品管理与同步

#### 2.3.1 功能描述
从连接的电商平台同步商品信息，提供统一的商品管理界面。

#### 2.3.2 功能列表
1. **商品同步**
   - 自动同步（按配置频率自动同步）
   - 手动同步（立即同步指定店铺或全部店铺）
   - 增量同步（只同步变更商品）
   - 全量同步（每天凌晨执行全量同步）
   - 同步冲突处理（保留最新版本或人工确认）

2. **商品列表**
   - 多维度筛选（平台、店铺、品类、状态、标签）
   - 表格视图（关键字段展示：图片、标题、SKU、价格、库存、状态）
   - 卡片视图（商品图片和关键信息）
   - 批量操作（批量编辑、批量上下架、批量导出）
   - 高级搜索（按标题、SKU、描述搜索）

3. **商品详情**
   - 基本信息（标题、描述、SKU、价格、库存）
   - 图片管理（主图、详情图、场景图）
   - 变体管理（颜色、尺寸等变体属性）
   - 分类管理（平台分类映射到系统分类）
   - 属性管理（自定义属性字段）

4. **商品编辑**
   - 基本信息编辑（标题、描述、价格等）
   - 批量编辑（批量修改价格、库存、状态等）
   - 跨平台编辑（同时更新多个平台的商品信息）
   - 编辑历史（记录所有修改操作）

5. **商品状态管理**
   - 在售状态（正常销售）
   - 停售状态（手动停售或库存为零）
   - 归档状态（长时间无销售且无库存）
   - 违规状态（平台检测到违规，自动下架）

6. **商品导入导出**
   - Excel/CSV模板导入
   - 批量导出（支持自定义字段选择）
   - 导入映射配置（字段映射规则）
   - 导入验证（数据格式和业务规则验证）

#### 2.3.3 技术规格
- **数据模型**：统一商品模型，支持多平台商品关联
- **图片存储**：MinIO对象存储，CDN加速
- **批量处理**：Celery异步任务处理批量操作
- **搜索功能**：Elasticsearch全文搜索（可选，v1.1）

### 2.4 订单管理与处理

#### 2.4.1 功能描述
自动同步多平台订单，提供统一的订单处理界面，支持基础发货流程。

#### 2.4.2 功能列表
1. **订单同步**
   - 实时同步（新订单5分钟内同步到系统）
   - 定时拉取（每5分钟拉取一次订单更新）
   - 增量同步（只同步变更订单）
   - 同步状态监控（显示最近同步订单数量和时间）

2. **订单列表**
   - 多维度筛选（平台、店铺、订单状态、日期范围、金额范围）
   - 表格视图（关键字段：订单号、客户、金额、状态、创建时间）
   - 订单状态标签（不同状态不同颜色标签）
   - 批量操作（批量发货、批量打印、批量导出）
   - 高级搜索（按订单号、客户姓名、商品名称搜索）

3. **订单详情**
   - 订单基本信息（订单号、平台、店铺、创建时间、状态）
   - 客户信息（姓名、地址、电话、邮箱）
   - 商品明细（商品名称、SKU、数量、单价、总价）
   - 支付信息（支付方式、支付状态、支付时间）
   - 物流信息（物流方式、运单号、发货时间、跟踪信息）

4. **订单处理**
   - 订单审核（标记为待发货）
   - 发货操作（填写物流信息和运单号）
   - 订单完成（标记为已完成）
   - 订单取消（取消订单并退款）
   - 售后处理（退货、换货、退款）

5. **订单状态流**
   - 待付款 → 待发货（客户付款后自动流转）
   - 待发货 → 已发货（填写物流单号后更新）
   - 已发货 → 已完成（物流签收后自动标记，或超时14天自动完成）
   - 异常状态（地址错误、库存不足、支付问题等）

6. **发货管理**
   - 发货预报（向销售平台预报发货信息）
   - 面单打印（支持批量打印面单）
   - 物流跟踪（手动或自动查询物流状态）
   - 发货确认（确认发货后通知客户）

#### 2.3.3 技术规格
- **订单模型**：统一订单模型，支持多平台订单映射
- **状态机**：订单状态机，确保状态流转合规
- **异步处理**：Celery处理订单同步和发货操作
- **物流集成**：基础物流跟踪API集成（快递鸟）

### 2.5 库存管理

#### 2.5.1 功能描述
统一库存管理，支持多仓库、一件代发和自主发货模式。

#### 2.5.2 功能列表
1. **库存视图**
   - 实时库存（各商品在各仓库的实时库存数量）
   - 库存分布（按仓库、按平台、按品类展示库存分布）
   - 库存变化（库存变动历史记录）
   - 库存预警（库存低于安全库存时高亮显示）

2. **仓库管理**
   - 仓库创建（物理仓库、虚拟仓库、供应商仓库）
   - 仓库信息管理（名称、地址、联系人、容量）
   - 仓库状态管理（启用/停用）
   - 仓库权限控制（按用户分配仓库访问权限）

3. **库存操作**
   - 库存调整（盘点、调拨、报损、报溢）
   - 库存预留（为订单预留库存）
   - 库存释放（取消订单时释放库存）
   - 库存同步（自动同步库存到销售平台）

4. **库存预警**
   - 安全库存设置（按商品设置安全库存阈值）
   - 预警通知（库存低于安全库存时发送通知）
   - 预警规则（可配置的预警条件和通知方式）
   - 预警历史（记录所有预警事件）

5. **库存模式支持**
   - 一件代发模式（库存为供应商库存，下单后自动通知供应商）
   - 自主发货模式（库存为自有库存，下单后从自有仓库发货）
   - 混合模式（部分商品一件代发，部分自主发货）

6. **库存报表**
   - 库存周转率（按商品、按品类计算周转率）
   - 库龄分析（库存商品存放时间分析）
   - 滞销品识别（长时间无销售的商品）
   - 库存价值（按成本价计算库存总价值）

#### 2.5.3 技术规格
- **库存模型**：支持多仓库、多库存类型（实物、在途、预留）
- **实时同步**：Redis缓存热点库存数据，确保实时性
- **事务处理**：库存操作支持数据库事务，确保数据一致性
- **预警系统**：定时任务检查库存预警条件

### 2.6 基础CRM客户管理

#### 2.6.1 功能描述
管理B端采购客户和C端销售客户的基本信息、交易历史和沟通记录。

#### 2.6.2 功能列表
1. **客户管理**
   - 客户列表（按类型、等级、状态筛选）
   - 客户基本信息（姓名、联系方式、地址、备注）
   - 客户分组（自定义客户分组）
   - 客户标签（为客户添加自定义标签）

2. **客户视图**
   - 客户详情（基本信息、交易历史、沟通记录）
   - 客户订单（客户所有订单列表）
   - 客户消费统计（消费金额、订单数量、平均订单价值）
   - 客户活跃度（最近购买时间、购买频率）

3. **沟通管理**
   - 沟通记录（记录与客户的沟通内容）
   - 跟进任务（创建客户跟进任务和提醒）
   - 沟通模板（常用沟通话术模板）
   - 沟通渠道（邮件、电话、站内消息记录）

4. **客户分级**
   - 分级规则（基于消费金额、购买频率分级）
   - 等级管理（VIP、重要、普通等级别）
   - 等级权益（不同等级客户享受不同权益）
   - 等级自动调整（基于规则自动调整客户等级）

5. **客户导入导出**
   - Excel/CSV模板导入
   - 客户数据导出（支持自定义字段）
   - 数据去重（导入时检测重复客户）
   - 数据验证（验证客户数据格式和完整性）

#### 2.6.3 技术规格
- **数据模型**：统一客户模型，支持B端和C端客户
- **数据去重**：基于邮箱、电话等关键字段自动去重
- **权限控制**：客户数据访问权限控制
- **数据同步**：从订单自动创建和更新客户信息

## 3. 用户故事与验收标准

### 3.1 多租户与用户管理

#### 用户故事1：团队创建与邀请
**作为** 企业主
**我希望** 创建团队账户并邀请团队成员
**以便** 实现团队协作和分工

**验收标准**：
1. 用户注册时可选择"创建新团队"或"加入现有团队"
2. 团队创建者自动成为团队超级管理员
3. 超级管理员可以邀请成员加入团队（通过邮箱）
4. 被邀请成员收到邀请邮件，点击链接完成注册和加入
5. 团队成员数量限制：基础版最多5人，高级版最多20人
6. 团队成员可以查看团队基本信息和管理自己的个人信息

#### 用户故事2：角色权限分配
**作为** 团队管理员
**我希望** 为团队成员分配不同角色和权限
**以便** 控制各成员能访问的模块和操作

**验收标准**：
1. 支持6种预定义角色：超级管理员、团队管理员、运营、客服、财务、只读
2. 每个角色有明确的权限集合（模块访问+操作权限）
3. 管理员可以查看和修改成员角色
4. 权限变更立即生效（无需重新登录）
5. 无权限的操作在界面上隐藏或禁用
6. API层面验证权限，防止越权操作

### 3.2 多店铺集成

#### 用户故事3：店铺连接
**作为** 多平台卖家
**我希望** 在一个系统中连接所有电商平台的店铺
**以便** 统一管理各平台业务

**验收标准**：
1. 支持Ozon、Amazon、Shopify平台连接
2. 连接流程引导用户获取和输入API密钥
3. 连接测试验证API连通性和权限
4. 连接成功显示店铺基本信息（名称、Logo、平台类型）
5. 店铺连接状态实时显示（正常、异常、停用）
6. 支持断开连接和重新连接

#### 用户故事4：数据同步监控
**作为** 运营人员
**我希望** 监控各店铺数据同步状态
**以便** 及时发现和解决同步问题

**验收标准**：
1. 店铺列表显示最近同步时间和状态
2. 同步错误显示具体错误信息和建议解决方案
3. 支持手动触发同步（立即同步按钮）
4. 同步历史记录可查看（最近100条记录）
5. API调用配额显示和预警（接近限制时预警）
6. 同步失败自动重试3次，重试失败发送通知

### 3.3 商品管理

#### 用户故事5：商品统一视图
**作为** 运营人员
**我希望** 在一个界面查看所有平台的商品
**以便** 统一管理商品信息和状态

**验收标准**：
1. 商品列表显示各平台商品统一视图
2. 支持按平台、店铺、状态、品类等多维度筛选
3. 商品卡片显示关键信息：图片、标题、SKU、价格、库存、状态
4. 点击商品进入详情页，显示完整信息和各平台信息
5. 支持批量操作：批量上下架、批量修改价格、批量导出
6. 商品搜索支持标题、SKU、描述全文搜索

#### 用户故事6：商品信息编辑
**作为** 运营人员
**我希望** 编辑商品信息并同步到各平台
**以便** 保持各平台商品信息一致

**验收标准**：
1. 商品编辑界面支持修改基本信息（标题、描述、价格等）
2. 支持单平台编辑和跨平台批量编辑
3. 编辑前显示原值和各平台当前值对比
4. 编辑保存后自动同步到对应平台
5. 编辑历史记录保存，可查看和回滚
6. 敏感操作（如价格大幅调整）需要二次确认

### 3.4 订单处理

#### 用户故事7：订单统一处理
**作为** 发货人员
**我希望** 在一个界面处理所有平台的订单
**以便** 提高发货效率

**验收标准**：
1. 订单列表显示各平台待处理订单
2. 支持按平台、状态、日期筛选订单
3. 订单详情显示完整信息：商品、客户、支付、物流
4. 发货操作：填写物流信息和运单号，一键发货
5. 发货后自动更新平台订单状态
6. 支持批量发货和打印面单

#### 用户故事8：订单状态跟踪
**作为** 客服人员
**我希望** 跟踪订单全生命周期状态
**以便** 及时响应客户查询

**验收标准**：
1. 订单状态清晰显示：待付款、待发货、已发货、已完成、已取消、售后中
2. 状态流转自动或手动触发，符合业务规则
3. 状态变更记录保存，可查看状态历史
4. 物流跟踪信息自动或手动更新
5. 异常订单自动识别和标记（地址错误、支付问题等）
6. 订单状态变更自动通知客户（可选）

### 3.5 库存管理

#### 用户故事9：实时库存查看
**作为** 库存管理员
**我希望** 实时查看各商品在各仓库的库存数量
**以便** 准确掌握库存情况

**验收标准**：
1. 库存列表显示商品在各仓库的实时库存
2. 库存数据实时更新（销售出库、采购入库等）
3. 支持按商品、仓库、品类筛选库存
4. 库存预警商品高亮显示（低于安全库存）
5. 库存变动历史记录可查看
6. 库存报表展示库存周转率、库龄等分析数据

#### 用户故事10：库存预警设置
**作为** 采购人员
**我希望** 设置库存预警规则
**以便** 及时补货避免缺货

**验收标准**：
1. 支持按商品设置安全库存阈值
2. 预警规则支持：库存低于阈值、库存为0、库存过高
3. 预警通知支持：站内消息、邮件、钉钉/飞书
4. 预警历史记录保存
5. 支持批量设置预警规则（按品类、按供应商）
6. 预警触发后自动生成采购建议（v2.0功能）

### 3.6 CRM客户管理

#### 用户故事11：客户信息管理
**作为** 销售经理
**我希望** 管理客户信息和交易历史
**以便** 维护客户关系和提供个性化服务

**验收标准**：
1. 客户列表显示客户基本信息和最后交易时间
2. 客户详情页显示完整信息、订单历史、沟通记录
3. 客户信息可从订单自动创建和更新
4. 支持客户分组和标签管理
5. 客户数据支持导入导出
6. 客户搜索支持姓名、电话、邮箱、订单号

#### 用户故事12：客户沟通记录
**作为** 客服人员
**我希望** 记录与客户的沟通内容
**以便** 跟踪客户问题和提供连续服务

**验收标准**：
1. 客户详情页显示沟通记录时间线
2. 支持添加新的沟通记录（电话、邮件、站内消息）
3. 沟通记录支持附件上传
4. 支持创建跟进任务和设置提醒
5. 沟通模板支持快速插入常用话术
6. 沟通记录支持按时间、类型、人员筛选

## 4. UI/UX设计

### 4.1 设计原则
- **简洁直观**：界面简洁，操作直观，新用户30分钟内可上手
- **一致性**：统一的设计语言和交互模式
- **效率优先**：常用操作一键完成，批量操作支持
- **响应式**：适配桌面、平板、手机屏幕
- **数据可视化**：关键数据图表展示，一目了然

### 4.2 核心页面设计

#### 4.2.1 仪表板 (Dashboard)
**布局**：卡片式布局，关键指标卡片 + 图表
**主要内容**：
1. 今日关键指标卡片：新订单数、待处理订单、库存预警、同步状态
2. 销售趋势图表（近7天/30天）
3. 订单状态分布饼图
4. 库存预警列表（TOP 10）
5. 最近活动时间线（同步、订单、库存变动）

#### 4.2.2 店铺管理 (Shops)
**布局**：列表视图 + 详情侧边栏
**主要内容**：
1. 店铺卡片列表（按平台分组）
2. 每个店铺卡片显示：平台Logo、店铺名称、连接状态、最近同步时间
3. 店铺详情侧边栏：API配置、同步设置、连接日志
4. 顶部操作栏：添加店铺、批量操作、筛选搜索

#### 4.2.3 商品中心 (Products)
**布局**：表格视图 + 筛选侧边栏
**主要内容**：
1. 商品表格：图片、标题、SKU、价格、库存、状态、平台
2. 高级筛选侧边栏：平台、店铺、品类、状态、价格范围、库存范围
3. 批量操作工具栏：选择商品后的批量操作按钮
4. 视图切换：表格视图/卡片视图
5. 导出功能：Excel/CSV导出

#### 4.2.4 订单中心 (Orders)
**布局**：表格视图 + 快速筛选栏
**主要内容**：
1. 订单表格：订单号、客户、金额、状态、平台、创建时间
2. 状态筛选快速栏：待付款、待发货、已发货、已完成、全部
3. 高级搜索：订单号、客户姓名、商品名称、日期范围
4. 批量操作：批量发货、批量打印、批量导出
5. 订单详情模态框：完整订单信息，发货操作

#### 4.2.5 库存管理 (Inventory)
**布局**：表格视图 + 仓库导航
**主要内容**：
1. 仓库导航侧边栏：选择查看特定仓库库存
2. 库存表格：商品图片、名称、SKU、仓库库存、总库存、安全库存、状态
3. 库存预警高亮显示（红色背景或图标）
4. 库存操作工具栏：调整库存、设置预警、导出报表
5. 库存图表：库存分布饼图、库存趋势图

#### 4.2.6 客户管理 (Customers)
**布局**：列表视图 + 详情视图
**主要内容**：
1. 客户列表：头像、姓名、等级、最近消费、订单数
2. 客户分组侧边栏：按等级、标签、自定义分组筛选
3. 客户详情页：选项卡布局（基本信息、订单历史、沟通记录）
4. 沟通记录时间线：按时间倒序显示沟通记录
5. 快速操作：添加沟通记录、创建跟进任务、发送消息

### 4.3 组件设计规范

#### 4.3.1 颜色规范
- **主色调**：蓝色 (#1890ff) - 行动、专业、信任
- **辅助色**：绿色 (#52c41a) - 成功、完成；红色 (#f5222d) - 错误、警告；橙色 (#fa8c16) - 警告、注意
- **中性色**：文字黑 (#262626)、文字灰 (#8c8c8c)、背景灰 (#f5f5f5)、边框 (#d9d9d9)

#### 4.3.2 字体规范
- **字体家族**：-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif
- **字体大小**：基础12px，正文14px，标题16px/18px/20px
- **行高**：1.5倍行高，确保可读性

#### 4.3.3 间距规范
- **基础单位**：8px
- **间距比例**：8px、16px、24px、32px、48px、64px
- **容器内边距**：16px/24px
- **组件间距**：16px

#### 4.3.4 按钮规范
- **主要按钮**：蓝色背景，白色文字，圆角4px
- **次要按钮**：白色背景，蓝色边框，蓝色文字
- **危险按钮**：红色背景或红色边框
- **按钮尺寸**：大(40px)、中(32px)、小(24px)
- **按钮状态**：正常、悬停、点击、禁用

### 4.4 响应式设计

#### 4.4.1 断点定义
- **移动端**：< 768px
- **平板端**：768px - 1024px
- **桌面端**：> 1024px

#### 4.4.2 移动端适配策略
- **简化导航**：移动端使用底部导航栏，只保留核心功能
- **卡片布局**：移动端使用卡片布局替代表格布局
- **操作简化**：移动端聚焦查看和简单操作，复杂操作引导到桌面端
- **触摸友好**：按钮和交互元素最小44px触摸目标

#### 4.4.3 响应式表格策略
- **桌面端**：完整表格展示
- **平板端**：简化表格，隐藏次要列
- **移动端**：卡片列表，每个卡片显示关键信息，详情点击展开

## 5. API设计

### 5.1 API基础规范

#### 5.1.1 通用规则
- **协议**：HTTPS only
- **域名**：api.icross.com
- **版本**：URL路径包含版本号 `/api/v1/`
- **编码**：UTF-8
- **时间格式**：ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
- **时区**：UTC时间，客户端负责时区转换

#### 5.1.2 请求规范
- **请求头**：
  ```
  Content-Type: application/json
  Authorization: Bearer {access_token}
  X-Request-ID: {uuid}  # 请求追踪ID
  ```
- **分页参数**：
  ```
  GET /api/v1/products?page=1&limit=50
  ```
- **筛选参数**：
  ```
  GET /api/v1/orders?status=pending&platform=ozon&start_date=2026-01-01&end_date=2026-01-31
  ```

#### 5.1.3 响应规范
- **成功响应**：
  ```json
  {
    "success": true,
    "data": { ... }, // 或 [ ... ] 数组
    "meta": {
      "page": 1,
      "limit": 50,
      "total": 150,
      "total_pages": 3
    }
  }
  ```
- **错误响应**：
  ```json
  {
    "success": false,
    "error": {
      "code": "INVALID_TOKEN",
      "message": "访问令牌无效或已过期",
      "details": { ... } // 可选，详细错误信息
    }
  }
  ```

### 5.2 认证API

#### 5.2.1 用户登录
**端点**：`POST /api/v1/auth/login`
**请求**：
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "token_type": "bearer",
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "张三",
      "role": "admin",
      "team_id": "team_456"
    }
  }
}
```

#### 5.2.2 令牌刷新
**端点**：`POST /api/v1/auth/refresh`
**请求**：
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
**响应**：同登录响应，返回新的access_token

### 5.3 用户与团队API

#### 5.3.1 获取当前用户信息
**端点**：`GET /api/v1/users/me`
**响应**：
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "张三",
    "avatar_url": "https://...",
    "role": "admin",
    "team_id": "team_456",
    "settings": {
      "timezone": "Asia/Shanghai",
      "currency": "CNY",
      "language": "zh-CN"
    }
  }
}
```

#### 5.3.2 获取团队成员
**端点**：`GET /api/v1/team/members`
**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": "user_123",
      "email": "user1@example.com",
      "name": "张三",
      "role": "admin",
      "status": "active",
      "joined_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": "user_124",
      "email": "user2@example.com",
      "name": "李四",
      "role": "operator",
      "status": "active",
      "joined_at": "2026-01-02T00:00:00Z"
    }
  ]
}
```

### 5.4 店铺API

#### 5.4.1 获取店铺列表
**端点**：`GET /api/v1/shops`
**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": "shop_123",
      "name": "我的Ozon店铺",
      "platform": "ozon",
      "platform_shop_id": "123456",
      "status": "connected",
      "sync_status": {
        "last_sync_time": "2026-02-18T10:30:00Z",
        "last_sync_status": "success",
        "next_sync_time": "2026-02-18T12:30:00Z"
      },
      "api_quota": {
        "used": 450,
        "limit": 1000,
        "reset_time": "2026-02-19T00:00:00Z"
      }
    }
  ]
}
```

#### 5.4.2 连接新店铺
**端点**：`POST /api/v1/shops`
**请求**：
```json
{
  "platform": "ozon",
  "name": "我的Ozon店铺",
  "api_credentials": {
    "client_id": "your_client_id",
    "api_key": "your_api_key"
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "id": "shop_123",
    "name": "我的Ozon店铺",
    "platform": "ozon",
    "status": "connected",
    "initial_sync_started": true
  }
}
```

### 5.5 商品API

#### 5.5.1 获取商品列表
**端点**：`GET /api/v1/products`
**查询参数**：
- `platform`：平台过滤
- `shop_id`：店铺过滤
- `status`：状态过滤（active, inactive, archived）
- `category_id`：品类过滤
- `q`：搜索关键词（标题、SKU、描述）
- `page`：页码
- `limit`：每页数量

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": "product_123",
      "title": "无线蓝牙耳机",
      "sku": "BT-EAR-001",
      "description": "高音质无线蓝牙耳机...",
      "main_image_url": "https://...",
      "price": 199.99,
      "currency": "CNY",
      "stock": 150,
      "status": "active",
      "platforms": [
        {
          "platform": "ozon",
          "platform_product_id": "ozon_123456",
          "platform_sku": "OZ-BT-EAR-001",
          "price": 2999,
          "currency": "RUB",
          "stock": 50,
          "status": "active"
        },
        {
          "platform": "amazon",
          "platform_product_id": "amz_B08XYZ123",
          "platform_sku": "AMZ-BT-EAR-001",
          "price": 29.99,
          "currency": "USD",
          "stock": 100,
          "status": "active"
        }
      ]
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 1250,
    "total_pages": 25
  }
}
```

#### 5.5.2 同步商品
**端点**：`POST /api/v1/products/sync`
**请求**：
```json
{
  "shop_ids": ["shop_123", "shop_456"], // 可选，空数组表示同步所有店铺
  "sync_type": "full" // 或 "incremental"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "task_id": "task_789",
    "status": "queued",
    "message": "商品同步任务已加入队列"
  }
}
```

### 5.6 订单API

#### 5.6.1 获取订单列表
**端点**：`GET /api/v1/orders`
**查询参数**：
- `platform`：平台过滤
- `shop_id`：店铺过滤
- `status`：状态过滤
- `start_date`：开始日期
- `end_date`：结束日期
- `customer_email`：客户邮箱过滤
- `page`：页码
- `limit`：每页数量

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": "order_123",
      "order_number": "OZ-20260218-001",
      "platform": "ozon",
      "shop_id": "shop_123",
      "customer": {
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "+8613800138000",
        "address": "北京市朝阳区..."
      },
      "items": [
        {
          "product_id": "product_123",
          "title": "无线蓝牙耳机",
          "sku": "BT-EAR-001",
          "quantity": 2,
          "unit_price": 199.99,
          "subtotal": 399.98
        }
      ],
      "total_amount": 399.98,
      "currency": "CNY",
      "status": "pending_shipment",
      "created_at": "2026-02-18T10:30:00Z",
      "updated_at": "2026-02-18T10:35:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 325,
    "total_pages": 7
  }
}
```

#### 5.6.2 更新订单状态
**端点**：`PUT /api/v1/orders/{order_id}/status`
**请求**：
```json
{
  "status": "shipped",
  "shipping_info": {
    "carrier": "SF Express",
    "tracking_number": "SF1234567890",
    "shipped_at": "2026-02-18T14:30:00Z"
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "order_id": "order_123",
    "new_status": "shipped",
    "updated_at": "2026-02-18T14:30:00Z"
  }
}
```

### 5.7 库存API

#### 5.7.1 获取库存列表
**端点**：`GET /api/v1/inventory`
**查询参数**：
- `product_id`：商品ID过滤
- `warehouse_id`：仓库ID过滤
- `low_stock`：是否只显示低库存商品（true/false）
- `page`：页码
- `limit`：每页数量

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "product_id": "product_123",
      "product_title": "无线蓝牙耳机",
      "product_sku": "BT-EAR-001",
      "warehouses": [
        {
          "warehouse_id": "warehouse_1",
          "warehouse_name": "北京仓库",
          "quantity": 50,
          "reserved_quantity": 5,
          "available_quantity": 45,
          "safety_stock": 20,
          "last_updated": "2026-02-18T10:30:00Z"
        },
        {
          "warehouse_id": "warehouse_2",
          "warehouse_name": "上海仓库",
          "quantity": 100,
          "reserved_quantity": 10,
          "available_quantity": 90,
          "safety_stock": 30,
          "last_updated": "2026-02-18T10:30:00Z"
        }
      ],
      "total_quantity": 150,
      "total_reserved": 15,
      "total_available": 135,
      "is_low_stock": false
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 245,
    "total_pages": 5
  }
}
```

#### 5.7.2 调整库存
**端点**：`POST /api/v1/inventory/adjust`
**请求**：
```json
{
  "product_id": "product_123",
  "warehouse_id": "warehouse_1",
  "adjustment_type": "physical_count", // physical_count, transfer_in, transfer_out, damage, etc.
  "quantity_change": 10,
  "reason": "月度盘点调整",
  "reference_number": "COUNT-202602-001"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "adjustment_id": "adj_789",
    "product_id": "product_123",
    "warehouse_id": "warehouse_1",
    "previous_quantity": 50,
    "new_quantity": 60,
    "adjustment_type": "physical_count",
    "adjusted_at": "2026-02-18T14:30:00Z"
  }
}
```

### 5.8 CRM API

#### 5.8.1 获取客户列表
**端点**：`GET /api/v1/customers`
**查询参数**：
- `segment`：客户分组
- `level`：客户等级（vip, important, normal）
- `q`：搜索关键词（姓名、邮箱、电话）
- `page`：页码
- `limit`：每页数量

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": "customer_123",
      "name": "张三",
      "email": "zhangsan@example.com",
      "phone": "+8613800138000",
      "level": "vip",
      "total_orders": 15,
      "total_spent": 12500.50,
      "last_order_date": "2026-02-15T10:30:00Z",
      "created_at": "2025-11-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 125,
    "total_pages": 3
  }
}
```

#### 5.8.2 添加客户沟通记录
**端点**：`POST /api/v1/customers/{customer_id}/communications`
**请求**：
```json
{
  "type": "phone", // phone, email, chat, in_person
  "direction": "outbound", // inbound, outbound
  "subject": "跟进订单状态",
  "content": "客户咨询订单OZ-20260218-001的物流状态，已告知预计明天送达",
  "follow_up_action": "明天下午再次确认送达情况",
  "follow_up_date": "2026-02-19T14:00:00Z",
  "attachments": [
    {
      "filename": "物流截图.png",
      "url": "https://..."
    }
  ]
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "communication_id": "comm_789",
    "customer_id": "customer_123",
    "type": "phone",
    "content": "客户咨询订单OZ-20260218-001的物流状态，已告知预计明天送达",
    "created_by": "user_123",
    "created_at": "2026-02-18T14:30:00Z"
  }
}
```

## 6. 数据库设计

### 6.1 核心表结构

#### 6.1.1 用户与团队表
```sql
-- 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    language VARCHAR(10) DEFAULT 'zh-CN',
    currency VARCHAR(3) DEFAULT 'CNY',
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 团队表
CREATE TABLE teams (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    logo_url TEXT,
    settings JSONB DEFAULT '{}',
    subscription_plan VARCHAR(20) DEFAULT 'basic',
    subscription_status VARCHAR(20) DEFAULT 'active',
    max_members INTEGER DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 团队成员表
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- super_admin, admin, operator, cs, finance, readonly
    permissions JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active', -- active, invited, inactive
    invited_by VARCHAR(36) REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id)
);

-- 用户会话表
CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.2 店铺表
```sql
-- 店铺表
CREATE TABLE shops (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL, -- ozon, amazon, shopify, etc.
    platform_shop_id VARCHAR(100), -- 平台店铺ID
    platform_shop_name VARCHAR(100), -- 平台店铺名称
    api_credentials JSONB NOT NULL, -- 加密存储API凭证
    settings JSONB DEFAULT '{}',
    sync_settings JSONB DEFAULT '{
        "product_sync_interval": 120,
        "order_sync_interval": 5,
        "inventory_sync_interval": 30,
        "sync_enabled": true
    }',
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, disconnected, error
    last_sync_time TIMESTAMPTZ,
    last_sync_status VARCHAR(20), -- success, error, partial
    api_quota_used INTEGER DEFAULT 0,
    api_quota_limit INTEGER,
    api_quota_reset_time TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 店铺同步日志表
CREATE TABLE shop_sync_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id VARCHAR(36) NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    sync_type VARCHAR(20) NOT NULL, -- product, order, inventory, full
    sync_mode VARCHAR(20) NOT NULL, -- manual, scheduled, realtime
    status VARCHAR(20) NOT NULL, -- queued, running, success, error, partial
    items_total INTEGER DEFAULT 0,
    items_processed INTEGER DEFAULT 0,
    items_succeeded INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.3 商品表
```sql
-- 商品主表
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    master_sku VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    main_image_url TEXT,
    images JSONB DEFAULT '[]',
    category_id VARCHAR(36),
    brand VARCHAR(100),
    weight DECIMAL(10, 2),
    dimensions JSONB, -- {length, width, height, unit}
    attributes JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, archived
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 商品变体表
CREATE TABLE product_variants (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL,
    variant_attributes JSONB DEFAULT '{}', -- {color: "red", size: "M"}
    price DECIMAL(10, 2),
    compare_at_price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    barcode VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, sku)
);

-- 平台商品表（多平台映射）
CREATE TABLE platform_products (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    shop_id VARCHAR(36) NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    platform_product_id VARCHAR(100) NOT NULL,
    platform_sku VARCHAR(100),
    platform_title VARCHAR(255),
    platform_description TEXT,
    platform_price DECIMAL(10, 2),
    platform_currency VARCHAR(3),
    platform_stock INTEGER DEFAULT 0,
    platform_status VARCHAR(50),
    platform_url TEXT,
    last_synced_at TIMESTAMPTZ,
    sync_status VARCHAR(20) DEFAULT 'synced', -- synced, pending, error
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shop_id, platform_product_id)
);

-- 商品价格历史表
CREATE TABLE product_price_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    shop_id VARCHAR(36) REFERENCES shops(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    change_type VARCHAR(20), -- manual, sync, bulk_update
    changed_by VARCHAR(36) REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.4 订单表
```sql
-- 订单主表
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    shop_id VARCHAR(36) NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    platform_order_id VARCHAR(100) NOT NULL,
    order_number VARCHAR(100) NOT NULL,
    customer_id VARCHAR(36) REFERENCES customers(id),
    customer_name VARCHAR(100),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    shipping_address JSONB NOT NULL,
    billing_address JSONB,
    currency VARCHAR(3) NOT NULL,
    subtotal_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    shipping_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, refunded, partially_refunded
    payment_method VARCHAR(50),
    payment_transaction_id VARCHAR(100),
    fulfillment_status VARCHAR(20) DEFAULT 'unfulfilled', -- unfulfilled, fulfilled, partially_fulfilled
    shipping_carrier VARCHAR(100),
    shipping_tracking_number VARCHAR(100),
    shipped_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, processing, shipped, delivered, cancelled, refunded
    platform_created_at TIMESTAMPTZ,
    platform_updated_at TIMESTAMPTZ,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shop_id, platform_order_id)
);

-- 订单商品表
CREATE TABLE order_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(36) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id),
    variant_id VARCHAR(36) REFERENCES product_variants(id),
    platform_product_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 订单状态历史表
CREATE TABLE order_status_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(36) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    substatus VARCHAR(50),
    notes TEXT,
    changed_by VARCHAR(36) REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.5 库存表
```sql
-- 仓库表
CREATE TABLE warehouses (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL,
    type VARCHAR(20) DEFAULT 'physical', -- physical, virtual, supplier
    address JSONB,
    contact_info JSONB,
    capacity INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, code)
);

-- 库存表
CREATE TABLE inventory (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    warehouse_id VARCHAR(36) NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    safety_stock INTEGER DEFAULT 0,
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    last_counted_at TIMESTAMPTZ,
    last_updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, variant_id, warehouse_id)
);

-- 库存变动表
CREATE TABLE inventory_transactions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    warehouse_id VARCHAR(36) NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL, -- purchase, sale, adjustment, transfer_in, transfer_out, return, damage
    quantity_change INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reference_type VARCHAR(50), -- order, purchase_order, adjustment, etc.
    reference_id VARCHAR(36),
    notes TEXT,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 库存预警表
CREATE TABLE inventory_alerts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    warehouse_id VARCHAR(36) REFERENCES warehouses(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL, -- low_stock, out_of_stock, over_stock
    threshold INTEGER,
    current_quantity INTEGER NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(36) REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.6 CRM表
```sql
-- 客户表
CREATE TABLE customers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(100),
    shipping_address JSONB,
    billing_address JSONB,
    customer_type VARCHAR(20) DEFAULT 'retail', -- retail, wholesale, distributor
    level VARCHAR(20) DEFAULT 'normal', -- vip, important, normal
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    first_order_date TIMESTAMPTZ,
    last_order_date TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, email)
);

-- 客户沟通记录表
CREATE TABLE customer_communications (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    customer_id VARCHAR(36) NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- phone, email, chat, in_person, ticket
    direction VARCHAR(20) NOT NULL, -- inbound, outbound
    subject VARCHAR(255),
    content TEXT NOT NULL,
    sender_id VARCHAR(36) REFERENCES users(id),
    recipient_email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed', -- pending, in_progress, completed, cancelled
    follow_up_action TEXT,
    follow_up_date TIMESTAMPTZ,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 客户分组表
CREATE TABLE customer_segments (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rules JSONB NOT NULL, -- 客户筛选规则
    customer_count INTEGER DEFAULT 0,
    is_dynamic BOOLEAN DEFAULT TRUE, -- 动态分组自动更新
    is_default BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 索引设计

#### 6.2.1 关键查询索引
```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team_status ON users(team_id, status);
CREATE INDEX idx_users_last_login ON users(last_login_at DESC);

-- 店铺表索引
CREATE INDEX idx_shops_team_platform ON shops(team_id, platform);
CREATE INDEX idx_shops_status ON shops(status);
CREATE INDEX idx_shops_last_sync ON shops(last_sync_time DESC);

-- 商品表索引
CREATE INDEX idx_products_team_sku ON products(team_id, master_sku);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at DESC);

-- 平台商品表索引
CREATE INDEX idx_platform_products_shop_product ON platform_products(shop_id, product_id);
CREATE INDEX idx_platform_products_platform_id ON platform_products(platform_product_id);

-- 订单表索引
CREATE INDEX idx_orders_team_shop ON orders(team_id, shop_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
CREATE INDEX idx_orders_platform_order_id ON orders(platform_order_id);

-- 库存表索引
CREATE INDEX idx_inventory_product_warehouse ON inventory(product_id, warehouse_id);
CREATE INDEX idx_inventory_available_quantity ON inventory(available_quantity);
CREATE INDEX idx_inventory_low_stock ON inventory(team_id) WHERE available_quantity <= safety_stock;

-- 客户表索引
CREATE INDEX idx_customers_team_email ON customers(team_id, email);
CREATE INDEX idx_customers_level ON customers(level);
CREATE INDEX idx_customers_last_order ON customers(last_order_date DESC);
```

#### 6.2.2 复合索引
```sql
-- 订单状态和时间复合索引
CREATE INDEX idx_orders_status_created_at ON orders(status, created_at DESC);

-- 商品搜索复合索引
CREATE INDEX idx_products_search ON products(team_id, status, title, master_sku);

-- 库存预警复合索引
CREATE INDEX idx_inventory_alerts_unresolved ON inventory_alerts(team_id, resolved, triggered_at DESC) WHERE resolved = FALSE;
```

### 6.3 分区策略

#### 6.3.1 订单表按月分区
```sql
-- 创建订单主表（分区表）
CREATE TABLE orders_partitioned (
    -- 列定义同orders表
    CHECK (created_at >= DATE '2026-01-01' AND created_at < DATE '2026-02-01')
) INHERITS (orders);

-- 创建每月分区
CREATE TABLE orders_2026_01 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE orders_2026_02 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- 创建索引
CREATE INDEX idx_orders_2026_01_created_at ON orders_2026_01(created_at);
CREATE INDEX idx_orders_2026_01_status ON orders_2026_01(status);
```

#### 6.3.2 库存变动表按团队分区
```sql
-- 按团队ID哈希分区
CREATE TABLE inventory_transactions_partitioned (
    -- 列定义同inventory_transactions表
    CHECK (team_id % 10 = 0)
) INHERITS (inventory_transactions);

-- 创建10个分区
CREATE TABLE inventory_transactions_p0 PARTITION OF inventory_transactions_partitioned
    FOR VALUES WITH (MODULUS 10, REMAINDER 0);
-- ... 创建p1到p9分区
```

### 6.4 数据保留策略

#### 6.4.1 数据归档
- **活跃数据**：最近12个月的数据保持在线
- **归档数据**：12-36个月的数据归档到冷存储
- **历史数据**：超过36个月的数据可删除或永久归档

#### 6.4.2 自动清理任务
```sql
-- 清理旧的同步日志（保留30天）
DELETE FROM shop_sync_logs 
WHERE completed_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- 清理旧的会话记录（保留7天）
DELETE FROM user_sessions 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';

-- 归档旧的订单（12个月前的订单）
INSERT INTO orders_archive 
SELECT * FROM orders 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '12 months';

DELETE FROM orders 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '12 months';
```

## 7. 集成设计

### 7.1 电商平台集成

#### 7.1.1 Ozon集成
**技术栈**：python-ozon-api库，Ozon Seller API v2
**认证方式**：API Key认证
**核心接口**：
1. **商品同步**：
   - `GET /v2/product/list` - 获取商品列表
   - `POST /v2/product/import` - 更新商品信息
   - `POST /v2/product/stock` - 更新库存
   
2. **订单同步**：
   - `GET /v2/posting/fbo/list` - 获取FBO订单列表
   - `GET /v2/posting/fbs/list` - 获取FBS订单列表
   - `POST /v2/posting/fbs/ship` - 发货操作
   
3. **库存同步**：
   - `POST /v1/product/stock` - 更新库存
   - `GET /v1/product/stock` - 获取库存

**同步策略**：
- 商品同步：每2小时增量同步，每天凌晨全量同步
- 订单同步：每5分钟同步新订单，实时同步状态变更
- 库存同步：每30分钟同步库存变化

#### 7.1.2 Amazon集成
**技术栈**：亚马逊SP-API Python SDK，OAuth 2.0
**认证方式**：LWA (Login with Amazon) OAuth 2.0
**核心接口**：
1. **商品同步**：
   - `GET /catalog/v0/items` - 获取商品目录
   - `GET /catalog/v0/categories` - 获取商品分类
   
2. **订单同步**：
   - `GET /orders/v0/orders` - 获取订单列表
   - `GET /orders/v0/orders/{orderId}` - 获取订单详情
   - `POST /orders/v0/orders/{orderId}/shipment` - 创建发货
   
3. **库存同步**：
   - `POST /fulfillment-inbound/v0/plans` - 库存计划
   - `GET /inventory/v0/summaries` - 库存摘要

**同步策略**：
- 遵循亚马逊API调用配额限制
- 使用报告机制批量获取数据
- 增量同步为主，减少API调用

#### 7.1.3 Shopify集成
**技术栈**：Shopify Python API库，GraphQL Admin API
**认证方式**：OAuth 2.0，支持Webhook
**核心接口**：
1. **商品同步**：
   - `GET /admin/api/2024-01/products.json` - 获取商品列表
   - `PUT /admin/api/2024-01/products/{id}.json` - 更新商品
   
2. **订单同步**：
   - `GET /admin/api/2024-01/orders.json` - 获取订单列表
   - `POST /admin/api/2024-01/orders/{id}/fulfillments.json` - 创建履约
   
3. **库存同步**：
   - `GET /admin/api/2024-01/inventory_levels.json` - 获取库存水平
   - `POST /admin/api/2024-01/inventory_levels/set.json` - 设置库存

**同步策略**：
- 使用Webhook实时接收订单创建和更新
- 商品和库存定时同步
- GraphQL批量查询优化性能

### 7.2 适配器设计模式

#### 7.2.1 适配器接口
```python
class PlatformAdapter(ABC):
    """电商平台适配器抽象基类"""
    
    @abstractmethod
    async def connect(self, credentials: dict) -> bool:
        """连接平台，验证凭证"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    async def sync_products(self, since: datetime = None) -> List[Product]:
        """同步商品"""
        pass
    
    @abstractmethod
    async def sync_orders(self, since: datetime = None) -> List[Order]:
        """同步订单"""
        pass
    
    @abstractmethod
    async def sync_inventory(self, product_ids: List[str] = None) -> List[Inventory]:
        """同步库存"""
        pass
    
    @abstractmethod
    async def update_product(self, product: Product) -> bool:
        """更新商品到平台"""
        pass
    
    @abstractmethod
    async def update_inventory(self, inventory: Inventory) -> bool:
        """更新库存到平台"""
        pass
    
    @abstractmethod
    async def create_fulfillment(self, order: Order, tracking_info: dict) -> bool:
        """创建发货"""
        pass
    
    @abstractmethod
    async def get_api_quota(self) -> dict:
        """获取API配额信息"""
        pass
```

#### 7.2.2 Ozon适配器实现
```python
class OzonAdapter(PlatformAdapter):
    """Ozon平台适配器"""
    
    def __init__(self, shop: Shop):
        self.shop = shop
        self.client = OzonClient(
            client_id=shop.api_credentials['client_id'],
            api_key=shop.api_credentials['api_key']
        )
        self.last_sync_time = None
    
    async def connect(self, credentials: dict) -> bool:
        try:
            # 测试API连接
            response = await self.client.get_warehouses()
            return True
        except Exception as e:
            logger.error(f"Ozon连接失败: {e}")
            return False
    
    async def sync_products(self, since: datetime = None) -> List[Product]:
        products = []
        limit = 100
        offset = 0
        
        while True:
            try:
                response = await self.client.get_products(limit=limit, offset=offset)
                if not response.get('items'):
                    break
                    
                for item in response['items']:
                    product = self._map_to_product(item)
                    products.append(product)
                
                offset += limit
            except Exception as e:
                logger.error(f"同步商品失败: {e}")
                break
        
        self.last_sync_time = datetime.now()
        return products
    
    async def sync_orders(self, since: datetime = None) -> List[Order]:
        orders = []
        limit = 100
        offset = 0
        
        # 构建查询参数
        params = {
            'limit': limit,
            'offset': offset
        }
        if since:
            params['since'] = since.isoformat()
        
        while True:
            try:
                response = await self.client.get_orders(**params)
                if not response.get('orders'):
                    break
                    
                for item in response['orders']:
                    order = self._map_to_order(item)
                    orders.append(order)
                
                offset += limit
                params['offset'] = offset
            except Exception as e:
                logger.error(f"同步订单失败: {e}")
                break
        
        return orders
    
    def _map_to_product(self, ozon_product: dict) -> Product:
        """将Ozon商品映射到系统商品模型"""
        return Product(
            platform_product_id=ozon_product['product_id'],
            sku=ozon_product['offer_id'],
            title=ozon_product['name'],
            description=ozon_product.get('description', ''),
            price=Decimal(ozon_product['price']),
            stock=ozon_product.get('stock', 0),
            images=ozon_product.get('images', []),
            attributes=ozon_product.get('attributes', {}),
            status='active' if ozon_product.get('visible', True) else 'inactive'
        )
    
    def _map_to_order(self, ozon_order: dict) -> Order:
        """将Ozon订单映射到系统订单模型"""
        return Order(
            platform_order_id=ozon_order['order_id'],
            order_number=ozon_order['order_number'],
            customer_name=ozon_order.get('customer_name', ''),
            customer_email=ozon_order.get('customer_email', ''),
            customer_phone=ozon_order.get('customer_phone', ''),
            shipping_address={
                'city': ozon_order.get('city', ''),
                'address': ozon_order.get('address', ''),
                'postal_code': ozon_order.get('postal_code', '')
            },
            total_amount=Decimal(ozon_order.get('total_amount', 0)),
            currency=ozon_order.get('currency', 'RUB'),
            status=self._map_order_status(ozon_order.get('status', '')),
            platform_created_at=parse_datetime(ozon_order.get('created_at')),
            items=[
                OrderItem(
                    platform_product_id=item['product_id'],
                    title=item['name'],
                    sku=item['offer_id'],
                    quantity=item['quantity'],
                    unit_price=Decimal(item['price']),
                    subtotal=Decimal(item['quantity']) * Decimal(item['price'])
                )
                for item in ozon_order.get('items', [])
            ]
        )
    
    def _map_order_status(self, ozon_status: str) -> str:
        """映射Ozon订单状态到系统状态"""
        status_map = {
            'awaiting_registration': 'pending',
            'awaiting_packaging': 'confirmed',
            'awaiting_deliver': 'processing',
            'arbitration': 'cancelled',
            'delivering': 'shipped',
            'delivered': 'delivered',
            'cancelled': 'cancelled'
        }
        return status_map.get(ozon_status, 'pending')
```

### 7.3 物流集成

#### 7.3.1 快递鸟集成
**技术栈**：快递鸟API，支持100+物流公司
**核心功能**：
1. **物流查询**：实时查询物流轨迹
2. **电子面单**：生成电子面单，打印发货标签
3. **物流订阅**：物流状态变更实时推送

**集成方式**：
```python
class KuaidiBirdService:
    """快递鸟物流服务"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api.kuaidi100.com"
    
    async def query_tracking(self, tracking_number: str, carrier: str) -> dict:
        """查询物流轨迹"""
        params = {
            'com': carrier,
            'num': tracking_number,
            'resultv2': 1
        }
        
        # 生成签名
        sign = hashlib.md5(
            f'{tracking_number}{carrier}{self.app_key}'.encode()
        ).hexdigest().upper()
        
        response = await self._request('GET', '/query', params=params)
        return response
    
    async def create_eorder(self, order: Order, carrier: str, template_id: str) -> dict:
        """创建电子面单"""
        data = {
            'OrderCode': order.order_number,
            'ShipperCode': carrier,
            'TemplateSize': '100*150',
            'Sender': {
                'Name': order.shipping_address.get('sender_name', ''),
                'Tel': order.shipping_address.get('sender_phone', ''),
                'Address': order.shipping_address.get('sender_address', '')
            },
            'Receiver': {
                'Name': order.customer_name,
                'Tel': order.customer_phone,
                'Address': order.shipping_address.get('address', '')
            },
            'Commodity': [
                {
                    'GoodsName': item.title,
                    'GoodsQuantity': item.quantity
                }
                for item in order.items
            ]
        }
        
        response = await self._request('POST', '/eorderapi.do', data=data)
        return response
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送HTTP请求"""
        url = f'{self.base_url}{endpoint}'
        
        async with httpx.AsyncClient() as client:
            if method == 'GET':
                response = await client.get(url, **kwargs)
            else:
                response = await client.post(url, **kwargs)
            
            response.raise_for_status()
            return response.json()
```

## 8. 非功能性需求

### 8.1 性能需求

#### 8.1.1 响应时间
- **页面加载**：
  - 普通页面加载时间 < 3秒
  - 复杂页面（商品列表、订单列表）加载时间 < 5秒
  - 初始应用加载时间 < 8秒（包含资源下载）
  
- **API响应**：
  - 普通API操作响应时间 < 1秒（p95）
  - 复杂查询响应时间 < 3秒（p95）
  - 批量操作支持异步处理，提供任务ID和状态查询
  
- **数据同步**：
  - 商品同步：1000个商品在5分钟内完成同步
  - 订单同步：新订单在5分钟内同步到系统
  - 库存同步：库存变化在1分钟内同步到平台

#### 8.1.2 并发性能
- **并发用户**：支持200个并发用户同时操作
- **API吞吐量**：支持1000个请求/秒
- **数据库连接**：支持500个并发数据库连接
- **同步任务**：支持10个店铺同时同步

#### 8.1.3 数据容量
- **商品数据**：支持百万级商品数据存储和查询
- **订单数据**：支持千万级订单数据存储和查询
- **库存数据**：支持实时库存更新，每天百万级库存变动
- **客户数据**：支持百万级客户数据管理

### 8.2 可用性需求

#### 8.2.1 服务可用性
- **整体可用性**：99.5% SLA（每月停机时间不超过3.6小时）
- **核心服务可用性**：99.9% SLA（商品、订单、库存服务）
- **数据可用性**：99.99% 数据持久性
- **备份恢复**：RTO < 4小时，RPO < 15分钟

#### 8.2.2 故障恢复
- **自动故障转移**：数据库主从自动切换
- **服务自愈**：服务异常自动重启
- **降级策略**：非核心功能降级，保证核心功能可用
- **限流熔断**：API限流和熔断机制，防止级联故障

### 8.3 安全性需求

#### 8.3.1 数据安全
- **传输加密**：全站HTTPS，TLS 1.3
- **存储加密**：敏感数据（密码、API密钥）加密存储
- **数据隔离**：多租户数据完全隔离
- **访问控制**：基于角色的细粒度权限控制

#### 8.3.2 应用安全
- **输入验证**：所有用户输入验证和清理
- **SQL注入防护**：使用ORM参数化查询
- **XSS防护**：输出编码，CSP策略
- **CSRF防护**：CSRF Token验证
- **文件上传安全**：文件类型验证，病毒扫描

#### 8.3.3 审计与合规
- **操作审计**：所有敏感操作记录审计日志
- **登录审计**：记录所有登录尝试
- **数据变更审计**：关键数据变更记录
- **合规性**：符合GDPR和中国网络安全法

### 8.4 可扩展性需求

#### 8.4.1 水平扩展
- **无状态服务**：所有业务服务设计为无状态
- **数据库分片**：支持按租户ID分片
- **缓存分层**：本地缓存 + Redis集群 + CDN
- **异步处理**：耗时操作异步化，避免阻塞

#### 8.4.2 垂直扩展
- **微服务拆分**：支持按业务域拆分为独立服务
- **独立部署**：关键服务支持独立部署和扩展
- **资源隔离**：不同租户资源隔离，避免互相影响

### 8.5 可维护性需求

#### 8.5.1 代码质量
- **代码规范**：遵循PEP 8 Python代码规范
- **类型提示**：全面使用类型提示
- **代码覆盖率**：单元测试覆盖率 > 80%
- **代码审查**：所有代码变更需要代码审查

#### 8.5.2 文档质量
- **API文档**：自动生成OpenAPI文档，保持最新
- **技术文档**：架构设计、部署指南完整
- **用户文档**：用户手册、操作指南完整
- **变更日志**：记录所有版本变更

## 9. 测试策略

### 9.1 测试类型

#### 9.1.1 单元测试
- **测试范围**：所有业务逻辑、工具函数、数据模型
- **测试框架**：pytest
- **覆盖率目标**：> 80%
- **测试位置**：`tests/unit/` 目录

#### 9.1.2 集成测试
- **测试范围**：API接口、数据库操作、外部服务集成
- **测试框架**：pytest + FastAPI TestClient
- **测试数据库**：使用测试数据库，每个测试用例独立事务
- **测试位置**：`tests/integration/` 目录

#### 9.1.3 端到端测试
- **测试范围**：完整业务流程，用户操作流
- **测试框架**：Playwright（前端） + pytest（后端）
- **测试场景**：关键用户路径（注册、连接店铺、同步商品、处理订单）
- **测试位置**：`tests/e2e/` 目录

#### 9.1.4 性能测试
- **测试范围**：API性能、并发性能、数据同步性能
- **测试工具**：locust、k6
- **测试场景**：高并发商品查询、批量订单处理、数据同步压力测试
- **性能指标**：响应时间、吞吐量、错误率、资源使用率

### 9.2 测试数据管理

#### 9.2.1 测试数据策略
- **隔离环境**：测试使用独立的数据库和Redis实例
- **数据工厂**：使用factory_boy创建测试数据
- **数据清理**：每个测试用例运行后清理测试数据
- **数据快照**：关键测试数据保存为快照，用于回归测试

#### 9.2.2 测试数据示例
```python
# 测试数据工厂示例
class ShopFactory(factory.Factory):
    class Meta:
        model = Shop
    
    id = factory.Faker('uuid4')
    name = factory.Faker('company')
    platform = 'ozon'
    status = 'active'
    api_credentials = {
        'client_id': 'test_client_id',
        'api_key': 'test_api_key'
    }
    sync_settings = {
        'product_sync_interval': 120,
        'order_sync_interval': 5
    }
    created_at = factory.Faker('date_time_this_year')

# 测试用例示例
def test_shop_sync_products():
    # 创建测试店铺
    shop = ShopFactory()
    
    # 模拟Ozon API响应
    mock_products = [
        {
            'product_id': '123',
            'offer_id': 'SKU-001',
            'name': '测试商品',
            'price': '1999.99',
            'stock': 100
        }
    ]
    
    # 执行同步
    result = shop.sync_products()
    
    # 验证结果
    assert len(result) == 1
    assert result[0].sku == 'SKU-001'
    assert result[0].price == Decimal('1999.99')
```

### 9.3 自动化测试流水线

#### 9.3.1 CI/CD流水线
```yaml
# GitHub Actions配置示例
name: Test Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

#### 9.3.2 测试报告
- **单元测试报告**：pytest-html生成HTML报告
- **覆盖率报告**：coverage.py生成覆盖率报告
- **性能测试报告**：locust生成性能测试报告
- **测试仪表板**：集成到监控系统，实时显示测试状态

## 10. 部署与运维

### 10.1 开发环境部署

#### 10.1.1 本地开发环境
**依赖软件**：
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+（前端开发）
- Docker Desktop（可选）

**本地启动脚本**：
```bash
# 克隆项目
git clone https://github.com/your-org/icross.git
cd icross

# 安装后端依赖
pip install -e ".[dev]"

# 安装前端依赖
cd frontend
npm install

# 启动数据库和Redis
docker-compose up -d db redis

# 运行数据库迁移
alembic upgrade head

# 启动后端开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端开发服务器（另一个终端）
cd frontend
npm run dev
```

#### 10.1.2 Docker开发环境
**docker-compose.yml**：
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: icross
      POSTGRES_PASSWORD: icross123
      POSTGRES_DB: icross_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://icross:icross123@db:5432/icross_dev
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: development
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 10.2 生产环境部署

#### 10.2.1 Kubernetes部署
**部署架构**：
```
Load Balancer (AWS ALB/NLB)
      |
Ingress Controller (Traefik)
      |
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ 前端服务 │ │ API网关  │ │ 用户服务 │
  │ (3副本)  │ │ (2副本)  │ │ (2副本)  │
  └─────────┘ └─────────┘ └─────────┘
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ 商品服务 │ │ 订单服务 │ │ 库存服务 │
  │ (3副本)  │ │ (3副本)  │ │ (2副本)  │
  └─────────┘ └─────────┘ └─────────┘
      |
Redis Cluster (3主3从)
      |
PostgreSQL HA (主从复制)
```

#### 10.2.2 Kubernetes配置
**backend-deployment.yaml**：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: icross
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
      tier: api
  template:
    metadata:
      labels:
        app: backend
        tier: api
    spec:
      containers:
      - name: backend
        image: icross/backend:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-cluster.icross.svc.cluster.local:6379"
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
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
    tier: api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### 10.2.3 数据库部署
**postgres-ha.yaml**：
```yaml
# PostgreSQL HA部署
apiVersion: postgres-operator.crunchydata.com/v1beta1
kind: PostgresCluster
metadata:
  name: icross-db
  namespace: icross
spec:
  image: registry.developers.crunchydata.com/crunchydata/crunchy-postgres:centos8-15.2-1
  postgresVersion: 15
  instances:
    - name: instance1
      replicas: 2
      dataVolumeClaimSpec:
        accessModes:
        - "ReadWriteOnce"
        resources:
          requests:
            storage: 100Gi
      resources:
        requests:
          memory: 2Gi
          cpu: 1
  backups:
    pgbackrest:
      image: registry.developers.crunchydata.com/crunchydata/crunchy-pgbackrest:centos8-2.44-1
      repos:
      - name: repo1
        volume:
          volumeClaimSpec:
            accessModes:
            - "ReadWriteOnce"
            resources:
              requests:
                storage: 50Gi
```

### 10.3 监控与告警

#### 10.3.1 监控指标
**应用指标**：
- API请求率、响应时间、错误率
- 数据库连接数、查询性能、锁等待
- Redis内存使用、命中率、连接数
- 任务队列长度、处理速度、失败率

**业务指标**：
- 店铺连接成功率
- 数据同步准确率
- 订单处理延迟
- 库存同步延迟

**基础设施指标**：
- CPU使用率、内存使用率、磁盘使用率
- 网络流量、连接数
- 容器资源使用

#### 10.3.2 告警规则
**关键告警**（P0）：
- 数据库不可用 > 5分钟
- Redis不可用 > 5分钟
- API错误率 > 5% 持续5分钟
- 订单同步延迟 > 15分钟

**重要告警**（P1）：
- 店铺连接失败 > 3次
- 商品同步失败 > 10%
- 库存同步延迟 > 30分钟
- 磁盘使用率 > 85%

**警告告警**（P2）：
- API响应时间 > 3秒（p95）
- 数据库连接数 > 80%
- Redis内存使用 > 80%
- 任务队列积压 > 1000

#### 10.3.3 监控部署
**Prometheus配置**：
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend.icross.svc.cluster.local:8000']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter.icross.svc.cluster.local:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter.icross.svc.cluster.local:9121']
```

**Grafana仪表板**：
- **应用概览**：API性能、错误率、请求量
- **数据库监控**：查询性能、连接数、锁等待
- **Redis监控**：内存使用、命中率、命令统计
- **业务监控**：店铺状态、同步性能、订单处理
- **基础设施**：CPU、内存、磁盘、网络

### 10.4 备份与恢复

#### 10.4.1 备份策略
**数据库备份**：
- **全量备份**：每天凌晨2点执行全量备份
- **增量备份**：每15分钟WAL日志备份
- **保留策略**：全量备份保留30天，WAL备份保留7天
- **备份存储**：S3兼容对象存储，跨区域复制

**文件备份**：
- **商品图片**：MinIO版本控制，自动复制到备份存储
- **日志文件**：ELK集群，日志保留180天
- **配置文件**：Git版本控制，配置即代码

**备份验证**：
- 每周执行备份恢复测试
- 验证备份文件完整性和可恢复性
- 记录备份测试结果和问题

#### 10.4.2 恢复流程
**数据库恢复流程**：
1. 确定恢复点时间（RPO）
2. 从备份存储获取全量备份和WAL日志
3. 在备用环境恢复数据库
4. 验证数据完整性和一致性
5. 切换流量到恢复后的数据库

**灾难恢复流程**：
1. 启动灾难恢复预案
2. 在备用区域启动基础设施
3. 恢复数据库和文件存储
4. 恢复应用程序和服务
5. 更新DNS记录，切换流量
6. 验证业务功能正常

### 10.5 运维自动化

#### 10.5.1 日常运维
**健康检查**：
```bash
# 健康检查脚本
#!/bin/bash

# 检查API健康
curl -f http://localhost:8000/health || exit 1

# 检查数据库连接
pg_isready -h localhost -p 5432 || exit 1

# 检查Redis连接
redis-cli ping | grep -q PONG || exit 1

echo "所有服务健康"
```

**日志收集**：
```yaml
# Fluentd配置
<source>
  @type tail
  path /var/log/backend/*.log
  pos_file /var/log/fluentd/backend.log.pos
  tag backend.*
  format json
</source>

<match backend.*>
  @type elasticsearch
  host elasticsearch.icross.svc.cluster.local
  port 9200
  index_name backend-${tag}
</match>
```

#### 10.5.2 自动化脚本
**数据清理脚本**：
```python
#!/usr/bin/env python3
"""
数据清理脚本：清理过期数据
"""

import asyncio
from datetime import datetime, timedelta
from app.core.database import async_session
from app.models import UserSession, ShopSyncLog

async def cleanup_old_data():
    """清理过期数据"""
    async with async_session() as session:
        # 清理30天前的同步日志
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await session.execute(
            delete(ShopSyncLog)
            .where(ShopSyncLog.completed_at < thirty_days_ago)
        )
        deleted_logs = result.rowcount
        
        # 清理7天前的用户会话
        seven_days_ago = datetime.now() - timedelta(days=7)
        result = await session.execute(
            delete(UserSession)
            .where(UserSession.created_at < seven_days_ago)
        )
        deleted_sessions = result.rowcount
        
        await session.commit()
        
        print(f"清理完成：同步日志 {deleted_logs} 条，用户会话 {deleted_sessions} 条")

if __name__ == "__main__":
    asyncio.run(cleanup_old_data())
```

**数据迁移脚本**：
```python
#!/usr/bin/env python3
"""
数据迁移脚本：执行数据库迁移
"""

import subprocess
import sys

def run_migration():
    """运行数据库迁移"""
    print("开始数据库迁移...")
    
    # 生成迁移脚本
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "数据库变更"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"生成迁移脚本失败: {result.stderr}")
        sys.exit(1)
    
    print("迁移脚本生成成功")
    
    # 应用迁移
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"应用迁移失败: {result.stderr}")
        sys.exit(1)
    
    print("数据库迁移完成")

if __name__ == "__main__":
    run_migration()
```

## 11. 开发路线图

### 11.1 v1.0开发阶段（12-16周）

#### 第1-2周：项目初始化和基础架构
- **基础设施搭建**：
  - 开发环境配置（Docker、数据库、Redis）
  - CI/CD流水线配置（GitHub Actions）
  - 代码规范和质量检查配置（black、isort、ruff、mypy）
  
- **基础框架搭建**：
  - FastAPI项目结构搭建
  - 数据库连接池配置
  - Redis客户端配置
  - 日志和错误处理配置
  
- **核心模型定义**：
  - 用户、团队、权限模型
  - 基础数据模型设计
  - Alembic迁移配置

#### 第3-4周：用户与权限系统
- **用户认证**：
  - 用户注册、登录、密码重置
  - JWT令牌认证和刷新
  - 会话管理和安全控制
  
- **团队管理**：
  - 团队创建和管理
  - 团队成员邀请和权限分配
  - 多租户数据隔离实现
  
- **权限系统**：
  - RBAC权限模型实现
  - 权限检查和验证
  - 操作审计日志

#### 第5-6周：店铺集成（Ozon优先）
- **Ozon集成**：
  - Ozon API客户端实现
  - API认证和连接测试
  - 店铺连接和管理界面
  
- **数据同步框架**：
  - 通用同步框架设计
  - 任务队列和异步处理
  - 同步状态监控和错误处理
  
- **店铺管理界面**：
  - 店铺列表和详情
  - 连接状态显示
  - API配置管理

#### 第7-8周：商品管理
- **商品同步**：
  - Ozon商品同步实现
  - 增量同步和全量同步
  - 同步冲突处理
  
- **商品管理界面**：
  - 商品列表和搜索
  - 商品详情和编辑
  - 批量操作支持
  
- **商品数据模型**：
  - 统一商品模型
  - 多平台商品映射
  - 商品变体支持

#### 第9-10周：订单管理
- **订单同步**：
  - Ozon订单同步实现
  - 实时订单获取
  - 订单状态同步
  
- **订单处理**：
  - 订单列表和筛选
  - 订单详情和操作
  - 发货和物流管理
  
- **订单状态机**：
  - 订单状态流转规则
  - 状态变更历史
  - 异常订单处理

#### 第11-12周：库存管理
- **库存同步**：
  - Ozon库存同步实现
  - 实时库存更新
  - 库存预警机制
  
- **库存管理界面**：
  - 库存列表和视图
  - 库存调整操作
  - 库存报表和分析
  
- **仓库管理**：
  - 仓库创建和管理
  - 多仓库库存支持
  - 库存分配规则

#### 第13-14周：CRM客户管理
- **客户管理**：
  - 客户信息管理
  - 客户分组和标签
  - 客户沟通记录
  
- **客户同步**：
  - 从订单自动创建客户
  - 客户信息更新
  - 客户去重和合并
  
- **客户分析**：
  - 客户消费统计
  - 客户等级划分
  - 客户活跃度分析

#### 第15-16周：测试、优化和部署
- **测试和优化**：
  - 单元测试和集成测试
  - 性能测试和优化
  - 安全测试和加固
  
- **部署准备**：
  - 生产环境配置
  - 监控和告警配置
  - 备份和恢复方案
  
- **用户测试**：
  - 内测用户邀请
  - 用户反馈收集
  - Bug修复和优化

### 11.2 关键里程碑

#### 里程碑1：基础框架完成（第2周）
- ✅ 开发环境就绪
- ✅ CI/CD流水线运行
- ✅ 基础数据模型定义
- ✅ 用户认证框架完成

#### 里程碑2：Ozon集成完成（第6周）
- ✅ Ozon API连接成功
- ✅ 店铺管理界面完成
- ✅ 商品同步功能完成
- ✅ 同步监控和错误处理

#### 里程碑3：核心ERP功能完成（第12周）
- ✅ 商品管理完整功能
- ✅ 订单处理完整功能
- ✅ 库存管理完整功能
- ✅ 基础CRM功能完成

#### 里程碑4：v1.0发布准备（第16周）
- ✅ 完整测试通过
- ✅ 性能优化完成
- ✅ 生产环境部署
- ✅ 内测用户邀请

### 11.3 资源需求

#### 开发团队：
- **后端开发**：2人（Python、FastAPI、数据库）
- **前端开发**：1人（React、TypeScript、Ant Design）
- **DevOps**：1人（Docker、Kubernetes、监控）
- **产品经理**：1人（需求、用户测试、反馈）

#### 基础设施：
- **开发环境**：本地开发机 + Docker
- **测试环境**：AWS/GCP测试集群
- **生产环境**：AWS/GCP生产集群
- **监控工具**：Prometheus、Grafana、ELK

#### 第三方服务：
- **代码托管**：GitHub（私有仓库）
- **CI/CD**：GitHub Actions
- **代码质量**：SonarCloud（可选）
- **错误监控**：Sentry
- **文档托管**：Read the Docs（可选）

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-02-18 | 初始版本创建，v1.0详细设计 | AI Assistant |

*本文档为iCross v1.0基础平台阶段详细设计文档，将指导v1.0版本的开发工作。后续版本设计将在独立文档中提供。*