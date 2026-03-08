# iCross v3.0 AI Agent与智能运营阶段详细设计文档

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v1.0 |
| **最后更新** | 2026-02-18 |
| **对应产品版本** | iCross v3.0 |
| **阶段名称** | AI Agent与智能运营阶段 (AI Agent & Smart Operations Phase) |
| **时间周期** | v2.0后4个月 |
| **文档负责人** | 产品经理 + AI架构师 |

## 1. 概述

### 1.1 阶段目标
在v2.0基础上，构建智能化的运营操作系统，实现：
- **AI Agent引擎**：基于LangChain的智能任务执行系统，支持自然语言指令
- **工作流设计器**：可视化工作流编排，自动化复杂业务流程
- **智能运营建议**：数据驱动的运营优化建议，支持一键执行
- **高级CRM**：客户生命周期管理，营销自动化
- **移动端应用**：iOS/Android移动管理，实时业务操作

### 1.2 核心价值主张
- **智能自动化**：AI Agent自动执行复杂运营任务，解放人力资源
- **工作流编排**：可视化编排业务流程，提升运营效率300%
- **数据智能决策**：AI分析业务数据，提供可执行的优化建议
- **全渠道客户管理**：客户生命周期自动化管理，提升客户价值50%
- **移动办公**：随时随地管理业务，实时响应市场变化

### 1.3 目标用户
- **专业型卖家**：5-10人团队，月销售额 > 50万人民币，管理 > 2000个SKU
- **企业级用户**：10+人团队，多店铺多平台运营，需要高级自动化
- **运营管理者**：需要数据驱动决策和自动化流程的管理人员

### 1.4 成功指标
- AI Agent任务执行成功率 > 85%
- 运营建议采纳率 > 50%
- 月活跃用户 > 500
- ARR (年度经常性收入) > $50k
- 客户生命周期价值提升 > 30%

## 2. 功能规格

### 2.1 AI Agent引擎

#### 2.1.1 功能描述
基于LangChain框架构建的智能Agent系统，支持自然语言指令解析、工具调用、任务分解和执行。

#### 2.1.2 功能列表
1. **自然语言接口**
   - **对话式交互**：用户通过自然语言描述任务，Agent理解并执行
   - **多轮对话**：支持多轮对话澄清需求，确认细节
   - **上下文理解**：理解对话上下文，保持连贯性
   - **意图识别**：识别用户意图，映射到相应工具或工作流
   - **参数提取**：从自然语言中提取任务参数

2. **工具系统**
   - **工具注册**：系统功能封装为Agent可调用的工具
   - **工具分类**：数据查询、操作执行、分析计算、外部服务
   - **工具描述**：自然语言描述工具功能和参数
   - **权限控制**：工具调用权限控制，防止越权操作
   - **工具组合**：多个工具组合完成复杂任务

3. **任务执行引擎**
   - **任务分解**：复杂任务自动分解为子任务序列
   - **并行执行**：支持多个子任务并行执行
   - **状态监控**：实时监控任务执行状态和进度
   - **错误处理**：执行失败自动重试和错误恢复
   - **结果收集**：收集和整合任务执行结果

4. **Agent管理**
   - **Agent配置**：配置Agent行为参数和限制
   - **Agent类型**：专用Agent（销售、客服、采购、库存）
   - **Agent协作**：多个Agent协作完成复杂任务
   - **性能监控**：监控Agent执行性能和成本
   - **学习优化**：基于执行结果优化Agent策略

5. **安全与审计**
   - **权限继承**：Agent只能执行用户有权限的操作
   - **敏感操作确认**：涉及资金、重大调整需用户确认
   - **操作范围限制**：Agent不能修改系统配置、删除重要数据
   - **操作审计**：记录所有Agent操作，支持追溯
   - **安全边界**：严格的安全边界和防护机制

#### 2.1.3 技术规格
- **Agent框架**：LangChain + OpenAI Function Calling
- **工具系统**：自定义Tool类，支持异步调用
- **任务编排**：LangChain Expression Language (LCEL)
- **记忆系统**：ConversationBufferMemory + VectorStore
- **安全控制**：基于角色的工具调用权限控制

### 2.2 工作流设计器

#### 2.2.1 功能描述
可视化工作流设计工具，支持拖拽式节点编排，实现复杂业务流程自动化。

#### 2.2.2 功能列表
1. **可视化编辑器**
   - **画布界面**：无限画布，支持缩放和平移
   - **节点库**：预定义节点（触发器、动作、条件、循环）
   - **拖拽操作**：拖拽节点到画布，连接节点
   - **连线编辑**：编辑节点连接关系和条件
   - **属性面板**：编辑节点属性和参数

2. **节点类型**
   - **触发器节点**：时间触发、事件触发、API触发、手动触发
   - **动作节点**：数据操作、工具调用、消息发送、文件处理
   - **条件节点**：条件判断、分支选择、循环控制
   - **数据节点**：变量定义、数据转换、计算节点
   - **集成节点**：外部服务调用、API调用

3. **工作流逻辑**
   - **顺序执行**：节点按连接顺序执行
   - **条件分支**：根据条件执行不同分支
   - **并行执行**：多个分支并行执行
   - **循环控制**：支持for循环、while循环
   - **错误处理**：错误捕获和处理分支

4. **工作流管理**
   - **版本控制**：工作流版本管理和回滚
   - **导入导出**：工作流配置导入导出
   - **模板库**：预定义工作流模板
   - **分享协作**：工作流分享和团队协作
   - **执行历史**：工作流执行历史记录

5. **调试与监控**
   - **调试模式**：单步执行，查看变量状态
   - **执行日志**：详细执行日志，每个节点状态
   - **性能监控**：监控工作流执行性能
   - **错误诊断**：错误诊断和建议修复
   - **测试环境**：工作流测试环境，不影响生产

#### 2.2.3 技术规格
- **前端框架**：React Flow + Zustand状态管理
- **后端引擎**：Apache Airflow / Prefect 工作流引擎
- **执行器**：Celery分布式任务执行
- **存储**：PostgreSQL工作流定义存储
- **版本控制**：Git存储工作流配置

### 2.3 智能运营建议

#### 2.3.1 功能描述
基于数据分析的智能运营建议系统，自动识别业务问题和优化机会，提供可执行建议。

#### 2.3.2 功能列表
1. **建议生成引擎**
   - **问题检测**：自动检测业务问题（销售下降、库存异常、价格问题）
   - **根因分析**：分析问题根本原因
   - **建议生成**：生成具体可执行的优化建议
   - **优先级排序**：建议优先级排序（高、中、低）
   - **置信度评估**：建议置信度评估（0-100%）

2. **建议类型**
   - **价格优化**：价格调整建议，提升销量或利润
   - **库存优化**：库存调整建议，减少缺货或积压
   - **营销优化**：营销活动建议，提升转化率
   - **商品优化**：商品上架、优化、下架建议
   - **运营效率**：流程优化建议，提升运营效率

3. **建议管理**
   - **建议列表**：所有建议列表，按优先级排序
   - **建议详情**：建议详细说明、依据、预期效果
   - **建议状态**：待处理、已接受、已执行、已拒绝、已过期
   - **建议执行**：一键执行建议或跳转到相关功能
   - **执行跟踪**：跟踪建议执行情况和实际效果

4. **效果评估**
   - **效果跟踪**：跟踪建议执行后的业务指标变化
   - **ROI计算**：计算建议带来的投资回报率
   - **A/B测试**：建议A/B测试验证效果
   - **反馈收集**：收集用户对建议的反馈
   - **模型优化**：基于效果反馈优化建议模型

5. **个性化推荐**
   - **用户画像**：基于用户行为和历史构建用户画像
   - **个性化建议**：基于用户画像的个性化建议
   - **学习偏好**：学习用户偏好，推荐更相关建议
   - **时机优化**：在最佳时机推送建议
   - **渠道优化**：通过最佳渠道推送建议

#### 2.3.3 技术规格
- **分析引擎**：Python数据分析栈（pandas, scikit-learn）
- **机器学习**：分类、回归、聚类算法
- **A/B测试**：统计显著性检验
- **推荐系统**：协同过滤 + 内容推荐
- **实时计算**：流式计算业务指标

### 2.4 高级CRM系统

#### 2.4.1 功能描述
在v1.0基础CRM上，增加客户生命周期管理、营销自动化、客户价值分析等高级功能。

#### 2.4.2 功能列表
1. **客户生命周期管理**
   - **生命周期阶段**：潜在客户、新客户、活跃客户、沉默客户、流失客户
   - **阶段自动识别**：基于行为自动识别客户阶段
   - **阶段转换规则**：定义阶段转换条件和动作
   - **生命周期视图**：客户生命周期可视化
   - **阶段优化**：优化客户在不同阶段的表现

2. **营销自动化**
   - **自动化流程**：创建营销自动化流程
   - **触发条件**：基于客户行为、时间、事件触发
   - **执行动作**：发送邮件、短信、推送通知、优惠券
   - **流程设计**：可视化营销流程设计
   - **效果分析**：营销活动效果分析和优化

3. **客户细分**
   - **动态细分**：基于规则动态创建客户细分
   - **RFM分析**：最近购买时间、购买频率、购买金额分析
   - **行为细分**：基于购买行为、浏览行为细分
   - **价值细分**：基于客户价值细分（高价值、中价值、低价值）
   - **细分管理**：细分创建、编辑、删除、合并

4. **营销活动管理**
   - **活动创建**：创建营销活动，选择目标细分
   - **内容设计**：设计营销内容（邮件模板、短信模板）
   - **活动计划**：活动时间计划、预算计划
   - **活动执行**：活动执行和监控
   - **效果分析**：活动效果分析和报告

5. **客户价值分析**
   - **LTV计算**：客户生命周期价值计算
   - **获取成本**：客户获取成本分析
   - **留存分析**：客户留存率和流失分析
   - **价值预测**：预测客户未来价值
   - **价值优化**：优化客户价值的策略建议

6. **全渠道沟通**
   - **沟通历史**：全渠道沟通历史统一视图
   - **实时聊天**：网站实时聊天集成
   - **社交媒体**：社交媒体客户沟通集成
   - **邮件营销**：邮件营销平台集成
   - **短信营销**：短信营销平台集成

#### 2.4.3 技术规格
- **营销自动化**：营销自动化引擎（类似HubSpot）
- **邮件服务**：SendGrid / Amazon SES集成
- **短信服务**：Twilio / 阿里云短信集成
- **聊天集成**：实时聊天SDK集成
- **社交媒体**：社交媒体API集成

### 2.5 移动端应用

#### 2.5.1 功能描述
iOS和Android移动应用，提供关键业务功能，支持实时通知和移动办公。

#### 2.5.2 功能列表
1. **移动仪表板**
   - **核心指标**：销售额、订单量、库存等核心指标卡片
   - **实时数据**：实时业务数据，支持下拉刷新
   - **快捷操作**：常用操作快捷入口
   - **通知中心**：重要通知和预警
   - **个性化**：可自定义仪表板布局

2. **订单管理**
   - **订单列表**：订单列表，支持筛选和搜索
   - **订单详情**：订单详情查看
   - **订单处理**：订单审核、发货等操作
   - **扫描发货**：扫描运单号快速发货
   - **物流跟踪**：物流状态跟踪

3. **库存管理**
   - **库存查看**：查看商品库存情况
   - **库存预警**：库存预警通知
   - **库存调整**：移动端库存调整
   - **盘点功能**：移动端库存盘点
   - **条码扫描**：扫描商品条码快速操作

4. **客户管理**
   - **客户列表**：客户列表和搜索
   - **客户详情**：客户信息和历史记录
   - **客户沟通**：与客户沟通（消息、电话）
   - **客户跟进**：客户跟进任务管理
   - **现场服务**：现场客户服务支持

5. **通知与审批**
   - **实时通知**：订单、库存、客户等重要通知
   - **消息推送**：重要消息推送通知
   - **审批流程**：移动端审批流程处理
   - **任务提醒**：任务和提醒通知
   - **离线支持**：离线数据缓存和同步

6. **移动专属功能**
   - **相机集成**：拍照上传商品图片
   - **位置服务**：基于位置的服务（仓库导航）
   - **离线模式**：离线操作，联网后自动同步
   - **语音输入**：语音输入快速操作
   - **生物识别**：指纹/面容识别登录

#### 2.4.3 技术规格
- **跨平台框架**：React Native (优先) 或 Flutter
- **推送通知**：Firebase Cloud Messaging (FCM)
- **离线存储**：AsyncStorage / SQLite
- **相机集成**：react-native-camera
- **地图集成**：react-native-maps

## 3. 用户故事与验收标准

### 3.1 AI Agent引擎

#### 用户故事23：自然语言任务执行
**作为** 运营经理
**我希望** 用自然语言描述任务，Agent自动执行
**以便** 快速完成复杂运营任务，无需手动操作

**验收标准**：
1. 在AI Agent界面输入自然语言指令
2. Agent理解指令，确认任务细节
3. Agent自动分解任务为子任务
4. 显示任务执行计划和预计时间
5. 执行过程中显示实时进度
6. 任务完成显示结果和摘要
7. 支持多轮对话澄清需求
8. 任务执行成功率 > 85%

#### 用户故事24：Agent工具调用
**作为** 数据分析师
**我希望** Agent能调用各种数据工具
**以便** 自动完成数据分析和报告生成

**验收标准**：
1. Agent工具库包含数据查询、分析、可视化工具
2. 用户描述数据分析需求，Agent选择合适工具
3. Agent自动设置工具参数
4. 工具调用结果自动整合
5. 支持多个工具串联使用
6. 工具调用权限控制（仅能调用用户有权限的工具）
7. 工具调用失败自动重试或切换备用工具
8. 工具调用历史记录和审计

### 3.2 工作流设计器

#### 用户故事25：可视化工作流设计
**作为** 运营专员
**我希望** 通过拖拽方式设计业务流程
**以便** 自动化重复性工作，提升效率

**验收标准**：
1. 工作流设计器提供可视化画布
2. 左侧节点库包含各种预定义节点
3. 拖拽节点到画布，连接节点定义流程
4. 双击节点编辑节点属性和参数
5. 支持条件分支、循环等逻辑控制
6. 工作流保存和版本管理
7. 工作流一键启用/停用
8. 工作流执行历史可查看

#### 用户故事26：复杂业务流程自动化
**作为** 企业主
**我希望** 自动化复杂业务流程
**以便** 减少人工错误，提升运营效率

**验收标准**：
1. 支持创建多层嵌套的复杂工作流
2. 工作流支持并行执行和条件分支
3. 工作流支持错误处理和重试机制
4. 工作流支持外部服务调用和API集成
5. 工作流执行状态实时监控
6. 工作流执行失败自动告警
7. 工作流性能分析和优化建议
8. 工作流执行效率提升 > 300%

### 3.3 智能运营建议

#### 用户故事27：自动业务问题检测
**作为** 运营总监
**我希望** 系统自动检测业务问题
**以便** 及时发现和解决问题，避免损失

**验收标准**：
1. 系统每天自动扫描业务数据
2. 检测常见业务问题：销售异常、库存异常、价格异常
3. 问题检测准确率 > 80%
4. 问题严重程度分级（严重、重要、一般）
5. 问题根因分析，提供可能原因
6. 问题自动分配给相关负责人
7. 问题解决跟踪和关闭
8. 问题历史记录和趋势分析

#### 用户故事28：可执行优化建议
**作为** 运营人员
**我希望** 系统提供具体的优化建议
**以便** 快速优化业务，提升业绩

**验收标准**：
1. 建议列表显示所有优化建议
2. 每个建议包含：问题描述、建议方案、预期效果、执行难度
3. 建议优先级排序（高、中、低）
4. 建议置信度显示（0-100%）
5. 一键执行建议或跳转到相关功能
6. 建议执行后效果跟踪
7. 建议采纳率 > 50%
8. 采纳建议后业务指标提升验证

### 3.4 高级CRM

#### 用户故事29：客户生命周期自动化
**作为** 销售经理
**我希望** 自动化管理客户生命周期
**以便** 提升客户满意度和留存率

**验收标准**：
1. 系统自动识别客户生命周期阶段
2. 每个阶段定义标准操作流程
3. 阶段转换自动触发相应动作
4. 客户生命周期可视化视图
5. 阶段转换规则可配置
6. 阶段转换历史记录
7. 客户生命周期价值分析
8. 生命周期管理提升客户留存率 > 20%

#### 用户故事30：营销自动化流程
**作为** 营销专员
**我希望** 创建自动化营销流程
**以便** 提升营销效率和效果

**验收标准**：
1. 营销自动化流程设计器
2. 支持多种触发条件：客户行为、时间、事件
3. 支持多种执行动作：邮件、短信、推送、优惠券
4. 流程支持条件分支和等待节点
5. 营销流程效果分析和优化
6. A/B测试支持验证不同方案
7. 营销流程ROI计算
8. 营销自动化提升转化率 > 15%

### 3.5 移动端应用

#### 用户故事31：移动业务管理
**作为** 移动办公人员
**我希望** 在手机上管理核心业务
**以便** 随时随地处理业务，快速响应

**验收标准**：
1. 移动端应用支持iOS和Android
2. 核心功能：订单处理、库存查看、客户沟通
3. 移动端操作体验流畅，响应快速
4. 支持离线操作，联网后自动同步
5. 重要通知实时推送
6. 扫描功能快速操作（条码、运单）
7. 移动端专属功能（拍照上传、位置服务）
8. 移动端用户满意度 > 4.5/5.0

#### 用户故事32：实时业务通知
**作为** 客服人员
**我希望** 实时接收业务重要通知
**以便** 及时响应客户需求和问题

**验收标准**：
1. 重要业务事件实时推送通知
2. 通知类型：新订单、库存预警、客户咨询、任务提醒
3. 通知可配置（接收哪些通知，何时接收）
4. 通知点击跳转到相关功能
5. 通知管理（标记已读、删除、归档）
6. 免打扰模式设置
7. 通知历史记录
8. 重要通知5分钟内响应率 > 90%

## 4. UI/UX设计

### 4.1 AI Agent工作台

#### 4.1.1 设计理念
- **对话式界面**：模仿自然对话，降低使用门槛
- **透明执行**：显示Agent思考过程和执行步骤
- **可控性**：用户随时可以干预和停止
- **学习性**：Agent从交互中学习用户偏好

#### 4.1.2 核心页面
1. **Agent对话界面**
   - **布局**：左侧对话历史，右侧当前对话
   - **输入框**：自然语言输入，支持语音输入
   - **对话历史**：按时间排序的对话历史
   - **执行状态**：显示Agent执行状态（思考、执行、完成）
   - **控制按钮**：停止、重试、确认等控制按钮

2. **Agent配置界面**
   - **Agent选择**：选择不同专业Agent
   - **参数配置**：配置Agent行为参数
   - **权限设置**：设置Agent操作权限
   - **历史记录**：Agent执行历史记录
   - **性能监控**：Agent执行性能监控

3. **工具管理界面**
   - **工具列表**：所有可用工具列表
   - **工具详情**：工具功能、参数、权限说明
   - **工具测试**：测试工具调用
   - **工具统计**：工具使用统计
   - **自定义工具**：自定义工具创建和管理

### 4.2 工作流设计器

#### 4.2.1 设计理念
- **可视化**：所见即所得的设计体验
- **易用性**：拖拽操作，简单直观
- **灵活性**：支持复杂逻辑和嵌套
- **协作性**：支持团队协作设计

#### 4.2.2 核心页面
1. **工作流画布**
   - **画布区域**：无限画布，支持缩放和平移
   - **节点库**：左侧节点分类列表
   - **属性面板**：右侧节点属性编辑
   - **工具栏**：顶部操作工具栏（保存、运行、调试等）
   - **状态栏**：底部状态信息栏

2. **节点编辑器**
   - **节点选择**：选择节点类型
   - **参数配置**：配置节点参数
   - **条件设置**：设置条件分支条件
   - **连接管理**：管理节点连接关系
   - **预览模式**：预览节点效果

3. **工作流管理**
   - **工作流列表**：所有工作流列表
   - **版本管理**：工作流版本历史
   - **执行历史**：工作流执行历史记录
   - **模板库**：预定义工作流模板
   - **分享协作**：工作流分享和协作编辑

### 4.3 智能建议中心

#### 4.3.1 设计理念
- **行动导向**：直接提供可执行建议
- **数据支撑**：每个建议都有数据依据
- **优先级明确**：清晰区分建议优先级
- **效果可测**：建议执行效果可跟踪

#### 4.3.2 核心页面
1. **建议仪表板**
   - **建议概览**：建议数量、采纳率、效果统计
   - **优先级视图**：按优先级分组显示建议
   - **分类视图**：按建议类型分组显示
   - **趋势图表**：建议采纳和执行效果趋势
   - **快速筛选**：按状态、类型、优先级筛选

2. **建议详情页**
   - **问题描述**：详细描述检测到的问题
   - **数据支撑**：支持建议的数据和分析
   - **建议方案**：具体的优化建议和步骤
   - **预期效果**：预期带来的业务改善
   - **执行选项**：一键执行或手动执行选项

3. **效果跟踪页**
   - **执行状态**：建议执行状态跟踪
   - **效果指标**：执行前后的业务指标对比
   - **ROI计算**：建议带来的投资回报计算
   - **用户反馈**：用户对建议的反馈
   - **优化建议**：基于效果的进一步优化建议

### 4.4 高级CRM界面

#### 4.4.1 设计理念
- **客户中心**：以客户为中心的设计
- **全渠道视图**：整合所有客户接触点
- **自动化流程**：自动化重复性客户管理任务
- **数据驱动**：基于数据的客户洞察

#### 4.4.2 核心页面
1. **客户360视图**
   - **基本信息**：客户基本信息和标签
   - **交互历史**：全渠道交互历史时间线
   - **交易历史**：所有交易记录和统计
   - **生命周期**：客户生命周期阶段和转换
   - **价值分析**：客户价值分析和预测

2. **营销自动化**
   - **流程设计器**：可视化营销流程设计
   - **活动管理**：营销活动创建和管理
   - **内容库**：营销内容模板库
   - **效果分析**：营销活动效果分析
   - **A/B测试**：营销方案A/B测试

3. **客户细分**
   - **细分列表**：所有客户细分列表
   - **细分创建**：基于规则创建客户细分
   - **细分分析**：细分客户特征和行为分析
   - **细分应用**：将细分应用于营销活动
   - **细分效果**：细分营销效果分析

### 4.5 移动端界面

#### 4.5.1 设计理念
- **移动优先**：为移动端优化的交互设计
- **核心功能**：聚焦核心业务功能
- **离线支持**：支持离线操作和同步
- **快速操作**：支持扫描、拍照等快速操作

#### 4.5.2 核心页面
1. **移动仪表板**
   - **指标卡片**：核心业务指标卡片
   - **快捷操作**：常用操作快捷入口
   - **通知中心**：重要通知列表
   - **今日任务**：今日待办任务列表
   - **数据图表**：关键数据趋势图表

2. **订单处理**
   - **订单列表**：订单列表，支持筛选
   - **订单详情**：订单详细信息
   - **发货操作**：扫描发货、填写运单
   - **订单搜索**：订单搜索功能
   - **批量操作**：订单批量处理

3. **库存管理**
   - **库存查看**：商品库存查看
   - **库存调整**：移动端库存调整
   - **盘点功能**：移动盘点，扫码盘点
   - **预警查看**：库存预警查看
   - **仓库导航**：仓库内商品位置导航

4. **客户沟通**
   - **客户列表**：客户列表和搜索
   - **客户详情**：客户信息和历史
   - **消息沟通**：与客户消息沟通
   - **电话集成**：点击拨打客户电话
   - **现场服务**：现场服务记录

## 5. API设计

### 5.1 AI Agent API

#### 5.1.1 Agent对话API
**端点**：`POST /api/v3/agent/conversation`
**请求**：
```json
{
  "agent_id": "agent_sales",
  "message": "帮我分析上周销售最好的10个商品，并给出优化建议",
  "conversation_id": "conv_123", // 可选，继续现有对话
  "context": {
    "user_id": "user_123",
    "permissions": ["view_products", "view_sales"]
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_123",
    "response": "我将为您分析上周销售最好的10个商品。首先，我需要查询销售数据...",
    "thought_process": [
      "用户要求分析上周销售最好的10个商品",
      "需要调用销售数据查询工具",
      "需要调用商品信息查询工具",
      "需要调用数据分析工具生成建议"
    ],
    "actions": [
      {
        "type": "tool_call",
        "tool": "sales_query",
        "parameters": {"time_range": "last_week", "limit": 10},
        "result": {"status": "executing"}
      }
    ],
    "status": "thinking", // thinking, executing, waiting, completed
    "estimated_completion_time": 30 // 秒
  }
}
```

#### 5.1.2 Agent工具调用API
**端点**：`POST /api/v3/agent/tools/{tool_name}/execute`
**请求**：
```json
{
  "tool_name": "sales_query",
  "parameters": {
    "time_range": "last_week",
    "metrics": ["revenue", "quantity", "orders"],
    "group_by": ["product_id"],
    "limit": 10
  },
  "context": {
    "user_id": "user_123",
    "agent_id": "agent_sales"
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "tool_call_id": "tool_456",
    "result": {
      "data": [
        {
          "product_id": "product_123",
          "product_title": "无线蓝牙耳机",
          "revenue": 12500.50,
          "quantity": 250,
          "orders": 125
        }
      ],
      "metadata": {
        "time_range": "2026-02-11 to 2026-02-17",
        "total_records": 10
      }
    },
    "execution_time": 2.5,
    "cost": 0.001
  }
}
```

### 5.2 工作流API

#### 5.2.1 工作流执行API
**端点**：`POST /api/v3/workflows/{workflow_id}/execute`
**请求**：
```json
{
  "trigger_type": "manual", // manual, scheduled, event, api
  "parameters": {
    "product_id": "product_123",
    "quantity": 100
  },
  "priority": "normal", // low, normal, high, urgent
  "callback_url": "https://..." // 可选，执行完成回调
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_789",
    "workflow_id": "wf_123",
    "status": "queued", // queued, running, completed, failed
    "started_at": "2026-02-18T14:30:00Z",
    "estimated_completion": "2026-02-18T14:35:00Z",
    "progress_url": "/api/v3/workflows/executions/exec_789/progress"
  }
}
```

#### 5.2.2 工作流执行状态API
**端点**：`GET /api/v3/workflows/executions/{execution_id}/progress`
**响应**：
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_789",
    "workflow_id": "wf_123",
    "status": "running",
    "progress": 65, // 百分比
    "current_node": "node_456",
    "node_name": "查询库存",
    "started_at": "2026-02-18T14:30:00Z",
    "elapsed_time": 120, // 秒
    "estimated_remaining": 65, // 秒
    "nodes_completed": 3,
    "total_nodes": 5,
    "logs": [
      {
        "timestamp": "2026-02-18T14:30:05Z",
        "node_id": "node_123",
        "node_name": "开始",
        "status": "completed",
        "message": "工作流开始执行"
      },
      {
        "timestamp": "2026-02-18T14:30:10Z",
        "node_id": "node_456",
        "node_name": "查询商品信息",
        "status": "completed",
        "message": "成功查询商品信息"
      }
    ]
  }
}
```

### 5.3 智能建议API

#### 5.3.1 建议生成API
**端点**：`POST /api/v3/recommendations/generate`
**请求**：
```json
{
  "scope": {
    "type": "inventory", // inventory, pricing, marketing, product, operations
    "product_ids": ["product_123", "product_456"],
    "time_range": "last_30_days"
  },
  "parameters": {
    "confidence_threshold": 0.7,
    "max_recommendations": 20
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "recommendation_batch_id": "batch_123",
    "recommendations": [
      {
        "id": "rec_123",
        "type": "inventory_optimization",
        "title": "调整安全库存水平",
        "description": "商品'无线蓝牙耳机'的安全库存设置过高，建议从60调整到40",
        "problem": {
          "metric": "safety_stock",
          "current_value": 60,
          "optimal_value": 40,
          "excess_percentage": 50
        },
        "solution": {
          "action": "update_safety_stock",
          "parameters": {"product_id": "product_123", "new_safety_stock": 40},
          "steps": ["进入库存管理", "编辑商品库存设置", "调整安全库存为40"]
        },
        "expected_impact": {
          "inventory_cost_reduction": 1200.00,
          "inventory_turnover_improvement": 0.2
        },
        "confidence": 0.85,
        "priority": "medium",
        "generated_at": "2026-02-18T14:30:00Z"
      }
    ],
    "summary": {
      "total_recommendations": 5,
      "estimated_total_impact": 5250.00,
      "generation_time": 15.3
    }
  }
}
```

#### 5.3.2 建议执行API
**端点**：`POST /api/v3/recommendations/{recommendation_id}/execute`
**请求**：
```json
{
  "execution_mode": "auto", // auto, manual, semi_auto
  "parameters": {}, // 可选，覆盖建议参数
  "notes": "测试执行建议"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_456",
    "recommendation_id": "rec_123",
    "status": "executing",
    "execution_mode": "auto",
    "action_taken": "update_safety_stock",
    "parameters_used": {"product_id": "product_123", "new_safety_stock": 40},
    "started_at": "2026-02-18T14:35:00Z",
    "estimated_completion": "2026-02-18T14:35:05Z"
  }
}
```

### 5.4 移动端API

#### 5.4.1 移动端认证API
**端点**：`POST /api/v3/mobile/auth/login`
**请求**：
```json
{
  "email": "user@example.com",
  "password": "password123",
  "device_info": {
    "device_id": "device_123",
    "platform": "ios",
    "os_version": "17.2",
    "app_version": "3.0.0",
    "push_token": "apns_token_123"
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "access_token": "mobile_token_123",
    "refresh_token": "mobile_refresh_123",
    "expires_in": 86400, // 24小时
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "张三",
      "role": "operator",
      "permissions": ["view_orders", "process_orders", "view_inventory"]
    },
    "sync_info": {
      "last_sync_time": "2026-02-18T10:30:00Z",
      "pending_changes": 0
    }
  }
}
```

#### 5.4.2 移动端数据同步API
**端点**：`POST /api/v3/mobile/sync`
**请求**：
```json
{
  "device_id": "device_123",
  "sync_token": "sync_789",
  "changes": {
    "orders": [
      {
        "id": "order_123",
        "action": "update",
        "data": {"status": "shipped", "tracking_number": "SF1234567890"},
        "local_timestamp": "2026-02-18T14:30:00Z"
      }
    ]
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "new_sync_token": "sync_790",
    "conflicts": [],
    "updates": {
      "orders": [
        {
          "id": "order_456",
          "action": "create",
          "data": {
            "id": "order_456",
            "order_number": "OZ-20260218-002",
            "status": "pending",
            "created_at": "2026-02-18T14:35:00Z"
          },
          "server_timestamp": "2026-02-18T14:35:00Z"
        }
      ],
      "inventory": [
        {
          "id": "inv_123",
          "action": "update",
          "data": {"product_id": "product_123", "quantity": 45},
          "server_timestamp": "2026-02-18T14:32:00Z"
        }
      ]
    },
    "deletions": {
      "customers": ["customer_789"]
    },
    "server_time": "2026-02-18T14:40:00Z"
  }
}
```

## 6. 数据库设计（扩展）

### 6.1 AI Agent相关表

#### 6.1.1 Agent配置表
```sql
CREATE TABLE agent_configs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50) NOT NULL, -- general, sales, inventory, customer_service, purchasing
    model_config JSONB NOT NULL, -- LLM模型配置
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    tools_enabled TEXT[] DEFAULT '{}', -- 启用的工具列表
    permissions JSONB DEFAULT '{}', -- Agent权限限制
    system_prompt TEXT, -- 系统提示词
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name)
);

CREATE INDEX idx_agent_configs_team_type ON agent_configs(team_id, agent_type);
CREATE INDEX idx_agent_configs_active ON agent_configs(team_id) WHERE is_active = TRUE;
```

#### 6.1.2 Agent对话表
```sql
CREATE TABLE agent_conversations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent_configs(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    title VARCHAR(255), -- 对话标题，自动生成
    status VARCHAR(20) DEFAULT 'active', -- active, completed, archived
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_agent_conversations_team_user ON agent_conversations(team_id, user_id);
CREATE INDEX idx_agent_conversations_agent ON agent_conversations(agent_id);
CREATE INDEX idx_agent_conversations_updated ON agent_conversations(updated_at DESC);
```

#### 6.1.3 Agent消息表
```sql
CREATE TABLE agent_messages (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(36) NOT NULL REFERENCES agent_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system, tool
    content TEXT,
    tool_calls JSONB, -- 工具调用信息
    tool_call_id VARCHAR(100), -- 工具调用ID
    tool_name VARCHAR(100), -- 工具名称
    tool_arguments JSONB, -- 工具参数
    tool_output JSONB, -- 工具输出
    token_count INTEGER DEFAULT 0,
    cost DECIMAL(10, 4) DEFAULT 0,
    model_used VARCHAR(50),
    reasoning TEXT, -- Agent思考过程
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_messages_conversation ON agent_messages(conversation_id, created_at);
CREATE INDEX idx_agent_messages_role ON agent_messages(conversation_id, role);
CREATE INDEX idx_agent_messages_tool ON agent_messages(tool_name) WHERE tool_name IS NOT NULL;
```

#### 6.1.4 Agent工具表
```sql
CREATE TABLE agent_tools (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- data_query, action, analysis, external
    endpoint VARCHAR(255), -- 工具调用端点
    http_method VARCHAR(10) DEFAULT 'POST',
    parameters_schema JSONB NOT NULL, -- 参数JSON Schema
    response_schema JSONB, -- 响应JSON Schema
    permissions_required TEXT[] DEFAULT '{}', -- 所需权限
    rate_limit INTEGER, -- 速率限制（次/分钟）
    cost_per_call DECIMAL(10, 4) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name)
);

CREATE INDEX idx_agent_tools_team_category ON agent_tools(team_id, category);
CREATE INDEX idx_agent_tools_active ON agent_tools(team_id) WHERE is_active = TRUE;
```

#### 6.1.5 Agent工具调用记录表
```sql
CREATE TABLE agent_tool_calls (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    conversation_id VARCHAR(36) REFERENCES agent_conversations(id) ON DELETE CASCADE,
    tool_id VARCHAR(36) NOT NULL REFERENCES agent_tools(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    parameters JSONB NOT NULL,
    result JSONB,
    status VARCHAR(20) NOT NULL, -- success, failed, timeout
    error_message TEXT,
    execution_time DECIMAL(10, 2), -- 秒
    cost DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_tool_calls_team_tool ON agent_tool_calls(team_id, tool_id);
CREATE INDEX idx_agent_tool_calls_user ON agent_tool_calls(user_id, created_at DESC);
CREATE INDEX idx_agent_tool_calls_status ON agent_tool_calls(status, created_at);
```

### 6.2 工作流相关表

#### 6.2.1 工作流定义表
```sql
CREATE TABLE workflow_definitions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version INTEGER DEFAULT 1,
    definition JSONB NOT NULL, -- 工作流节点和连接定义
    trigger_config JSONB, -- 触发器配置
    variables_schema JSONB, -- 变量定义
    timeout_seconds INTEGER DEFAULT 3600,
    retry_config JSONB DEFAULT '{"max_retries": 3, "backoff_factor": 2}',
    concurrency_limit INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_template BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name, version)
);

CREATE INDEX idx_workflow_definitions_team_active ON workflow_definitions(team_id) WHERE is_active = TRUE;
CREATE INDEX idx_workflow_definitions_templates ON workflow_definitions(team_id) WHERE is_template = TRUE;
CREATE INDEX idx_workflow_definitions_updated ON workflow_definitions(updated_at DESC);
```

#### 6.2.2 工作流执行表
```sql
CREATE TABLE workflow_executions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    workflow_id VARCHAR(36) NOT NULL REFERENCES workflow_definitions(id),
    execution_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL, -- queued, running, completed, failed, cancelled
    trigger_type VARCHAR(20) NOT NULL, -- manual, scheduled, event, api
    trigger_data JSONB, -- 触发数据
    input_parameters JSONB, -- 输入参数
    output_result JSONB, -- 输出结果
    variables JSONB DEFAULT '{}', -- 执行变量
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id, created_at DESC);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status, created_at);
CREATE INDEX idx_workflow_executions_team_date ON workflow_executions(team_id, created_at DESC);
```

#### 6.2.3 工作流节点执行表
```sql
CREATE TABLE workflow_node_executions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(36) NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    node_id VARCHAR(100) NOT NULL, -- 工作流节点ID
    node_type VARCHAR(50) NOT NULL, -- trigger, action, condition, loop
    node_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- pending, running, completed, failed, skipped
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_node_executions_execution ON workflow_node_executions(execution_id, node_id);
CREATE INDEX idx_workflow_node_executions_status ON workflow_node_executions(execution_id, status);
CREATE INDEX idx_workflow_node_executions_duration ON workflow_node_executions(execution_id, duration_ms DESC);
```

#### 6.2.4 工作流日志表
```sql
CREATE TABLE workflow_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(36) NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    node_execution_id VARCHAR(36) REFERENCES workflow_node_executions(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL, -- info, warning, error, debug
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_logs_execution ON workflow_logs(execution_id, created_at);
CREATE INDEX idx_workflow_logs_level ON workflow_logs(execution_id, level, created_at);
CREATE INDEX idx_workflow_logs_node ON workflow_logs(node_execution_id, created_at);
```

### 6.3 智能建议相关表

#### 6.3.1 建议定义表
```sql
CREATE TABLE recommendation_definitions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL, -- inventory, pricing, marketing, product, operations
    name VARCHAR(100) NOT NULL,
    description TEXT,
    detection_rule JSONB NOT NULL, -- 问题检测规则
    generation_logic JSONB NOT NULL, -- 建议生成逻辑
    priority_calculation JSONB, -- 优先级计算规则
    expected_impact_calculation JSONB, -- 预期影响计算
    confidence_calculation JSONB, -- 置信度计算
    execution_action JSONB, -- 执行动作定义
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, recommendation_type, name)
);

CREATE INDEX idx_recommendation_definitions_team_type ON recommendation_definitions(team_id, recommendation_type);
CREATE INDEX idx_recommendation_definitions_active ON recommendation_definitions(team_id) WHERE is_active = TRUE;
```

#### 6.3.2 建议实例表
```sql
CREATE TABLE recommendation_instances (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    definition_id VARCHAR(36) NOT NULL REFERENCES recommendation_definitions(id),
    batch_id VARCHAR(36), -- 批次ID，同一批次生成的建议
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    problem_description TEXT,
    problem_data JSONB, -- 问题数据
    solution_description TEXT,
    solution_action JSONB NOT NULL, -- 解决方案动作
    expected_impact JSONB, -- 预期影响
    confidence DECIMAL(3, 2) NOT NULL, -- 置信度 0-1
    priority VARCHAR(20) NOT NULL, -- high, medium, low
    status VARCHAR(20) DEFAULT 'new', -- new, acknowledged, approved, rejected, executed, expired
    target_entity_type VARCHAR(50), -- product, order, customer, etc.
    target_entity_id VARCHAR(36), -- 目标实体ID
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by VARCHAR(36) REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    approved_by VARCHAR(36) REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    executed_by VARCHAR(36) REFERENCES users(id),
    executed_at TIMESTAMPTZ,
    execution_result JSONB,
    actual_impact JSONB, -- 实际影响
    expired_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendation_instances_team_status ON recommendation_instances(team_id, status);
CREATE INDEX idx_recommendation_instances_priority ON recommendation_instances(team_id, priority, status);
CREATE INDEX idx_recommendation_instances_target ON recommendation_instances(target_entity_type, target_entity_id);
CREATE INDEX idx_recommendation_instances_generated ON recommendation_instances(generated_at DESC);
```

#### 6.3.3 建议效果跟踪表
```sql
CREATE TABLE recommendation_impact_tracking (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    recommendation_id VARCHAR(36) NOT NULL REFERENCES recommendation_instances(id) ON DELETE CASCADE,
    tracking_period_start DATE NOT NULL,
    tracking_period_end DATE NOT NULL,
    metrics_before JSONB NOT NULL, -- 执行前指标
    metrics_after JSONB NOT NULL, -- 执行后指标
    impact_calculation JSONB NOT NULL, -- 影响计算
    roi_calculation DECIMAL(10, 2), -- ROI计算
    user_feedback VARCHAR(20), -- positive, neutral, negative
    feedback_notes TEXT,
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recommendation_id, tracking_period_start)
);

CREATE INDEX idx_recommendation_impact_tracking_recommendation ON recommendation_impact_tracking(recommendation_id);
CREATE INDEX idx_recommendation_impact_tracking_period ON recommendation_impact_tracking(tracking_period_start);
```

### 6.4 移动端相关表

#### 6.4.1 移动设备表
```sql
CREATE TABLE mobile_devices (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(100) NOT NULL, -- 设备唯一标识
    platform VARCHAR(20) NOT NULL, -- ios, android
    os_version VARCHAR(20),
    app_version VARCHAR(20),
    device_model VARCHAR(100),
    push_token VARCHAR(255),
    last_login_at TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    sync_token VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id, device_id)
);

CREATE INDEX idx_mobile_devices_user ON mobile_devices(user_id, platform);
CREATE INDEX idx_mobile_devices_active ON mobile_devices(team_id) WHERE is_active = TRUE;
CREATE INDEX idx_mobile_devices_push_token ON mobile_devices(push_token) WHERE push_token IS NOT NULL;
```

#### 6.4.2 移动端同步表
```sql
CREATE TABLE mobile_sync_records (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(36) NOT NULL REFERENCES mobile_devices(id) ON DELETE CASCADE,
    sync_type VARCHAR(20) NOT NULL, -- full, incremental, conflict_resolution
    sync_direction VARCHAR(20) NOT NULL, -- upload, download, bidirectional
    changes_applied INTEGER DEFAULT 0, -- 应用的变更数量
    changes_received INTEGER DEFAULT 0, -- 接收的变更数量
    conflicts_resolved INTEGER DEFAULT 0, -- 解决的冲突数量
    sync_duration_ms INTEGER, -- 同步耗时（毫秒）
    sync_status VARCHAR(20) NOT NULL, -- success, partial, failed
    error_message TEXT,
    sync_token_before VARCHAR(100),
    sync_token_after VARCHAR(100),
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_mobile_sync_records_device ON mobile_sync_records(device_id, started_at DESC);
CREATE INDEX idx_mobile_sync_records_status ON mobile_sync_records(sync_status, started_at);
```

#### 6.4.3 移动端离线操作表
```sql
CREATE TABLE mobile_offline_operations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(36) NOT NULL REFERENCES mobile_devices(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL, -- create_order, update_inventory, etc.
    entity_type VARCHAR(50) NOT NULL, -- order, inventory, customer, etc.
    entity_id VARCHAR(100), -- 实体ID（本地生成）
    operation_data JSONB NOT NULL, -- 操作数据
    local_timestamp TIMESTAMPTZ NOT NULL, -- 本地操作时间
    sync_status VARCHAR(20) DEFAULT 'pending', -- pending, synced, conflicted, failed
    sync_attempts INTEGER DEFAULT 0,
    last_sync_attempt TIMESTAMPTZ,
    sync_error TEXT,
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mobile_offline_operations_device_status ON mobile_offline_operations(device_id, sync_status);
CREATE INDEX idx_mobile_offline_operations_timestamp ON mobile_offline_operations(local_timestamp DESC);
CREATE INDEX idx_mobile_offline_operations_entity ON mobile_offline_operations(entity_type, entity_id);
```

## 7. 技术架构

### 7.1 AI Agent架构

#### 7.1.1 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面       │    │   API网关       │    │   Agent服务     │
│   (React)       │────│   (FastAPI)     │────│   (LangChain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                      ┌───────┴───────┐         ┌───────┴───────┐
                      │   认证授权     │         │   工具路由     │
                      │   (JWT)       │         │   (Tool Router)│
                      └───────────────┘         └───────────────┘
                              │                         │
                      ┌───────┴───────┐         ┌───────┴───────┐
                      │   业务服务     │         │   工具执行     │
                      │   (微服务)     │         │   (Tool Exec) │
                      └───────────────┘         └───────────────┘
                              │                         │
                      ┌───────┴───────┐         ┌───────┴───────┐
                      │   数据存储     │         │   外部服务     │
                      │   (PostgreSQL)│         │   (APIs)      │
                      └───────────────┘         └───────────────┘
```

#### 7.1.2 LangChain集成架构
```python
# Agent服务核心架构
class ICROSSAgent:
    """iCross智能Agent"""
    
    def __init__(self, agent_config: dict):
        self.config = agent_config
        self.llm = self._init_llm()
        self.tools = self._load_tools()
        self.memory = self._init_memory()
        self.agent = self._build_agent()
    
    def _init_llm(self):
        """初始化LLM"""
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model=self.config["model"],
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"],
            streaming=True
        )
    
    def _load_tools(self):
        """加载工具"""
        from langchain.tools import Tool
        
        tools = []
        for tool_name in self.config["tools_enabled"]:
            tool_config = get_tool_config(tool_name)
            tool = Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                func=self._create_tool_func(tool_config),
                return_direct=False
            )
            tools.append(tool)
        
        return tools
    
    def _build_agent(self):
        """构建Agent"""
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        # 系统提示词
        system_prompt = self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建执行器
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
        
        return executor
    
    async def process_message(self, message: str, context: dict) -> dict:
        """处理用户消息"""
        try:
            # 执行Agent
            response = await self.agent.ainvoke({
                "input": message,
                "chat_history": self.memory.chat_memory.messages
            })
            
            # 更新记忆
            self.memory.save_context(
                {"input": message},
                {"output": response["output"]}
            )
            
            return {
                "success": True,
                "response": response["output"],
                "thought_process": self._extract_thoughts(response),
                "tool_calls": self._extract_tool_calls(response)
            }
            
        except Exception as e:
            logger.error(f"Agent处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，我遇到了一些问题。请稍后重试或联系管理员。"
            }
```

### 7.2 工作流引擎架构

#### 7.2.1 工作流执行引擎
```python
# 工作流引擎核心
class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self):
        self.executor = CeleryExecutor()
        self.dag_processor = DAGProcessor()
        self.node_registry = NodeRegistry()
        
    async def execute_workflow(self, workflow_id: str, trigger_data: dict) -> str:
        """执行工作流"""
        try:
            # 加载工作流定义
            workflow_def = await self._load_workflow_definition(workflow_id)
            
            # 创建执行记录
            execution_id = await self._create_execution_record(
                workflow_id, trigger_data
            )
            
            # 解析DAG
            dag = self.dag_processor.parse_dag(workflow_def["definition"])
            
            # 执行工作流
            execution_task = self.executor.submit(
                self._execute_dag,
                dag,
                trigger_data,
                execution_id
            )
            
            # 返回执行ID
            return execution_id
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            raise
    
    async def _execute_dag(self, dag: DAG, context: dict, execution_id: str):
        """执行DAG"""
        # 拓扑排序
        topological_order = dag.get_topological_order()
        
        # 执行每个节点
        for node_id in topological_order:
            node = dag.get_node(node_id)
            
            # 记录节点开始
            await self._record_node_start(execution_id, node_id)
            
            try:
                # 获取节点输入
                node_input = self._prepare_node_input(node, context)
                
                # 执行节点
                node_output = await self._execute_node(node, node_input)
                
                # 更新上下文
                context.update(node_output)
                
                # 记录节点完成
                await self._record_node_completion(
                    execution_id, node_id, node_output
                )
                
            except Exception as e:
                # 记录节点失败
                await self._record_node_failure(
                    execution_id, node_id, str(e)
                )
                
                # 根据错误处理策略决定是否继续
                if node.error_policy == "stop":
                    raise
                elif node.error_policy == "continue":
                    continue
        
        # 记录工作流完成
        await self._record_workflow_completion(execution_id, context)
    
    async def _execute_node(self, node: Node, input_data: dict) -> dict:
        """执行单个节点"""
        node_type = node.node_type
        
        if node_type == "action":
            return await self._execute_action_node(node, input_data)
        elif node_type == "condition":
            return await self._execute_condition_node(node, input_data)
        elif node_type == "loop":
            return await self._execute_loop_node(node, input_data)
        elif node_type == "data":
            return await self._execute_data_node(node, input_data)
        else:
            raise ValueError(f"未知节点类型: {node_type}")
    
    async def _execute_action_node(self, node: Node, input_data: dict) -> dict:
        """执行动作节点"""
        action_type = node.action_type
        
        # 根据动作类型执行
        if action_type == "api_call":
            return await self._execute_api_call(node, input_data)
        elif action_type == "database_query":
            return await self._execute_database_query(node, input_data)
        elif action_type == "tool_call":
            return await self._execute_tool_call(node, input_data)
        elif action_type == "notification":
            return await self._execute_notification(node, input_data)
        else:
            raise ValueError(f"未知动作类型: {action_type}")
```

### 7.3 移动端架构

#### 7.3.1 React Native架构
```
┌─────────────────────────────────────────────────┐
│                 用户界面层 (UI Layer)             │
│  • 组件库 (React Native Components)              │
│  • 导航 (React Navigation)                      │
│  • 样式 (Styled Components / StyleSheet)        │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                业务逻辑层 (Business Logic)        │
│  • 状态管理 (Zustand / Redux)                   │
│  • API客户端 (Axios + 拦截器)                   │
│  • 业务服务 (Services)                          │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                数据持久层 (Data Persistence)      │
│  • 本地存储 (AsyncStorage)                      │
│  • 数据库 (SQLite / WatermelonDB)               │
│  • 同步服务 (Sync Service)                      │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                原生模块层 (Native Modules)        │
│  • 相机 (react-native-camera)                   │
│  • 推送 (react-native-push-notification)        │
│  • 条码扫描 (react-native-barcode-scanner)      │
└─────────────────────────────────────────────────┘
```

#### 7.3.2 离线同步架构
```javascript
// 离线同步服务
class OfflineSyncService {
  constructor() {
    this.localDB = new LocalDatabase();
    this.syncQueue = new SyncQueue();
    this.networkMonitor = new NetworkMonitor();
    this.conflictResolver = new ConflictResolver();
  }

  // 离线操作
  async performOfflineOperation(operation) {
    // 保存到本地数据库
    const localRecord = await this.localDB.saveOperation(operation);
    
    // 添加到同步队列
    await this.syncQueue.enqueue({
      operationId: localRecord.id,
      operationType: operation.type,
      data: operation.data,
      localTimestamp: new Date().toISOString()
    });
    
    // 如果在线，立即同步
    if (this.networkMonitor.isOnline()) {
      await this.syncNow();
    }
    
    return localRecord;
  }

  // 同步
  async syncNow() {
    if (!this.networkMonitor.isOnline()) {
      return { success: false, reason: 'offline' };
    }

    const pendingOperations = await this.syncQueue.getPending();
    
    for (const op of pendingOperations) {
      try {
        // 发送到服务器
        const response = await apiClient.syncOperation(op);
        
        // 处理响应
        await this.handleSyncResponse(op, response);
        
        // 标记为已同步
        await this.syncQueue.markAsSynced(op.operationId);
        
      } catch (error) {
        // 处理错误
        await this.handleSyncError(op, error);
      }
    }
    
    // 下载服务器变更
    await this.downloadServerChanges();
    
    return { success: true, synced: pendingOperations.length };
  }

  // 冲突解决
  async handleConflict(localData, serverData) {
    // 根据策略解决冲突
    const strategy = this.conflictResolver.getStrategy(
      localData.entityType,
      localData.operationType
    );
    
    return strategy.resolve(localData, serverData);
  }
}
```

## 8. 部署与扩展

### 8.1 AI Agent服务部署

#### 8.1.1 部署架构
```
负载均衡器 (AWS ALB)
       |
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Agent网关 │ │ Agent服务 │ │ 工具服务 │
   │ (2副本)   │ │ (3副本)   │ │ (2副本)   │
   └─────────┘ └─────────┘ └─────────┘
       │              │              │
   ┌───┴───┐     ┌───┴───┐     ┌───┴───┐
   │ Redis  │     │ LLM API│     │ 业务服务│
   │ 集群   │     │ 代理   │     │ (微服务)│
   └───────┘     └───────┘     └───────┘
```

#### 8.1.2 资源需求
- **Agent服务**：CPU密集型，需要多核CPU和大内存
- **LLM API代理**：需要稳定网络连接和API密钥管理
- **工具服务**：根据工具类型需要不同资源（数据库连接、外部API调用）
- **Redis集群**：用于会话存储和消息队列

#### 8.1.3 监控与告警
- **性能监控**：Agent响应时间、工具调用成功率
- **成本监控**：LLM API调用成本监控
- **错误监控**：Agent执行错误率和根因分析
- **使用监控**：用户使用模式和频率

### 8.2 工作流引擎部署

#### 8.2.1 部署架构
```
调度器 (Airflow Scheduler)
       |
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Web服务器 │ │ 执行器   │ │ 工作器   │
   │ (2副本)   │ │ (主备)   │ │ (多副本) │
   └─────────┘ └─────────┘ └─────────┘
       │              │              │
   ┌───┴───┐     ┌───┴───┐     ┌───┴───┐
   │ 元数据 │     │ 消息队 │     │ 日志存 │
   │ 数据库 │     │ 列     │     │ 储     │
   └───────┘     └───────┘     └───────┘
```

#### 8.2.2 高可用配置
- **调度器高可用**：多调度器实例，领导选举
- **执行器高可用**：主备模式，自动故障转移
- **工作器自动扩缩**：基于队列长度自动扩缩工作器
- **数据库高可用**：PostgreSQL主从复制

#### 8.2.3 性能优化
- **DAG解析优化**：缓存解析结果，减少重复解析
- **任务并行化**：支持任务并行执行
- **资源隔离**：不同类型任务资源隔离
- **优先级队列**：支持任务优先级调度

### 8.3 移动端部署

#### 8.3.1 应用商店部署
- **iOS App Store**：企业开发者账户，TestFlight测试
- **Android Google Play**：Google Play Console发布
- **国内安卓市场**：华为、小米、应用宝等
- **企业分发**：企业内部分发渠道

#### 8.3.2 后端服务部署
- **API服务**：移动端专用API，优化移动网络
- **推送服务**：Firebase Cloud Messaging (FCM)
- **CDN加速**：静态资源CDN加速
- **移动网关**：移动端专用API网关

#### 8.3.3 移动端监控
- **崩溃监控**：Sentry / Firebase Crashlytics
- **性能监控**：应用启动时间、页面加载时间
- **用户行为**：用户使用路径和习惯
- **网络监控**：API调用成功率和延迟

## 9. 开发路线图

### 9.1 v3.0开发阶段（v2.0后4个月）

#### 第1-2月：AI Agent引擎
- **Agent基础架构**：
  - LangChain集成和定制
  - 工具系统设计和实现
  - 对话管理和记忆系统
  - Agent权限和安全控制
  
- **核心Agent开发**：
  - 销售分析Agent
  - 库存管理Agent
  - 客户服务Agent
  - 采购决策Agent
  
- **Agent界面开发**：
  - 对话式界面
  - Agent配置和管理
  - 工具调用监控
  - 执行历史记录

#### 第3-4月：工作流设计器
- **工作流引擎**：
  - 工作流定义和解析
  - 节点执行引擎
  - 工作流调度和执行
  - 错误处理和重试
  
- **可视化设计器**：
  - 拖拽式界面开发
  - 节点库和属性编辑器
  - 工作流调试和测试
  - 工作流模板系统
  
- **工作流集成**：
  - 与业务系统集成
  - 定时任务和工作流
  - 事件触发工作流
  - API触发工作流

#### 第5-6月：智能运营建议
- **建议引擎**：
  - 问题检测算法
  - 建议生成逻辑
  - 优先级和置信度计算
  - 效果预测模型
  
- **建议管理**：
  - 建议展示和筛选
  - 一键执行功能
  - 效果跟踪和反馈
  - A/B测试框架
  
- **个性化推荐**：
  - 用户画像构建
  - 个性化建议生成
  - 建议时机优化
  - 推荐系统优化

#### 第7-8月：高级CRM和移动端
- **高级CRM**：
  - 客户生命周期管理
  - 营销自动化系统
  - 客户细分和分析
  - 全渠道沟通集成
  
- **移动端开发**：
  - React Native应用开发
  - 核心功能移动化
  - 离线同步功能
  - 推送通知集成
  
- **系统集成与测试**：
  - 全系统集成测试
  - 性能测试和优化
  - 用户测试和反馈
  - 生产环境部署

### 9.2 关键里程碑

#### 里程碑1：AI Agent上线（第2月末）
- ✅ Agent基础架构完成
- ✅ 核心Agent功能上线
- ✅ Agent对话界面完成
- ✅ 用户测试和反馈收集

#### 里程碑2：工作流设计器上线（第4月末）
- ✅ 工作流引擎完成
- ✅ 可视化设计器上线
- ✅ 工作流执行和监控
- ✅ 工作流模板库上线

#### 里程碑3：智能建议系统上线（第6月末）
- ✅ 建议引擎完成
- ✅ 建议管理界面上线
- ✅ 个性化推荐上线
- ✅ 建议效果验证

#### 里程碑4：移动端上线（第8月末）
- ✅ 移动端应用上线
- ✅ 高级CRM功能上线
- ✅ 全系统集成完成
- ✅ v3.0正式发布

### 9.3 资源需求

#### 开发团队扩展：
- **AI工程师**：2人（Agent、机器学习、NLP）
- **前端工程师**：2人（工作流设计器、移动端）
- **后端工程师**：2人（工作流引擎、移动后端）
- **移动开发**：2人（iOS/Android开发）
- **测试工程师**：1人（全系统测试）

#### 基础设施扩展：
- **GPU服务器**：用于AI模型推理
- **工作流集群**：工作流执行集群
- **移动后端**：移动端专用后端服务
- **推送服务**：移动推送服务基础设施
- **监控系统**：全链路监控系统

#### 第三方服务：
- **OpenAI API**：GPT-4等高级模型
- **LangChain**：Agent框架（开源）
- **Apache Airflow**：工作流引擎（开源）
- **Firebase**：移动推送和分析
- **SendGrid/Twilio**：邮件/短信服务

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-02-18 | 初始版本创建，v3.0详细设计 | AI Assistant |

*本文档为iCross v3.0 AI Agent与智能运营阶段详细设计文档，将指导v3.0版本的开发工作。*