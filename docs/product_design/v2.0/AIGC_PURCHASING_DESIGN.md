# iCross v2.0 AIGC与采购自动化阶段详细设计文档

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v1.0 |
| **最后更新** | 2026-02-18 |
| **对应产品版本** | iCross v2.0 |
| **阶段名称** | AIGC与采购自动化阶段 (AIGC & Purchasing Automation Phase) |
| **时间周期** | v1.0后3个月 |
| **文档负责人** | 产品经理 + AI技术负责人 |

## 1. 概述

### 1.1 阶段目标
在v1.0基础ERP平台基础上，增加AI内容生成和智能采购功能，实现：
- **AIGC内容生成**：自动生成商品上架文案、营销图片、介绍视频
- **采购源管理**：供应商和货源平台统一管理，智能货源推荐
- **智能采购**：基于销售数据和库存情况自动生成采购订单
- **高级库存**：智能补货建议，库存优化分析
- **数据仪表板**：多维度数据分析和可视化

### 1.2 核心价值主张
- **内容创作自动化**：AI自动生成高质量商品内容，降低90%内容创作成本
- **采购决策智能化**：数据驱动的智能采购推荐，提升采购效率50%
- **库存管理精细化**：基于销售预测的智能补货，减少缺货和积压
- **数据分析可视化**：多维度业务数据洞察，支持数据驱动决策

### 1.3 目标用户
- **成长型卖家**：3-5人团队，月销售额10-50万人民币，管理500-2000个SKU
- **专业型卖家**：5-10人团队，月销售额 > 50万人民币，管理 > 2000个SKU
- **内容创作者**：需要大量商品内容创作的支持人员

### 1.4 成功指标
- AIGC内容使用率 > 60%
- 采购自动化率 > 40%
- 付费用户转化率 > 25%
- 用户留存率（90天） > 70%
- 库存周转率提升 > 20%

## 2. 功能规格

### 2.1 AIGC内容生成系统

#### 2.1.1 功能描述
基于AI大模型自动生成商品上架所需的各种内容，包括文案、图片、视频，支持多语言和多风格。

#### 2.1.2 功能列表
1. **文案生成引擎**
   - **商品标题生成**：基于商品属性和目标市场生成优化标题
   - **商品描述生成**：生成详细商品描述，突出卖点和功能
   - **卖点提炼**：从商品信息中自动提炼3-5个核心卖点
   - **SEO关键词生成**：生成相关SEO关键词和标签
   - **多语言支持**：支持中文、英文、俄文等目标市场语言
   - **风格定制**：支持不同风格（专业、活泼、简洁、详细等）

2. **图片生成引擎**
   - **主图生成**：基于商品原图生成优化主图（白底、场景、模特图）
   - **详情图生成**：生成商品详情展示图（功能展示、尺寸对比、使用场景）
   - **营销图生成**：生成促销海报、广告图、社交媒体图
   - **风格转换**：支持多种图片风格（真实感、插画风、简约风等）
   - **背景替换**：自动替换商品图片背景
   - **尺寸适配**：生成不同平台要求的图片尺寸

3. **视频生成引擎**
   - **图片转视频**：将商品图片自动剪辑成展示视频
   - **产品演示视频**：生成商品功能演示视频
   - **营销短视频**：生成社交媒体短视频（15-60秒）
   - **自动配乐**：根据商品类型自动匹配背景音乐
   - **自动字幕**：自动生成和添加字幕
   - **特效添加**：自动添加转场特效和文字动画

4. **内容管理**
   - **内容库**：存储所有生成的AIGC内容
   - **版本管理**：内容版本控制和历史记录
   - **内容审核**：人工审核和编辑AIGC生成内容
   - **内容应用**：一键应用到商品或导出使用
   - **内容模板**：保存常用内容生成模板

5. **AIGC任务管理**
   - **批量生成**：批量生成多个商品的内容
   - **任务队列**：AIGC任务队列和状态监控
   - **进度跟踪**：实时显示生成进度
   - **失败重试**：失败任务自动重试机制
   - **成本统计**：统计AIGC使用成本（API调用费用）

#### 2.1.3 技术规格
- **LLM服务**：OpenAI GPT-4 + Claude 3，支持国内大模型备用
- **图片生成**：Stable Diffusion API + DALL-E 3，支持自定义模型
- **视频生成**：Runway ML + Pika Labs API
- **异步处理**：Celery分布式任务队列
- **内容存储**：MinIO对象存储 + CDN加速
- **成本控制**：API调用配额和费用监控

### 2.2 采购源与供应商管理

#### 2.2.1 功能描述
统一管理商品采购来源，包括供应商信息和货源平台集成，支持智能货源推荐。

#### 2.2.2 功能列表
1. **供应商管理**
   - **供应商信息**：基本信息（名称、联系人、联系方式）
   - **供应商档案**：合作历史、评价评级、证书资质
   - **供应商分类**：按品类、地区、合作类型分类
   - **供应商评估**：价格、质量、交期、服务综合评估
   - **供应商标签**：自定义标签（优质、备用、淘汰等）
   - **供应商沟通**：记录与供应商的沟通历史

2. **货源平台集成**
   - **1688集成**：阿里巴巴1688平台商品信息抓取
   - **淘宝/天猫集成**：淘宝天猫商品信息抓取
   - **拼多多集成**：拼多多商品信息抓取
   - **敦煌网集成**：敦煌网跨境电商货源
   - **平台认证**：货源平台API认证和连接
   - **数据抓取**：商品信息、价格、库存、评价抓取

3. **采购源发现**
   - **链接导入**：通过商品链接自动识别货源
   - **图片搜索**：通过商品图片反向搜索货源
   - **关键词搜索**：在货源平台搜索同类商品
   - **相似货源推荐**：基于现有商品推荐相似货源
   - **价格对比**：多个货源价格对比分析

4. **采购源评估**
   - **价格评估**：货源价格与销售价格对比
   - **质量评估**：基于评价和评分的质量评估
   - **交期评估**：发货速度和物流时效评估
   - **可靠性评估**：供应商可靠性和稳定性评估
   - **综合评分**：多维度综合评分和排名

5. **智能推荐引擎**
   - **基于销售推荐**：基于商品销售数据推荐货源
   - **基于库存推荐**：基于库存情况推荐补货货源
   - **基于价格推荐**：推荐性价比最高的货源
   - **基于质量推荐**：推荐质量最可靠的货源
   - **混合推荐**：多因素加权综合推荐

#### 2.2.3 技术规格
- **货源平台API**：1688 OpenAPI、淘宝开放平台API
- **网页抓取**：Playwright无头浏览器，反爬虫策略
- **数据解析**：XPath/CSS选择器，动态内容处理
- **推荐算法**：协同过滤 + 内容推荐混合算法
- **评估模型**：多维度加权评估模型

### 2.3 智能采购系统

#### 2.3.1 功能描述
基于销售预测、库存情况和货源推荐，自动生成采购订单，支持一键采购。

#### 2.3.2 功能列表
1. **采购需求分析**
   - **库存分析**：分析当前库存水平和安全库存
   - **销售预测**：基于历史销售数据预测未来需求
   - **季节性分析**：考虑季节性因素调整采购计划
   - **促销计划**：考虑促销活动增加采购量
   - **需求计算**：计算实际采购需求数量

2. **采购计划生成**
   - **自动生成**：基于需求分析自动生成采购计划
   - **手动调整**：支持手动调整采购数量和时间
   - **分批采购**：支持分批采购计划
   - **采购时间规划**：考虑采购周期和到货时间
   - **预算控制**：采购预算规划和监控

3. **采购订单管理**
   - **采购单创建**：创建采购订单，选择供应商
   - **采购单审批**：采购单审批流程（多级审批）
   - **采购单状态**：跟踪采购单状态（待审批、已下单、已发货、已收货）
   - **采购单修改**：采购单修改和变更记录
   - **采购单取消**：采购单取消和原因记录

4. **一键采购**
   - **自动下单**：在货源平台自动下单（1688等）
   - **下单模板**：预定义下单模板和规则
   - **订单确认**：自动确认订单和支付（可选）
   - **订单跟踪**：自动跟踪采购订单状态
   - **异常处理**：采购异常自动告警和处理

5. **采购执行跟踪**
   - **发货跟踪**：跟踪供应商发货状态
   - **物流跟踪**：跟踪采购商品物流信息
   - **到货验收**：到货验收和质量检查
   - **入库处理**：采购商品入库操作
   - **付款处理**：采购付款申请和处理

6. **采购分析**
   - **采购成本分析**：采购成本统计和分析
   - **供应商绩效**：供应商绩效评估和分析
   - **采购效率分析**：采购周期和效率分析
   - **库存周转分析**：采购对库存周转的影响
   - **成本节约分析**：智能采购带来的成本节约

#### 2.3.3 技术规格
- **自动下单**：货源平台自动化操作（RPA）
- **工作流引擎**：采购审批和工作流引擎
- **预测模型**：时间序列预测 + 机器学习模型
- **成本计算**：采购成本完整计算模型（含运费、关税等）
- **集成对接**：与v1.0库存、订单系统深度集成

### 2.4 高级库存管理

#### 2.4.1 功能描述
在v1.0基础库存管理上，增加智能补货、库存优化、高级分析功能。

#### 2.4.2 功能列表
1. **智能补货系统**
   - **补货计算**：基于销售预测和安全库存计算补货量
   - **补货时机**：基于采购周期确定最佳补货时机
   - **补货建议**：生成具体的补货商品和数量建议
   - **补货审批**：补货建议审批流程
   - **自动补货**：支持自动创建采购单补货

2. **库存优化**
   - **安全库存优化**：基于需求波动优化安全库存水平
   - **库存分布优化**：多仓库库存分布优化建议
   - **库存结构优化**：商品库存结构优化分析
   - **滞销品处理**：滞销品识别和处理建议
   - **库存健康度**：库存健康度综合评分

3. **高级库存分析**
   - **库存周转分析**：商品、品类、仓库多维度周转分析
   - **库龄分析**：库存商品库龄分析和预警
   - **缺货分析**：缺货原因分析和改进建议
   - **过剩分析**：库存过剩原因分析和处理建议
   - **库存价值分析**：库存价值统计和分析

4. **库存预测**
   - **需求预测**：基于历史数据预测未来库存需求
   - **到货预测**：基于采购订单预测未来到货
   - **库存水平预测**：预测未来库存水平变化
   - **预警预测**：预测未来可能的库存预警
   - **可视化预测**：库存预测结果可视化展示

5. **库存报表**
   - **库存日报**：每日库存变化报告
   - **库存周报**：每周库存分析报告
   - **库存月报**：每月库存综合报告
   - **自定义报表**：自定义库存分析报表
   - **报表导出**：报表Excel/PDF导出

#### 2.4.3 技术规格
- **预测算法**：ARIMA、Prophet、LSTM等预测模型
- **优化算法**：线性规划、库存优化算法
- **实时计算**：流式计算库存指标
- **数据仓库**：库存分析专用数据仓库
- **可视化库**：ECharts高级图表库

### 2.5 数据仪表板与分析

#### 2.5.1 功能描述
提供多维度业务数据分析和可视化仪表板，支持数据驱动决策。

#### 2.5.2 功能列表
1. **综合仪表板**
   - **核心指标**：销售额、订单量、利润、库存周转等核心指标
   - **趋势图表**：销售趋势、订单趋势、流量趋势等
   - **对比分析**：同比、环比、目标对比分析
   - **实时数据**：实时销售数据、订单数据
   - **预警面板**：关键指标异常预警

2. **销售分析**
   - **销售概况**：总体销售情况分析
   - **商品分析**：热销商品、滞销商品分析
   - **平台分析**：各平台销售对比分析
   - **时间分析**：按日、周、月、季度、年分析
   - **地区分析**：销售地区分布分析

3. **商品分析**
   - **商品表现**：商品销售、利润、转化率分析
   - **品类分析**：商品品类销售分析
   - **价格分析**：价格敏感度、最优价格分析
   - **库存分析**：商品库存周转和健康度
   - **关联分析**：商品关联销售分析

4. **客户分析**
   - **客户概况**：客户数量、活跃度、价值分析
   - **客户分层**：VIP客户、重要客户、普通客户分析
   - **客户行为**：购买频率、客单价、复购率分析
   - **客户获取**：新客户获取成本和价值分析
   - **客户留存**：客户留存率和流失分析

5. **采购分析**
   - **采购概况**：采购金额、数量、频次分析
   - **供应商分析**：供应商绩效和成本分析
   - **采购效率**：采购周期、到货准时率分析
   - **成本分析**：采购成本构成和优化分析
   - **库存影响**：采购对库存的影响分析

6. **自定义分析**
   - **自定义指标**：自定义计算指标和公式
   - **自定义维度**：自定义分析维度和分组
   - **自定义图表**：自定义图表类型和样式
   - **保存分析**：保存常用分析视图
   - **分享分析**：分析结果分享和协作

#### 2.5.3 技术规格
- **数据仓库**：OLAP数据仓库，支持快速多维分析
- **ETL管道**：数据抽取、转换、加载管道
- **BI引擎**：开源BI引擎（Superset或Metabase）
- **缓存策略**：分析结果多级缓存
- **实时更新**：准实时数据更新（分钟级）

## 3. 用户故事与验收标准

### 3.1 AIGC内容生成

#### 用户故事13：商品文案AI生成
**作为** 运营人员
**我希望** 系统自动生成商品上架文案
**以便** 快速完成商品上架，节省内容创作时间

**验收标准**：
1. 在商品编辑页面提供"AI生成文案"按钮
2. 选择生成类型：标题、描述、卖点、SEO关键词
3. 选择目标语言：中文、英文、俄文等
4. 选择文案风格：专业、活泼、简洁、详细等
5. 生成结果显示在编辑框，支持编辑和调整
6. 支持批量生成多个商品的文案
7. 生成历史保存，可查看和复用
8. 生成成本显示（API调用费用）

#### 用户故事14：商品图片AI生成
**作为** 设计师
**我希望** 系统基于商品原图生成营销图片
**以便** 快速获得多种风格的营销素材

**验收标准**：
1. 在商品图片管理页面提供"AI生成图片"功能
2. 选择图片类型：主图、详情图、场景图、营销图
3. 选择图片风格：白底图、场景图、模特图、插画风等
4. 选择图片尺寸：平台要求的各种尺寸模板
5. 支持背景替换和商品增强
6. 生成图片预览和下载
7. 支持批量生成多个商品的图片
8. 生成图片质量达到商用标准

### 3.2 采购源管理

#### 用户故事15：货源平台商品抓取
**作为** 采购人员
**我希望** 通过商品链接自动抓取货源信息
**以便** 快速找到优质采购源

**验收标准**：
1. 在采购源页面提供"链接导入"功能
2. 支持1688、淘宝、拼多多等平台链接
3. 自动识别链接平台和商品ID
4. 抓取商品信息：标题、图片、价格、库存、评价
5. 抓取供应商信息：店铺名称、评分、联系方式
6. 抓取结果保存为采购源记录
7. 支持批量链接导入
8. 抓取失败时显示错误原因

#### 用户故事16：智能货源推荐
**作为** 采购经理
**我希望** 系统推荐优质采购源
**以便** 做出更好的采购决策

**验收标准**：
1. 在商品详情页显示"推荐货源"模块
2. 推荐算法考虑：价格、质量、交期、可靠性
3. 每个推荐货源显示：价格、评分、交期、推荐理由
4. 支持手动调整推荐权重（价格优先、质量优先等）
5. 支持查看货源详情和对比
6. 推荐准确率 > 70%（基于历史采购数据）
7. 支持反馈推荐质量（有用/无用）
8. 推荐算法基于反馈持续优化

### 3.3 智能采购

#### 用户故事17：自动采购计划生成
**作为** 库存管理员
**我希望** 系统自动生成采购计划
**以便** 及时补货避免缺货

**验收标准**：
1. 系统每天自动分析库存和销售数据
2. 自动计算补货需求：商品、数量、时间
3. 采购计划显示：商品、当前库存、安全库存、建议采购量
4. 支持手动调整采购计划
5. 采购计划审批流程（可选）
6. 自动生成采购计划报告
7. 采购计划基于销售预测，预测准确率 > 60%
8. 缺货率降低 > 30%（相比手动采购）

#### 用户故事18：一键采购下单
**作为** 采购专员
**我希望** 在系统内一键完成采购下单
**以便** 提高采购效率

**验收标准**：
1. 在采购计划页面提供"一键采购"按钮
2. 自动选择最优货源（基于推荐算法）
3. 自动填写采购数量、收货地址等信息
4. 支持1688等平台自动下单（需预先授权）
5. 下单成功显示订单号和预计发货时间
6. 下单失败显示原因和重试选项
7. 采购订单自动同步到系统
8. 采购效率提升 > 50%（相比手动下单）

### 3.4 高级库存

#### 用户故事19：智能补货建议
**作为** 运营总监
**我希望** 系统提供智能补货建议
**以便** 优化库存水平和资金占用

**验收标准**：
1. 库存页面显示"补货建议"模块
2. 建议基于：销售预测、采购周期、安全库存
3. 每个建议显示：商品、建议数量、建议时间、理由
4. 支持一键接受建议生成采购计划
5. 支持调整建议参数（安全库存系数、预测周期等）
6. 建议采纳率 > 50%
7. 采纳建议后缺货率降低 > 40%
8. 库存周转率提升 > 20%

#### 用户故事20：库存健康度分析
**作为** 财务人员
**我希望** 分析库存健康度
**以便** 优化资金使用和库存管理

**验收标准**：
1. 库存分析页面显示"健康度评分"
2. 评分维度：周转率、库龄、缺货率、过剩率
3. 健康度分级：优秀、良好、一般、差
4. 每个维度提供详细分析和改进建议
5. 历史健康度趋势图表
6. 健康度异常预警（评分低于阈值）
7. 支持导出健康度分析报告
8. 健康度评分与实际业务表现一致

### 3.5 数据仪表板

#### 用户故事21：业务数据可视化
**作为** 企业主
**我希望** 在一个仪表板查看所有关键业务数据
**以便** 快速了解业务状况和做出决策

**验收标准**：
1. 仪表板页面显示核心业务指标卡片
2. 指标包括：今日销售额、订单量、利润、库存周转等
3. 趋势图表显示近7天/30天数据变化
4. 平台对比图表显示各平台表现
5. 实时数据更新（分钟级）
6. 指标异常高亮显示（下降、超阈值等）
7. 支持钻取查看详细数据
8. 支持自定义仪表板布局和指标

#### 用户故事22：销售深度分析
**作为** 数据分析师
**我希望** 深度分析销售数据
**以便** 发现业务问题和优化机会

**验收标准**：
1. 销售分析页面提供多维度分析功能
2. 时间维度：日、周、月、季度、年、自定义
3. 商品维度：单品、品类、品牌、价格段
4. 平台维度：各平台对比分析
5. 客户维度：新老客户、客户层级、地区
6. 高级分析：趋势分析、对比分析、占比分析
7. 支持自定义分析维度和指标
8. 分析结果支持图表、表格、导出

## 4. UI/UX设计

### 4.1 AIGC内容工作室

#### 4.1.1 设计理念
- **创作流设计**：引导式内容创作流程，降低使用门槛
- **实时预览**：生成内容实时预览，所见即所得
- **批量处理**：支持批量生成，提高效率
- **模板化**：提供内容模板，快速生成标准内容

#### 4.1.2 核心页面
1. **AIGC工作台**
   - **布局**：左侧导航（文案、图片、视频），右侧工作区
   - **功能**：选择生成类型、设置参数、开始生成
   - **预览**：实时预览生成结果
   - **操作**：应用、保存、重新生成、导出

2. **文案生成器**
   - **输入**：商品基本信息、关键词、参考文案
   - **设置**：语言选择、风格选择、长度控制
   - **输出**：标题、描述、卖点、SEO关键词
   - **编辑**：在线编辑生成文案，支持富文本

3. **图片生成器**
   - **上传**：商品原图上传
   - **设置**：图片类型、风格、尺寸、背景
   - **预览**：生成图片缩略图预览
   - **下载**：下载高清图片，多种格式支持

4. **视频生成器**
   - **素材**：图片/视频素材上传
   - **设置**：视频类型、时长、配乐、字幕
   - **预览**：视频预览播放
   - **导出**：导出视频文件，多种分辨率和格式

5. **内容库**
   - **浏览**：按商品、类型、时间浏览生成内容
   - **搜索**：按关键词搜索内容
   - **管理**：内容分类、标签、删除
   - **复用**：复用历史内容到新商品

### 4.2 采购管理中心

#### 4.2.1 设计理念
- **决策支持**：提供充分信息支持采购决策
- **流程引导**：引导用户完成采购全流程
- **对比分析**：多货源对比，辅助决策
- **自动化**：尽可能自动化重复操作

#### 4.2.2 核心页面
1. **采购仪表板**
   - **概览**：待采购商品、采购预算、供应商状态
   - **预警**：库存预警、价格异常、供应商风险
   - **待办**：待审批采购单、待处理采购任务
   - **统计**：采购金额、数量、成本节约统计

2. **采购源发现**
   - **搜索**：商品关键词搜索货源
   - **导入**：链接导入商品信息
   - **推荐**：智能推荐优质货源
   - **对比**：多货源对比表格

3. **采购计划**
   - **列表**：采购计划列表，按状态分类
   - **详情**：计划详情，商品清单、数量、时间
   - **审批**：采购计划审批流程界面
   - **执行**：从计划到采购单的执行跟踪

4. **采购订单**
   - **创建**：创建采购订单，选择供应商和商品
   - **管理**：采购订单列表，按状态筛选
   - **跟踪**：订单状态跟踪，发货、物流、到货
   - **付款**：采购付款申请和处理

5. **供应商管理**
   - **目录**：供应商目录，按分类浏览
   - **详情**：供应商详细信息，合作历史
   - **评估**：供应商评估和评分
   - **沟通**：供应商沟通记录

### 4.3 高级库存管理

#### 4.3.1 设计理念
- **可视化**：库存数据可视化展示
- **预测性**：显示库存预测和趋势
- **行动导向**：直接提供可执行建议
- **深度分析**：提供深度库存分析工具

#### 4.3.2 核心页面
1. **库存健康度仪表板**
   - **评分**：库存健康度综合评分
   - **指标**：周转率、库龄、缺货率、过剩率
   - **趋势**：健康度趋势图表
   - **预警**：健康度异常预警

2. **智能补货**
   - **建议列表**：补货建议商品列表
   - **详情**：建议详情，计算依据
   - **调整**：调整建议参数
   - **执行**：一键生成采购计划

3. **库存分析**
   - **多维分析**：多维度库存数据分析
   - **深度钻取**：从汇总数据钻取到明细
   - **对比分析**：历史对比、目标对比
   - **报告生成**：生成库存分析报告

4. **库存预测**
   - **需求预测**：未来库存需求预测图表
   - **到货预测**：基于采购单的到货预测
   - **水平预测**：未来库存水平预测
   - **预警预测**：未来可能预警预测

### 4.4 数据仪表板

#### 4.4.1 设计理念
- **一目了然**：关键数据一目了然
- **可交互**：支持数据钻取和筛选
- **可定制**：用户可定制关注指标
- **实时性**：准实时数据更新

#### 4.4.2 核心页面
1. **综合仪表板**
   - **指标卡片**：核心指标卡片，突出显示
   - **趋势图表**：主要指标趋势折线图
   - **对比图表**：平台、商品、时间对比
   - **实时看板**：实时销售和订单看板

2. **销售分析**
   - **概览**：销售总体情况
   - **趋势**：销售趋势分析
   - **构成**：销售构成分析（商品、平台、地区）
   - **深度分析**：高级销售分析工具

3. **商品分析**
   - **表现分析**：商品销售表现排名
   - **关联分析**：商品关联销售分析
   - **价格分析**：价格敏感度和优化分析
   - **库存分析**：商品库存和销售关联分析

4. **客户分析**
   - **分层分析**：客户分层和表现分析
   - **行为分析**：客户购买行为分析
   - **价值分析**：客户生命周期价值分析
   - **留存分析**：客户留存和流失分析

5. **自定义分析**
   - **构建器**：拖拽式分析构建器
   - **保存**：保存自定义分析视图
   - **分享**：分享分析结果
   - **模板**：分析模板库

## 5. API设计

### 5.1 AIGC API

#### 5.1.1 文案生成API
**端点**：`POST /api/v2/aigc/generate-text`
**请求**：
```json
{
  "product_id": "product_123",
  "generation_type": "description", // title, description, bullet_points, seo_keywords
  "language": "zh-CN", // zh-CN, en-US, ru-RU
  "style": "professional", // professional, casual, concise, detailed
  "additional_prompt": "强调防水功能",
  "reference_texts": ["参考文案1", "参考文案2"]
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "generation_id": "gen_123",
    "content": "这是一款高品质的无线蓝牙耳机...",
    "estimated_cost": 0.02, // 美元
    "generation_time": 3.5, // 秒
    "model_used": "gpt-4"
  }
}
```

#### 5.1.2 图片生成API
**端点**：`POST /api/v2/aigc/generate-image`
**请求**：
```json
{
  "product_id": "product_123",
  "image_type": "main_image", // main_image, detail_image, scene_image, marketing_image
  "style": "white_background", // white_background, lifestyle, model, illustration
  "source_image_url": "https://.../original.jpg",
  "size": {
    "width": 800,
    "height": 800
  },
  "prompt": "无线蓝牙耳机，高端质感，自然光"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "generation_id": "gen_456",
    "image_url": "https://.../generated.jpg",
    "thumbnail_url": "https://.../thumbnail.jpg",
    "estimated_cost": 0.15,
    "generation_time": 12.5,
    "model_used": "stable-diffusion-xl"
  }
}
```

### 5.2 采购API

#### 5.2.1 货源搜索API
**端点**：`POST /api/v2/sourcing/search`
**请求**：
```json
{
  "query": "无线蓝牙耳机",
  "platforms": ["1688", "taobao"], // 1688, taobao, pinduoduo
  "filters": {
    "min_price": 50,
    "max_price": 200,
    "min_rating": 4.0,
    "location": "广东"
  },
  "limit": 20
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "source_123",
        "platform": "1688",
        "title": "无线蓝牙耳机 高音质 运动防水",
        "price": 89.50,
        "min_order_quantity": 10,
        "image_url": "https://...",
        "supplier": {
          "name": "XX电子有限公司",
          "rating": 4.8,
          "response_rate": 95.2
        },
        "delivery_time": "3-5天",
        "recommendation_score": 0.87
      }
    ],
    "total_results": 1250
  }
}
```

#### 5.2.2 采购计划生成API
**端点**：`POST /api/v2/purchasing/generate-plan`
**请求**：
```json
{
  "product_ids": ["product_123", "product_456"],
  "plan_type": "auto", // auto, manual
  "parameters": {
    "safety_stock_factor": 1.2,
    "forecast_period_days": 30,
    "lead_time_days": 7
  }
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "plan_id": "plan_789",
    "items": [
      {
        "product_id": "product_123",
        "product_title": "无线蓝牙耳机",
        "current_stock": 50,
        "safety_stock": 60,
        "forecast_demand": 200,
        "recommended_quantity": 210,
        "recommended_sources": [
          {
            "source_id": "source_123",
            "price": 89.50,
            "total_cost": 18795.00
          }
        ]
      }
    ],
    "total_cost": 18795.00,
    "estimated_savings": 2350.00
  }
}
```

### 5.3 库存分析API

#### 5.3.1 库存健康度API
**端点**：`GET /api/v2/inventory/health`
**查询参数**：
- `warehouse_id`：仓库ID（可选）
- `category_id`：品类ID（可选）
- `time_range`：时间范围（7d, 30d, 90d）

**响应**：
```json
{
  "success": true,
  "data": {
    "overall_score": 78.5,
    "dimensions": {
      "turnover": {
        "score": 82.3,
        "value": 4.2,
        "unit": "次/年",
        "trend": "improving",
        "recommendation": "周转率良好，继续保持"
      },
      "aging": {
        "score": 65.4,
        "value": 45,
        "unit": "天",
        "trend": "worsening",
        "recommendation": "库龄偏长，建议促销清仓"
      },
      "stockout": {
        "score": 91.2,
        "value": 2.3,
        "unit": "%",
        "trend": "stable",
        "recommendation": "缺货率控制良好"
      },
      "excess": {
        "score": 75.1,
        "value": 12.5,
        "unit": "%",
        "trend": "improving",
        "recommendation": "过剩库存逐步改善"
      }
    },
    "top_concerns": [
      {
        "product_id": "product_789",
        "product_title": "过季服装",
        "issue": "库龄超过180天",
        "suggestion": "设置促销活动清理库存"
      }
    ]
  }
}
```

#### 5.3.2 库存预测API
**端点**：`POST /api/v2/inventory/forecast`
**请求**：
```json
{
  "product_ids": ["product_123", "product_456"],
  "forecast_horizon_days": 30,
  "include_purchase_orders": true,
  "confidence_level": 0.95
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "forecasts": [
      {
        "product_id": "product_123",
        "product_title": "无线蓝牙耳机",
        "current_stock": 50,
        "daily_forecast": {
          "mean": 15.2,
          "std": 3.1,
          "p95_low": 9.3,
          "p95_high": 21.1
        },
        "stockout_risk": {
          "days_until_stockout": 3.3,
          "probability_7d": 0.85,
          "probability_14d": 0.95
        },
        "recommendation": {
          "action": "urgent_purchase",
          "quantity": 200,
          "timing": "immediate"
        }
      }
    ]
  }
}
```

### 5.4 数据分析API

#### 5.4.1 销售分析API
**端点**：`GET /api/v2/analytics/sales`
**查询参数**：
- `start_date`：开始日期
- `end_date`：结束日期
- `group_by`：分组维度（day, week, month, product, platform, category）
- `metrics`：指标（revenue, orders, quantity, profit）
- `filters`：筛选条件JSON

**响应**：
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_revenue": 125000.50,
      "total_orders": 1250,
      "total_quantity": 3250,
      "total_profit": 31250.25,
      "avg_order_value": 100.00,
      "growth_rate": 0.15
    },
    "trend": [
      {
        "period": "2026-02-01",
        "revenue": 4500.00,
        "orders": 45,
        "quantity": 120,
        "profit": 1125.00
      }
    ],
    "breakdown": {
      "by_platform": [
        {
          "platform": "ozon",
          "revenue": 75000.30,
          "orders": 750,
          "percentage": 0.60
        }
      ],
      "by_product": [
        {
          "product_id": "product_123",
          "product_title": "无线蓝牙耳机",
          "revenue": 25000.00,
          "quantity": 500,
          "percentage": 0.20
        }
      ],
      "by_category": [
        {
          "category": "电子产品",
          "revenue": 100000.00,
          "percentage": 0.80
        }
      ]
    }
  }
}
```

#### 5.4.2 实时指标API
**端点**：`GET /api/v2/analytics/realtime`
**响应**：
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-18T14:30:00Z",
    "metrics": {
      "revenue_today": 12500.50,
      "orders_today": 125,
      "customers_today": 85,
      "conversion_rate": 2.5,
      "avg_order_value": 100.00,
      "top_products": [
        {
          "product_id": "product_123",
          "title": "无线蓝牙耳机",
          "quantity": 25,
          "revenue": 5000.00
        }
      ],
      "platform_performance": [
        {
          "platform": "ozon",
          "revenue": 7500.00,
          "orders": 75
        }
      ]
    },
    "alerts": [
      {
        "type": "stockout_risk",
        "product_id": "product_456",
        "message": "商品库存低于安全库存",
        "severity": "high"
      }
    ]
  }
}
```

## 6. 数据库设计（扩展）

### 6.1 AIGC相关表

#### 6.1.1 AIGC任务表
```sql
CREATE TABLE aigc_tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    task_type VARCHAR(20) NOT NULL, -- text, image, video
    task_subtype VARCHAR(30), -- title, description, main_image, etc.
    product_id VARCHAR(36) REFERENCES products(id) ON DELETE CASCADE,
    input_parameters JSONB NOT NULL,
    output_result JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    actual_cost DECIMAL(10, 4) DEFAULT 0,
    model_used VARCHAR(50),
    generation_time DECIMAL(10, 2), -- 秒
    error_message TEXT,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aigc_tasks_team_status ON aigc_tasks(team_id, status);
CREATE INDEX idx_aigc_tasks_product ON aigc_tasks(product_id);
CREATE INDEX idx_aigc_tasks_created_at ON aigc_tasks(created_at DESC);
```

#### 6.1.2 AIGC内容表
```sql
CREATE TABLE aigc_contents (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    content_type VARCHAR(20) NOT NULL, -- text, image, video
    content_subtype VARCHAR(30) NOT NULL, -- title, description, main_image, etc.
    content_data JSONB NOT NULL, -- 文本内容或文件元数据
    language VARCHAR(10), -- 语言代码
    style VARCHAR(30), -- 风格
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    applied_to_platform BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMPTZ,
    task_id VARCHAR(36) REFERENCES aigc_tasks(id),
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aigc_contents_product_type ON aigc_contents(product_id, content_type);
CREATE INDEX idx_aigc_contents_active ON aigc_contents(team_id, is_active);
CREATE INDEX idx_aigc_contents_version ON aigc_contents(product_id, content_type, version DESC);
```

#### 6.1.3 AIGC模板表
```sql
CREATE TABLE aigc_templates (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type VARCHAR(20) NOT NULL, -- text, image, video
    template_subtype VARCHAR(30) NOT NULL,
    prompt_template TEXT NOT NULL,
    parameters JSONB DEFAULT '{}',
    language VARCHAR(10),
    style VARCHAR(30),
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aigc_templates_team_type ON aigc_templates(team_id, template_type);
CREATE INDEX idx_aigc_templates_default ON aigc_templates(team_id, is_default);
```

### 6.2 采购相关表

#### 6.2.1 供应商表
```sql
CREATE TABLE suppliers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50),
    type VARCHAR(20) DEFAULT 'manufacturer', -- manufacturer, wholesaler, distributor, dropshipper
    contact_info JSONB NOT NULL, -- {contact_person, phone, email, address}
    platform_info JSONB, -- {platform, platform_supplier_id, shop_url}
    rating DECIMAL(3, 2) DEFAULT 0, -- 综合评分 0-5
    rating_details JSONB DEFAULT '{
        "price": 0,
        "quality": 0,
        "delivery": 0,
        "service": 0,
        "communication": 0
    }',
    total_orders INTEGER DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    payment_terms TEXT,
    delivery_terms TEXT,
    minimum_order_quantity INTEGER,
    lead_time_days INTEGER,
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, blacklisted
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name)
);

CREATE INDEX idx_suppliers_team_rating ON suppliers(team_id, rating DESC);
CREATE INDEX idx_suppliers_type ON suppliers(type);
CREATE INDEX idx_suppliers_status ON suppliers(status);
```

#### 6.2.2 采购源表
```sql
CREATE TABLE sourcing_sources (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    supplier_id VARCHAR(36) REFERENCES suppliers(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL, -- 1688, taobao, pinduoduo, etc.
    platform_product_id VARCHAR(100),
    platform_url TEXT,
    title VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    min_order_quantity INTEGER DEFAULT 1,
    available_quantity INTEGER,
    images JSONB DEFAULT '[]',
    specifications JSONB, -- 规格参数
    rating DECIMAL(3, 2), -- 平台评分
    review_count INTEGER,
    delivery_info JSONB, -- 发货信息
    shipping_cost DECIMAL(10, 2),
    estimated_delivery_days INTEGER,
    last_checked_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    recommendation_score DECIMAL(3, 2), -- 推荐分数 0-1
    recommendation_reasons TEXT[], -- 推荐理由
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, product_id, platform, platform_product_id)
);

CREATE INDEX idx_sourcing_sources_product ON sourcing_sources(product_id);
CREATE INDEX idx_sourcing_sources_recommendation ON sourcing_sources(team_id, recommendation_score DESC);
CREATE INDEX idx_sourcing_sources_price ON sourcing_sources(product_id, price);
```

#### 6.2.3 采购计划表
```sql
CREATE TABLE purchase_plans (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    plan_number VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    plan_type VARCHAR(20) DEFAULT 'auto', -- auto, manual
    status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, approved, rejected, executed
    total_items INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10, 2) DEFAULT 0,
    estimated_savings DECIMAL(10, 2) DEFAULT 0,
    parameters JSONB, -- 生成参数
    approval_flow JSONB, -- 审批流程
    approved_by VARCHAR(36) REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    notes TEXT,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchase_plans_team_status ON purchase_plans(team_id, status);
CREATE INDEX idx_purchase_plans_created_at ON purchase_plans(created_at DESC);
```

#### 6.2.4 采购计划明细表
```sql
CREATE TABLE purchase_plan_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id VARCHAR(36) NOT NULL REFERENCES purchase_plans(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    current_stock INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    forecast_demand INTEGER NOT NULL,
    recommended_quantity INTEGER NOT NULL,
    recommended_source_id VARCHAR(36) REFERENCES sourcing_sources(id),
    estimated_unit_cost DECIMAL(10, 2),
    estimated_total_cost DECIMAL(10, 2),
    priority INTEGER DEFAULT 1, -- 优先级 1-5
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchase_plan_items_plan ON purchase_plan_items(plan_id);
CREATE INDEX idx_purchase_plan_items_product ON purchase_plan_items(product_id);
```

#### 6.2.5 采购订单表
```sql
CREATE TABLE purchase_orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    order_number VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(36) NOT NULL REFERENCES suppliers(id),
    plan_id VARCHAR(36) REFERENCES purchase_plans(id),
    status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, confirmed, shipped, received, cancelled
    total_amount DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'CNY',
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_cost DECIMAL(10, 2) DEFAULT 0,
    payment_terms TEXT,
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, partial, paid
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, order_number)
);

CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_delivery_date ON purchase_orders(expected_delivery_date);
```

#### 6.2.6 采购订单明细表
```sql
CREATE TABLE purchase_order_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(36) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id),
    variant_id VARCHAR(36) REFERENCES product_variants(id),
    sourcing_source_id VARCHAR(36) REFERENCES sourcing_sources(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    received_quantity INTEGER DEFAULT 0,
    quality_status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected, partial
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchase_order_items_order ON purchase_order_items(order_id);
CREATE INDEX idx_purchase_order_items_product ON purchase_order_items(product_id);
```

### 6.3 库存分析表

#### 6.3.1 库存健康度表
```sql
CREATE TABLE inventory_health_scores (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL,
    overall_score DECIMAL(5, 2) NOT NULL, -- 0-100
    dimension_scores JSONB NOT NULL, -- {turnover: 82.3, aging: 65.4, stockout: 91.2, excess: 75.1}
    product_count INTEGER DEFAULT 0,
    healthy_count INTEGER DEFAULT 0, -- 健康商品数
    warning_count INTEGER DEFAULT 0, -- 警告商品数
    critical_count INTEGER DEFAULT 0, -- 严重商品数
    top_issues JSONB, -- 主要问题商品
    recommendations JSONB, -- 改进建议
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, calculation_date)
);

CREATE INDEX idx_inventory_health_dates ON inventory_health_scores(calculation_date DESC);
CREATE INDEX idx_inventory_health_score ON inventory_health_scores(team_id, overall_score);
```

#### 6.3.2 库存预测表
```sql
CREATE TABLE inventory_forecasts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    forecast_type VARCHAR(20) NOT NULL, -- demand, stock_level, stockout_risk
    horizon_days INTEGER NOT NULL, -- 预测 horizon
    forecast_values JSONB NOT NULL, -- 预测值
    confidence_intervals JSONB, -- 置信区间
    model_used VARCHAR(50),
    model_parameters JSONB,
    accuracy_metrics JSONB, -- 准确度指标
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, product_id, variant_id, forecast_date, forecast_type, horizon_days)
);

CREATE INDEX idx_inventory_forecasts_product ON inventory_forecasts(product_id, forecast_date);
CREATE INDEX idx_inventory_forecasts_date_type ON inventory_forecasts(forecast_date, forecast_type);
```

#### 6.3.3 库存周转表
```sql
CREATE TABLE inventory_turnover (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id VARCHAR(36) REFERENCES product_variants(id) ON DELETE CASCADE,
    warehouse_id VARCHAR(36) REFERENCES warehouses(id) ON DELETE CASCADE,
    period_type VARCHAR(10) NOT NULL, -- daily, weekly, monthly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    beginning_inventory INTEGER NOT NULL,
    ending_inventory INTEGER NOT NULL,
    average_inventory DECIMAL(10, 2) NOT NULL,
    cost_of_goods_sold DECIMAL(10, 2) NOT NULL,
    turnover_rate DECIMAL(10, 2) NOT NULL, -- 周转率
    turnover_days DECIMAL(10, 2) NOT NULL, -- 周转天数
    sales_quantity INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, product_id, variant_id, warehouse_id, period_type, period_start)
);

CREATE INDEX idx_inventory_turnover_period ON inventory_turnover(period_start DESC);
CREATE INDEX idx_inventory_turnover_product ON inventory_turnover(product_id, period_start DESC);
```

### 6.4 分析数据表

#### 6.4.1 销售聚合表
```sql
CREATE TABLE sales_aggregates (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    aggregation_date DATE NOT NULL,
    aggregation_level VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    platform VARCHAR(20), -- 平台，NULL表示汇总
    product_id VARCHAR(36) REFERENCES products(id),
    category_id VARCHAR(36),
    metrics JSONB NOT NULL, -- {revenue: 1000, orders: 10, quantity: 50, profit: 200, ...}
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, aggregation_date, aggregation_level, platform, product_id, category_id)
);

CREATE INDEX idx_sales_aggregates_date ON sales_aggregates(aggregation_date DESC);
CREATE INDEX idx_sales_aggregates_product ON sales_aggregates(product_id, aggregation_date DESC);
CREATE INDEX idx_sales_aggregates_platform ON sales_aggregates(platform, aggregation_date DESC);
```

#### 6.4.2 客户分析表
```sql
CREATE TABLE customer_analytics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id VARCHAR(36) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    customer_id VARCHAR(36) NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    metrics JSONB NOT NULL, -- {total_orders: 15, total_spent: 12500.50, avg_order_value: 833.37, ...}
    segmentation JSONB, -- 客户分群信息
    lifecycle_stage VARCHAR(20), -- 生命周期阶段
    predicted_ltv DECIMAL(10, 2), -- 预测生命周期价值
    churn_risk DECIMAL(3, 2), -- 流失风险 0-1
    next_purchase_prediction DATE, -- 下次购买预测
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, customer_id, analysis_date)
);

CREATE INDEX idx_customer_analytics_date ON customer_analytics(analysis_date DESC);
CREATE INDEX idx_customer_analytics_ltv ON customer_analytics(team_id, predicted_ltv DESC);
CREATE INDEX idx_customer_analytics_churn ON customer_analytics(team_id, churn_risk DESC);
```

## 7. 集成设计

### 7.1 AIGC服务集成

#### 7.1.1 OpenAI集成
**服务配置**：
```python
class OpenAIService:
    """OpenAI服务集成"""
    
    def __init__(self, api_key: str, organization: str = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            organization=organization
        )
        self.cost_tracker = CostTracker()
    
    async def generate_text(self, prompt: str, model: str = "gpt-4", **kwargs) -> dict:
        """生成文本"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            generation_time = time.time() - start_time
            content = response.choices[0].message.content
            
            # 计算成本
            cost = self.calculate_cost(
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )
            
            self.cost_tracker.record_usage(model, cost)
            
            return {
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "cost": cost,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"OpenAI文本生成失败: {e}")
            raise
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算API调用成本"""
        # OpenAI定价（美元/千token）
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        }
        
        if model not in pricing:
            return 0.0
        
        cost = (prompt_tokens / 1000 * pricing[model]["input"] +
                completion_tokens / 1000 * pricing[model]["output"])
        
        return round(cost, 4)
```

#### 7.1.2 Stable Diffusion集成
**服务配置**：
```python
class StableDiffusionService:
    """Stable Diffusion服务集成"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.stability.ai"):
        self.client = AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.cost_tracker = CostTracker()
    
    async def generate_image(self, prompt: str, **kwargs) -> dict:
        """生成图片"""
        try:
            start_time = time.time()
            
            # 默认参数
            params = {
                "prompt": prompt,
                "output_format": "png",
                "height": 512,
                "width": 512,
                "steps": 30,
                "cfg_scale": 7.0,
                "samples": 1,
                "style_preset": "photographic",
                **kwargs
            }
            
            response = await self.client.post(
                "/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                json=params
            )
            response.raise_for_status()
            
            generation_time = time.time() - start_time
            
            # 解析响应
            data = response.json()
            
            # 计算成本（根据Stability AI定价）
            cost = self.calculate_cost(params)
            
            self.cost_tracker.record_usage("stable-diffusion", cost)
            
            # 返回base64编码的图片
            image_data = data["artifacts"][0]["base64"]
            
            return {
                "image_data": image_data,
                "model": "stable-diffusion-xl",
                "parameters": params,
                "cost": cost,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Stable Diffusion图片生成失败: {e}")
            raise
    
    def calculate_cost(self, params: dict) -> float:
        """计算图片生成成本"""
        # Stability AI定价
        # 假设每张图片 $0.002 - $0.01 根据复杂度和尺寸
        base_cost = 0.002
        size_multiplier = (params.get("width", 512) * params.get("height", 512)) / (512 * 512)
        steps_multiplier = params.get("steps", 30) / 30
        
        cost = base_cost * size_multiplier * steps_multiplier
        return round(cost, 4)
```

### 7.2 货源平台集成

#### 7.2.1 1688平台集成
**服务配置**：
```python
class Alibaba1688Service:
    """1688平台集成服务"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://gw.open.1688.com/openapi"
        
    async def search_products(self, keywords: str, **kwargs) -> List[dict]:
        """搜索商品"""
        try:
            # 构建API参数
            params = {
                "keywords": keywords,
                "pageNo": kwargs.get("page", 1),
                "pageSize": kwargs.get("limit", 20),
                "categoryId": kwargs.get("category_id"),
                "startPrice": kwargs.get("min_price"),
                "endPrice": kwargs.get("max_price"),
                "sortType": kwargs.get("sort", "totalQuantity_desc")
            }
            
            # 生成签名
            params["_aop_signature"] = self.generate_signature(params)
            params["_aop_timestamp"] = str(int(time.time() * 1000))
            
            response = await self._request(
                "GET",
                "/param2/1/com.alibaba.b2b.search.web/offerSearchService/searchOfferDetail",
                params=params
            )
            
            # 解析响应
            products = []
            for item in response.get("result", []):
                product = self._parse_product(item)
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"1688商品搜索失败: {e}")
            return []
    
    async def get_product_detail(self, product_id: str) -> dict:
        """获取商品详情"""
        try:
            params = {
                "offerId": product_id,
                "needReturnProtect": "true"
            }
            
            params["_aop_signature"] = self.generate_signature(params)
            params["_aop_timestamp"] = str(int(time.time() * 1000))
            
            response = await self._request(
                "GET",
                "/param2/1/com.alibaba.b2b.product.web/offerDetailService/getOfferDetail",
                params=params
            )
            
            return self._parse_product_detail(response)
            
        except Exception as e:
            logger.error(f"1688商品详情获取失败: {e}")
            return {}
    
    def generate_signature(self, params: dict) -> str:
        """生成API签名"""
        # 1688 API签名算法
        sorted_params = sorted(params.items())
        string_to_sign = self.app_secret
        for k, v in sorted_params:
            string_to_sign += f"{k}{v}"
        string_to_sign += self.app_secret
        
        signature = hashlib.md5(string_to_sign.encode()).hexdigest().upper()
        return signature
    
    def _parse_product(self, item: dict) -> dict:
        """解析商品数据"""
        return {
            "product_id": item.get("offerId"),
            "title": item.get("subject"),
            "price": float(item.get("price", 0)),
            "min_order_quantity": item.get("minOrderQuantity", 1),
            "image_url": item.get("imgUrl"),
            "supplier": {
                "name": item.get("companyName"),
                "rating": float(item.get("score", 0)),
                "response_rate": float(item.get("rate", 0))
            },
            "delivery_time": item.get("deliveryTime"),
            "platform": "1688"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs):
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        async with AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, **kwargs)
            else:
                response = await client.post(url, **kwargs)
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("errorCode"):
                raise Exception(f"1688 API错误: {data.get('errorMsg')}")
            
            return data
```

### 7.3 预测分析集成

#### 7.3.1 销售预测服务
```python
class SalesForecastService:
    """销售预测服务"""
    
    def __init__(self):
        self.models = {}
        
    async def train_forecast_model(self, product_id: str, historical_data: List[dict]) -> str:
        """训练预测模型"""
        try:
            # 准备数据
            df = self._prepare_dataframe(historical_data)
            
            # 选择模型
            if len(df) < 30:
                # 数据量少，使用简单模型
                model = self._train_simple_model(df)
                model_type = "moving_average"
            elif len(df) < 90:
                # 中等数据量，使用ARIMA
                model = self._train_arima_model(df)
                model_type = "arima"
            else:
                # 数据量充足，使用Prophet或LSTM
                model = self._train_prophet_model(df)
                model_type = "prophet"
            
            # 保存模型
            model_id = f"model_{product_id}_{int(time.time())}"
            self.models[model_id] = {
                "model": model,
                "type": model_type,
                "trained_at": datetime.now(),
                "product_id": product_id
            }
            
            # 评估模型
            evaluation = self._evaluate_model(model, df, model_type)
            
            return {
                "model_id": model_id,
                "model_type": model_type,
                "evaluation": evaluation,
                "trained_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"销售预测模型训练失败: {e}")
            raise
    
    async def forecast(self, model_id: str, horizon_days: int = 30) -> dict:
        """执行预测"""
        try:
            if model_id not in self.models:
                raise ValueError(f"模型不存在: {model_id}")
            
            model_info = self.models[model_id]
            model = model_info["model"]
            model_type = model_info["type"]
            
            # 执行预测
            if model_type == "moving_average":
                forecast = self._forecast_moving_average(model, horizon_days)
            elif model_type == "arima":
                forecast = self._forecast_arima(model, horizon_days)
            elif model_type == "prophet":
                forecast = self._forecast_prophet(model, horizon_days)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            # 添加置信区间
            forecast_with_ci = self._add_confidence_interval(forecast, model_type)
            
            return {
                "model_id": model_id,
                "forecast": forecast_with_ci,
                "horizon_days": horizon_days,
                "forecasted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"销售预测失败: {e}")
            raise
    
    def _prepare_dataframe(self, data: List[dict]) -> pd.DataFrame:
        """准备数据框"""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.asfreq('D').fillna(0)  # 填充缺失日期
        return df
    
    def _train_prophet_model(self, df: pd.DataFrame):
        """训练Prophet模型"""
        from prophet import Prophet
        
        # 准备Prophet格式数据
        prophet_df = df.reset_index()
        prophet_df = prophet_df.rename(columns={'date': 'ds', 'quantity': 'y'})
        
        # 创建并训练模型
        model = Prophet(
            seasonality_mode='multiplicative',
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        
        model.fit(prophet_df)
        return model
    
    def _forecast_prophet(self, model, horizon_days: int) -> dict:
        """Prophet模型预测"""
        future = model.make_future_dataframe(periods=horizon_days)
        forecast = model.predict(future)
        
        # 提取预测结果
        result = {}
        for _, row in forecast.tail(horizon_days).iterrows():
            date = row['ds'].strftime('%Y-%m-%d')
            result[date] = {
                'yhat': max(0, row['yhat']),  # 预测值
                'yhat_lower': max(0, row['yhat_lower']),  # 下限
                'yhat_upper': max(0, row['yhat_upper'])   # 上限
            }
        
        return result
    
    def _evaluate_model(self, model, df: pd.DataFrame, model_type: str) -> dict:
        """评估模型性能"""
        # 使用交叉验证或留出法评估
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        test_df = df.iloc[train_size:]
        
        # 重新训练（仅训练集）
        if model_type == "prophet":
            train_prophet_df = train_df.reset_index()
            train_prophet_df = train_prophet_df.rename(columns={'date': 'ds', 'quantity': 'y'})
            model_eval = Prophet()
            model_eval.fit(train_prophet_df)
            
            # 在测试集上预测
            future = model_eval.make_future_dataframe(periods=len(test_df))
            forecast_eval = model_eval.predict(future)
            forecast_eval = forecast_eval.tail(len(test_df))
            
            # 计算误差
            actual = test_df['quantity'].values
            predicted = forecast_eval['yhat'].values
            
        # 计算评估指标
        mae = np.mean(np.abs(actual - predicted))
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        return {
            "mae": float(mae),
            "mape": float(mape),
            "rmse": float(rmse),
            "train_size": len(train_df),
            "test_size": len(test_df)
        }
```

## 8. 部署与扩展

### 8.1 AIGC服务部署

#### 8.1.1 高可用部署架构
```
负载均衡器 (AWS ALB/NLB)
       |
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ AIGC网关  │ │ 文案服务  │ │ 图片服务  │
   │ (2副本)   │ │ (3副本)   │ │ (3副本)   │
   └─────────┘ └─────────┘ └─────────┘
   ┌─────────┐ ┌─────────┐
   │ 视频服务  │ │ 任务队列  │
   │ (2副本)   │ │ (Redis) │
   └─────────┘ └─────────┘
       |
   ┌─────────┐
   │ 模型服务  │
   │ (GPU实例) │
   └─────────┘
       |
  对象存储 (S3/MinIO)
```

#### 8.1.2 GPU资源配置
- **文案生成**：CPU实例即可，需要大内存
- **图片生成**：GPU实例（NVIDIA A10/T4），显存 >= 16GB
- **视频生成**：GPU实例（NVIDIA A100/V100），显存 >= 32GB
- **模型服务**：专用GPU集群，支持模型热加载

#### 8.1.3 成本控制策略
- **API调用限流**：用户级别API调用限制
- **成本监控**：实时监控AIGC服务成本
- **缓存策略**：生成内容缓存，减少重复生成
- **模型选择**：根据任务复杂度选择成本最优模型
- **预算预警**：用户预算使用预警

### 8.2 预测分析服务部署

#### 8.2.1 大数据处理架构
```
数据源 → Kafka → Flink流处理 → 特征存储
                     ↓
             模型训练服务
                     ↓
            模型注册表 (MLflow)
                     ↓
        预测服务 (实时/批量)
                     ↓
         结果存储 + 监控
```

#### 8.2.2 模型管理
- **模型版本控制**：使用MLflow管理模型版本
- **模型监控**：监控模型性能和漂移
- **自动重训练**：数据漂移时自动触发重训练
- **A/B测试**：新模型A/B测试验证效果
- **回滚机制**：模型性能下降时自动回滚

#### 8.2.3 性能优化
- **特征缓存**：常用特征预计算和缓存
- **批量预测**：支持批量预测提高效率
- **分布式预测**：大规模预测分布式处理
- **模型压缩**：模型压缩减少推理时间
- **硬件加速**：GPU/TPU加速模型推理

## 9. 开发路线图

### 9.1 v2.0开发阶段（v1.0后3个月）

#### 第1-2月：AIGC内容生成系统
- **AIGC基础架构**：
  - AIGC服务框架搭建
  - OpenAI/Stable Diffusion API集成
  - 内容生成任务队列
  - 内容存储和管理
  
- **文案生成**：
  - 商品标题生成
  - 商品描述生成
  - SEO关键词生成
  - 多语言支持
  
- **图片生成**：
  - 商品主图生成
  - 详情图生成
  - 营销图生成
  - 图片编辑和管理

#### 第3-4月：采购自动化系统
- **货源平台集成**：
  - 1688平台API集成
  - 淘宝/天猫商品抓取
  - 货源数据解析和标准化
  - 货源质量评估
  
- **智能采购**：
  - 采购需求分析算法
  - 采购计划自动生成
  - 采购审批工作流
  - 采购订单管理
  
- **供应商管理**：
  - 供应商信息管理
  - 供应商评估体系
  - 供应商沟通记录
  - 供应商绩效分析

#### 第5-6月：高级库存与数据分析
- **高级库存管理**：
  - 智能补货算法
  - 库存健康度分析
  - 库存预测模型
  - 库存优化建议
  
- **数据分析平台**：
  - 数据仓库建设
  - ETL数据处理管道
  - 数据分析仪表板
  - 自定义分析工具
  
- **系统集成与优化**：
  - 与v1.0系统深度集成
  - 性能测试和优化
  - 用户测试和反馈
  - 生产环境部署

### 9.2 关键里程碑

#### 里程碑1：AIGC内容生成上线（第2月末）
- ✅ AIGC服务部署完成
- ✅ 文案生成功能上线
- ✅ 图片生成功能上线
- ✅ 用户内容生成测试通过

#### 里程碑2：采购自动化上线（第4月末）
- ✅ 1688集成完成
- ✅ 智能采购流程上线
- ✅ 供应商管理系统完成
- ✅ 采购效率提升验证

#### 里程碑3：数据分析平台上线（第6月末）
- ✅ 数据仓库建设完成
- ✅ 分析仪表板上线
- ✅ 库存预测功能上线
- ✅ v2.0完整版本发布

### 9.3 资源需求

#### 开发团队扩展：
- **AI工程师**：2人（AIGC、机器学习、预测模型）
- **数据工程师**：1人（数据仓库、ETL、数据分析）
- **后端开发**：1人（采购系统、库存算法）
- **前端开发**：1人（AIGC界面、数据分析界面）

#### 基础设施扩展：
- **GPU服务器**：用于AIGC图片/视频生成
- **大数据集群**：用于数据分析和预测
- **对象存储扩展**：存储AIGC生成内容
- **监控系统升级**：监控AI服务成本和性能

#### 第三方服务：
- **OpenAI API**：GPT-4等大模型服务
- **Stability AI**：Stable Diffusion图片生成
- **Runway ML**：视频生成服务
- **阿里云**：1688 API服务

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-02-18 | 初始版本创建，v2.0详细设计 | AI Assistant |

*本文档为iCross v2.0 AIGC与采购自动化阶段详细设计文档，将指导v2.0版本的开发工作。*