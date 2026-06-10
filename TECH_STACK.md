# AgentForge 技术栈定稿（技术宪法）

> 本文档是项目贯穿全程的技术选型基准与开发蓝本。
>
> **定位：求职导向的个人项目** —— 目标不是堆组件数量，而是把少数关键能力做到面试能讲透。
>
> **核心原则：骨架完整 + 3 个护城河做深 + 砍掉时间黑洞。**
>
> 约束：单人、约 6 周。

---

## 一、三条护城河（重中之重）

面试被问深的地方就这三个，每一个都要能画图、能讲设计权衡、能说清边界情况怎么处理。其余组件都是为这三条护城河和"系统看起来完整"服务的。

| 护城河 | 涉及技术 | 要能讲清的核心 |
|---|:--|---|
| **① 多租户隔离** | PostgreSQL RLS + Qdrant payload filter | 双层隔离，"租户 A 绝对读不到 B"的对抗性测试 |
| **② 混合检索 + 重排** | Qdrant(dense+sparse) + bge-m3 + bge-reranker | 为什么纯向量对缩写/代码/专名失效；召回前后对比数字 |
| **③ 分布式锁与限流** | Redis + Lua 脚本 | Lua 原子性、Redlock 争议、为什么不能裸用 SETNX |

---

## 二、核心层（必做，做深）

| 模块 | 技术 | 说明 |
|---|---|---|
| Web 框架 | FastAPI + Uvicorn / Gunicorn | 异步路由、依赖注入、中间件链、SSE 流式 |
| 数据校验 | Pydantic v2 | 所有 API Schema、工具 Schema |
| 认证 | 自实现 JWT（access/refresh）+ bcrypt | 不用 fastapi-users，自己写才好讲，也是多租户前提 |
| Agent 编排 | LangGraph + langchain-core | 只用 core，不要全套 langchain |
| 模型层 | OpenAI 兼容协议 | Ollama 本地 / 云端国产模型可随时切换（演示加分点） |
| 数据库 | PostgreSQL 16 + SQLAlchemy 2.0 + asyncpg + Alembic | **护城河①**：JSONB、RLS 行级权限 |
| 缓存 / 锁 | Redis 7 + Lua | **护城河③**：分布式锁、令牌桶限流 |
| 向量检索 | Qdrant（dense+sparse 混合）+ bge-m3 + bge-reranker-v2-m3 | **护城河②**：bge-m3 一个模型出两种向量，Qdrant 原生 fusion |

---

## 三、Agent 落地设计（LangGraph）

项目的灵魂：把核心层的组件（LangGraph + 检索 + 模型 + 工具）组装成一个能跑的 Agent。**不训练 / 不微调模型**，模型层只是适配层；工作量在编排和链路设计上。

### 3.1 状态定义（State）

用 `TypedDict` 或 Pydantic 定义贯穿全图的状态，字段大致：

```
messages        对话历史
query           当前问题
route           路由决策：rag / direct / tool
retrieved       召回的文档（混合检索结果）
reranked        重排后的 top-k
tool_calls      待执行的工具调用
tool_results    工具执行结果
answer          最终回答
metadata        trace_id、tenant_id 等（贯穿可观测性与多租户）
```

### 3.2 节点设计

| 节点 | 职责 | 关联 |
|---|---|---|
| `router` | 判断走向：要不要检索 / 要不要调工具 / 直接答 | 呼应"什么时候才用 RAG" |
| `retrieve` | dense+sparse 混合检索，带租户 filter | 护城河①② |
| `rerank` | bge-reranker 重排，取 top-5 | 护城河② |
| `generate` | 拼 RAG prompt 模板 → LLM 流式生成（带来源引用） | 见 3.7 |
| `tool_executor` | 执行工具调用 | 自实现工具注册系统 |
| `grade`（可选） | 检索相关性打分 / 答案自检，分数低则回退或重检索 | 防幻觉、显工程素养 |

### 3.3 图结构（条件边）

```
START
 └─ router ──条件边──┐
                     ├─ "rag"    → retrieve → rerank → generate → END
                     ├─ "direct" → generate → END
                     └─ "tool"   → tool_executor → generate → END
```

**router 怎么判断**：先让 LLM 对问题意图分类，或先检索一把看相关性分数是否过阈值（低于阈值就不喂给模型，直接走 direct）。"会判断什么时候不检索"本身就是面试加分点。

### 3.4 LangGraph 高级特性落地（相对旧项目的升级点）

- **Checkpointer（PostgreSQL backend）**：状态持久化，支持多轮对话、断点续传
- **Interrupt（HITL）**：敏感 / 高风险操作前暂停，等人工确认再继续
- **Streaming**：节点级流式，`generate` 节点逐字流给前端（配合 FastAPI SSE）
- **Subgraph**：把 RAG 那条链（retrieve → rerank → generate）抽成可复用子图

### 3.5 自实现工具注册系统

- 统一接口注册工具，每个工具带 Pydantic input schema
- Agent 运行时动态发现可用工具列表
- 比直接用 langchain 内置工具更能体现能力，是简历里"自实现工具注册系统"的落点

### 3.6 RAG 在 Agent 中的位置

RAG 不是独立模块，而是 `router` 判定为 `"rag"` 时走的那条子链：**retrieve → rerank → generate**。是否走它由 router 的条件边决定。

### 3.7 RAG 生成节点的 prompt 模板

```
[System]
你是一个知识库问答助手。只能依据下面提供的「参考资料」回答问题。
- 如果参考资料里没有答案，明确说"根据现有资料无法回答"，不要编造。
- 回答时在末尾标注引用的资料编号。

[参考资料]
【资料1｜来源：产品手册 p.12】
{chunk_1 内容}

【资料2｜来源：FAQ 文档】
{chunk_2 内容}

[用户问题]
{user_question}
```

**关键要点：**

- **每个 chunk 带来源标注** → 可引用、可溯源（企业级 RAG 标配）
- **明确"只据资料回答 + 没有就说不知道"** → 防幻觉核心
- **只塞 rerank 后的 top-3~5** → 省 token，避免"lost in the middle"
- **chunk 间用清晰分隔符** → 模型能区分独立资料

---

## 四、支撑层（够用即可，别强求深度）

| 模块 | 技术 | 说明 |
|---|---|---|
| 异步队列 | Celery + Redis broker | 文档解析、批量 embedding；简历高频词 |
| 文档处理 | PyMuPDF + python-docx | 覆盖 PDF / Word 主流格式，切分策略自己写（加分） |
| 对象存储 | MinIO | 原始文件进 MinIO，元数据进 PG（分层是好故事） |
| 部署 | Docker + Docker Compose | 一个 compose 拉起全套服务 |
| 测试 | pytest + pytest-asyncio + httpx + pytest-cov | 单元 70% / 集成 20% / E2E 10% |
| 配置 / 依赖 | pydantic-settings + uv | 用 uv，不用 poetry |
| CI | GitHub Actions | push 自动 lint + 测试 + 构建 |

---

## 五、可观测性（瘦身版）

- **OTel trace 埋点 + context 传播** —— 重点：把 trace 跨 Celery 任务传下去，是护城河③的天然延伸，很能讲
- **Prometheus** 抓 metrics
- **Loguru** 结构化 JSON 日志

> 建议：trace 既然埋了，补一个 **Jaeger 单容器**看链路（很轻），否则埋了点却看不见就白做了。Grafana 大盘那套属于"全家桶"，本项目不上。

---

## 六、加分层（最后做，做不完不影响主线）

- **MCP**：FastMCP（把知识库问答 / 数据查询暴露为 MCP Tool）
- **K8s**：k3s 本地跑一遍（Deployment / Service / ConfigMap / Secret / Ingress）
- **压测**：Locust（产出 P99 / QPS / 错误率报告，简历亮点）

> **纪律：加分层绝不前置。** 3 条护城河没打透之前不碰。面试官数你会几个组件的权重，远低于你能不能把 RLS 隔离讲到底。

---

## 七、相比原始清单砍掉了什么（及替代）

| 砍掉的 | 它是什么 | 为什么砍 | 替代方案 |
|---|---|---|---|
| `unstructured` | 万能文档解析库 | 依赖重、安装坑多、镜像膨胀；项目只需 PDF/Word，用不上；黑盒不好讲 | PyMuPDF + python-docx（轻、可控、切分自己写） |
| `rank-bm25` | 纯 Python 的 BM25 关键词检索库 | 要自维护关键词索引 + 中文分词 + 结果合并，多一摊活 | Qdrant 原生 sparse vector（bge-m3 一次出 dense+sparse，Qdrant 原生 fusion） |
| `Nginx` | 反向代理 | 单人项目意义不大 | 需前后端同域名时再加 |
| `Grafana 大盘` | metrics 可视化 | 配通了但讲不深，时间黑洞 | 瘦身版可观测性即可 |

> 关键：砍的是**冗余的实现路径**，不是能力。文档解析、关键词检索两个能力都还在，只是换了更轻的活法。

---

## 八、依赖清单

版本交给 uv 解析最新兼容版，不锁死老版本。

```
# Web / async
fastapi uvicorn[standard] gunicorn httpx aiofiles

# 校验 / 配置
pydantic pydantic-settings

# DB
sqlalchemy[asyncio] asyncpg alembic

# Redis / 队列
redis[hiredis] celery[redis]

# Agent
langgraph langchain-core langchain-openai

# 模型 / 检索
openai FlagEmbedding   # bge-m3 原生出 dense+sparse，reranker 也在这里
qdrant-client

# 文档处理
pymupdf python-docx

# 认证
python-jose[cryptography] passlib[bcrypt]

# MCP / 存储
fastmcp minio

# 可观测（瘦身）
opentelemetry-api opentelemetry-sdk
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-sqlalchemy
opentelemetry-instrumentation-redis
opentelemetry-exporter-otlp
prometheus-client loguru

# 测试 / 压测
pytest pytest-asyncio pytest-cov locust

# 前端
streamlit
```

---

## 九、Docker Compose 预期服务清单

```
api         FastAPI 主服务
worker      Celery worker
beat        Celery 定时调度
postgres
redis
qdrant
minio
jaeger      单容器，看 trace
prometheus
streamlit   前端（撑场面）
```

---

## 十、面试叙事备忘

- **系统架构讲述**：准备一段 5 分钟的讲述 —— 数据怎么流、为什么这么分层、瓶颈在哪、怎么权衡。这个叙事能力比多会一个组件值钱。
- **连环追问问答稿**：每条护城河准备一份，预判面试官怎么往深里问。
- **Agent 落地**：要能徒手画出第三节那张图结构，并讲清 router 怎么决策、RAG 子链怎么走。
- 简历技术栈可以列全，但心里分清：哪些"能被问深"（核心层 + 3 护城河 + Agent 编排），哪些"用过但点到为止"（加分层）。

---

## 附：建议的 Day 1 起步路径

> 骨架（FastAPI + Postgres + 多租户表 + RLS）→ 跑通最小 Agent 链路（router → generate，先不接检索）→ 再把 RAG 子链接上。
>
> 先让护城河①的地基和 Agent 主干立起来，后面所有东西都挂在这上面。
