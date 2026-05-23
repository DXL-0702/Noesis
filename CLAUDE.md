# 开发规范性要求

## 核心协作原则
1.  **禁止自主决策**：在项目开发全流程中，**绝不自作主张猜测我的需求、意图或技术选型**。任何需要推进的开发步骤、功能调整、代码修改、技术方案选择，均需先与我沟通确认，获得明确指令后再执行。
2.  **步骤化沟通与确认**：每一步开发操作（包括但不限于代码编写、功能迭代、配置调整、模块设计）均需以**明确的步骤形式**展开，且每一步执行前必须：
    - 清晰说明**即将执行的具体操作内容**；
    - 等待我确认同意后，再开展后续工作；
    - 若我未明确回复，需暂停所有操作，直至收到指令。
3.  **全链路利弊透明化**：针对每一次编辑、修改或新增的内容，必须**同时清晰阐述该操作的好处与潜在坏处**，具体要求如下：
    - 好处：从项目整体进度、代码质量、功能实现、性能优化、可维护性等维度，具体说明该操作能带来的正向价值；
    - 坏处：从技术风险、兼容性、后续迭代难度、资源消耗等维度，客观分析该操作可能存在的隐患与不足；
    - 需确保利弊分析**贴合项目当前实际场景**，不泛泛而谈，不夸大或缩小影响。
4.  **基于整体思路的最优建议**：需基于我预先明确的**项目整体核心思路、目标、技术栈规划、长期迭代方向**，给出**唯一且最优的建议**，具体要求：
    - 建议需紧扣项目整体目标，避免偏离核心方向；
    - 仅提供**最优解**，不提供多个备选方案（除非我明确要求对比）；
    - 建议需结合技术原理与项目实际，说明为何该方案是最优选择，同时呼应前文提到的利弊分析。

## 协作行为规范
1.  沟通语言需**精准、简洁、专业**，避免模糊表述、歧义性描述或主观臆断性表达；
2.  所有输出内容（包括操作说明、利弊分析、建议）需**结构化呈现**（如分点、分模块），便于快速理解；
3.  若我未明确说明项目整体思路，需先引导我梳理核心目标、技术栈、功能清单等关键信息，再开展后续协作；
4.  若我提出的需求存在技术可行性风险或与整体思路冲突，需先明确指出问题，再给出调整建议，而非直接拒绝或擅自修改。

## CI/CD 标准流程规范
> 项目开发遵循 CI/CD 标准流程，每一步执行前须经讨论确认，执行后须验证结果。

### 分支管理
- `main`：稳定主干，仅接受经过验证的合并；禁止直接 push 未经审查的代码
- `feat/<name>`：功能开发分支，每个里程碑（v0.x）对应独立分支
- `fix/<name>`：缺陷修复分支
- 合并策略：**Squash Merge**（保持主干提交历史整洁）

### 提交规范（Conventional Commits）
```
<type>(<scope>): <subject>

type: feat | fix | refactor | chore | docs | test | perf
scope: core | ingest | parse | cognify | store | graphrag | api | web | cli
```

### 代码变更流程
1. **讨论方案** → 确认技术选型与实现细节
2. **编写代码** → 仅实现已确认的功能，不擅自扩展
3. **运行测试** → 单元测试全部通过后方可提交
4. **提交代码** → 由开发者（用户）亲自执行 `git commit` 和 `git push`
5. **更新文档** → 同步更新 CLAUDE.md / README.md / architecture.md

### 文档同步原则
- **CLAUDE.md 优先**：所有技术决策、架构变更先写入 CLAUDE.md
- **README.md 提炼**：从 CLAUDE.md 提取用户关心的核心内容，中英双语同步更新
- **architecture.md 可视化**：将 CLAUDE.md 架构设计转为 Mermaid 图表，随迭代更新
- **docs/progress/ 进度快照**：面向开源贡献者，分为 `DONE.md`（已完成）和 `NEXT.md`（待开发）
  - 触发更新时机：某模块通过端到端验证后、某 v0.x 阶段完成后、开始新阶段开发前
  - 每次触发时 Claude 主动询问是否更新，由开发者确认后执行
  - `DONE.md` 只记录**已验证**的功能点，不记录仅有代码未验证的模块
  - `NEXT.md` 记录当前阶段具体开发思路，不重复 CLAUDE.md 完整路线图
- 五份文档需**同步更新**，不允许出现内容不一致的情况

### 测试策略
- 每个模块有独立测试文件（`tests/` 目录），不在业务代码底部堆砌测试
- 测试文件重构延后至 v0.3
- Python：pytest | TypeScript：vitest
- 压力测试与集成测试在完整服务栈启动后统一执行

---
**总结：你的角色是"高级技术顾问"，而不是"自主执行者"。你的价值在于提供专业、审慎、透明的分析和建议，而最终的决策权始终在我手中。**

---

# Eidos 完整开发方案

## 一、项目定位

Eidos 是一个**本地优先、可版本化、可追溯的多模态知识图谱操作系统**，面向人类与 AI Agent 共同使用。

> **核心定位**：将持续变化的数字世界（代码、文档、图片、项目历史）转化为可追溯的 GraphRAG 记忆。

与竞品的本质区分：
- **Graphify** = 代码库图谱生成器（一次性项目快照）
- **Understand-Anything** = 代码/文档交互式图谱 Dashboard（项目理解工具）
- **Cognee** = Agent memory framework（开发者 SDK）
- **Eidos** = 版本化知识图谱操作系统（长期知识基础设施 + 最终用户产品）

### 核心差异化

1. **Local-first cognitive graph** — 本地优先，零数据上传，Ollama 端侧模型
2. **Multimodal knowledge space** — 代码、PDF、图片、日志、GitHub Issues/PRs 统一知识空间
3. **Deterministic + semantic hybrid extraction** — tree-sitter 零 Token AST + LLM 语义提取，降低 50 倍 Token 消耗
4. **Traceable GraphRAG** — 每条回答强制附带推理路径（Graph paths + source evidence + confidence labels）
5. **Graph version control** — 快照、diff、rollback、time-travel query
6. **End-user productization** — CLI + API + Web 可视化知识工作台（React + Cytoscape.js）
7. **Human + Agent shared memory** — MCP 协议支持，Agent 可直接读写知识图谱

---

## 二、技术栈

### 2.1 语言分工

| 语言 | 职责边界 | 核心理由 |
|------|----------|----------|
| **Python** | 主引擎：数据接入、多模态解析、实体/关系抽取、混合存储、GraphRAG、FastAPI、CLI | ML/NLP 生态无可替代，tree-sitter、fastembed、Ollama 集成零摩擦 |
| **TypeScript** | Web UI：React、Cytoscape.js 可视化、知识图谱交互 | 前端生态成熟，Cytoscape.js 图谱可视化标准库 |

### 2.2 完整技术栈清单

| 层级 | 技术 |
|------|------|
| **前端** | React 19 + TypeScript + Vite |
| **UI 框架** | Tailwind CSS + shadcn/ui |
| **图谱可视化** | Cytoscape.js |
| **前端状态** | Zustand |
| **API Server** | FastAPI (Python) |
| **图数据库** | Kuzu（默认）/ Neo4j Community（可选） |
| **向量数据库** | LanceDB（本地文件，零运维） |
| **元数据索引** | SQLite |
| **代码解析** | tree-sitter（零 Token 代码结构提取） |
| **文档解析** | PyMuPDF / pdfplumber（PDF）、markdown-it（MD） |
| **图片解析** | Tesseract OCR + Pillow + Ollama vision model |
| **Embedding** | fastembed（默认）/ Ollama nomic-embed-text（可选） |
| **LLM（端侧）** | Ollama（qwen2.5 系列，可选 mistral/llama3） |
| **CLI** | Typer（Python） |
| **配置管理** | Pydantic Settings（环境变量 + 配置文件） |
| **数据验证** | Pydantic v2 |
| **ORM（SQLite）** | SQLAlchemy 2.0 |
| **测试** | pytest（Python）、vitest（TypeScript） |

---

## 三、目录结构

```
Eidos/
├── eidos/                          # Python 主包
│   ├── __init__.py
│   ├── core/                       # 共享类型、配置、工具、常量
│   │   ├── config.py               # Pydantic Settings（环境变量 + eidos.yaml）
│   │   ├── types.py                # 共享数据模型（Pydantic）
│   │   ├── constants.py            # 关系类型、置信度标签、模态常量
│   │   └── utils.py                # 通用工具函数
│   ├── ingest/                     # 数据接入层
│   │   ├── local_scanner.py        # 本地文件夹扫描（inotify/FSWatch 预留）
│   │   ├── github_connector.py     # GitHub 仓库克隆与变更监听
│   │   └── file_watcher.py         # 文件变更监听（v0.2 实现）
│   ├── parse/                      # 多模态解析层
│   │   ├── code_parser.py          # tree-sitter AST 解析（6 种语言）
│   │   ├── doc_parser.py           # 文档解析（PDF/MD/TXT/DOCX）
│   │   └── image_parser.py         # 图片解析（OCR + 视觉语义）
│   ├── cognify/                    # 智能认知层
│   │   ├── entity_extractor.py     # 实体抽取（LLM + 规则）
│   │   ├── relation_extractor.py   # 关系抽取（12 类标准关系模型）
│   │   ├── cross_modal_aligner.py  # 跨模态对齐（v0.1 基础版）
│   │   └── embedder.py             # 向量嵌入（fastembed / Ollama）
│   ├── store/                      # 混合存储层
│   │   ├── graph_store.py          # 图数据库抽象接口
│   │   ├── kuzu_store.py           # Kuzu 实现（默认）
│   │   ├── neo4j_store.py          # Neo4j 实现（可选）
│   │   ├── vector_store.py         # 向量数据库抽象接口
│   │   ├── lancedb_store.py        # LanceDB 实现（默认）
│   │   ├── metadata_store.py       # SQLite 元数据索引接口
│   │   └── evidence_store.py       # 证据/溯源模型存储
│   ├── graphrag/                   # 检索与推理层
│   │   ├── graph_traverser.py      # 精确图遍历（BFS/DFS + Cypher）
│   │   ├── semantic_search.py      # 语义向量搜索
│   │   ├── fusion_engine.py        # GraphRAG 融合引擎
│   │   └── tracer.py               # 推理路径追溯（confidence 标签）
│   ├── api/                        # RESTful API（FastAPI）
│   │   ├── routes/
│   │   │   ├── ingest.py           # 数据接入端点
│   │   │   ├── query.py            # 查询/问答端点
│   │   │   ├── graph.py            # 图操作端点
│   │   │   ├── trace.py            # 推理路径追溯端点
│   │   │   ├── snapshot.py         # 图谱快照端点（v0.2）
│   │   │   └── mcp.py              # MCP 协议端点（v0.3）
│   │   └── main.py                 # FastAPI 应用入口
│   └── cli/                        # CLI 工具（Typer）
│       ├── commands.py             # eidos ingest / query / trace / snapshot 等
│       └── main.py                 # CLI 入口
│
├── packages/
│   └── web/                        # React Web UI
│       ├── src/
│       │   ├── components/         # 图谱组件、搜索组件、Trace 面板
│       │   ├── pages/              # GraphView、SearchView、AskView、TraceView、TimelineView
│       │   ├── stores/             # Zustand 状态管理
│       │   └── api/                # FastAPI 客户端封装
│       ├── public/
│       └── package.json
│
├── tests/                          # 测试目录
│   ├── unit/                       # 单元测试
│   ├── integration/                # 集成测试
│   └── fixtures/                   # 测试数据
│
├── docs/
│   ├── architecture.md             # Mermaid 架构图
│   ├── progress/
│   │   ├── DONE.md                 # 已验证功能快照
│   │   └── NEXT.md                 # 待开发思路
│   └── api/                        # API 文档
│
├── scripts/                        # 工具脚本
│   ├── setup-neo4j.sh              # Neo4j 初始化
│   └── benchmark.py                # 性能基准测试
│
├── docker-compose.yml              # Kuzu（默认零依赖）/ Neo4j（可选 Docker）+ Eidos API
├── eidos.yaml                      # 配置文件模板
├── pyproject.toml                  # Python 依赖 + 项目元数据
├── package.json                    # 前端依赖（可选 monorepo 用）
└── .cursorignore                   # 忽略图谱缓存文件
```

---

## 四、核心模块详解

### 4.1 统一知识模型（Provenance-first）

Eidos 所有数据实体围绕**溯源（Provenance）**设计。每个知识单元必须可追溯到原始数据源。

**核心实体类型**：

```
Source          — 数据源（文件、URL、GitHub 仓库）
Document        — 文档（PDF、MD、代码文件）
Chunk           — 文本/代码片段（用于向量化）
Entity          — 知识实体（函数、类、概念、服务名）
Relation        — 实体间关系（12 类标准模型）
Evidence        — 关系/实体的证据来源
GraphVersion    — 图谱版本快照
AnswerTrace     — 问答推理路径
```

**12 类标准关系模型**：

```text
DEFINES         — 定义关系（文件定义函数）
IMPORTS         — 导入关系（模块导入依赖）
CALLS           — 调用关系（函数调用函数）
REFERENCES      — 引用关系（文档引用实体）
EXTENDS         — 继承关系
IMPLEMENTS      — 实现关系
CONTAINS        — 包含关系（类包含方法）
DEPENDS_ON      — 依赖关系
DOCUMENTS       — 文档关系（文档描述实体）
MENTIONS        — 提及关系（文本提及概念）
ALIGNS_WITH     — 跨模态对齐（v0.1 基础）
TESTS           — 测试关系（测试覆盖代码）
```

**置信度标签**：

```text
EXTRACTED       — 确定性提取（AST、正则、显式链接）
INFERRED        — LLM 推理生成
AMBIGUOUS       — 低置信度，需人工确认
CONFLICT        — 与已有知识矛盾（v0.3 检测）
```

### 4.2 多模态解析引擎

#### 代码解析（tree-sitter，零 Token）

```text
source code
  -> tree-sitter parser
  -> functions / classes / methods / imports / calls
  -> deterministic graph edges
  -> content hash cache（增量更新基础）
```

**v0.1 支持语言**：Python、TypeScript/JavaScript、Go、Rust、Java、C/C++

**缓存策略**：
- SHA-256 内容哈希
- 文件未变更 → 跳过重新解析、重新嵌入
- 文件变更 → 仅更新受影响节点和边

#### 文档解析

```text
PDF  -> PyMuPDF / pdfplumber  -> 文本 + 页码 + 章节结构
MD   -> markdown-it           -> 标题层级 + 链接 + 代码块
TXT  -> 文本分块               -> 语义段落
```

#### 图片解析

```text
图片 -> Tesseract OCR           -> 文本层
     -> Ollama vision model     -> 视觉语义描述（可选，v0.1 基础版）
```

### 4.3 混合存储层

```text
                    ┌──────────────────────┐
                    │    Eidos 业务层       │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌─────────┐    ┌──────────┐    ┌───────────┐
        │  Kuzu   │    │ LanceDB  │    │  SQLite   │
        │  (图)    │    │ (向量)   │    │ (元数据)  │
        │ 默认     │    │ 默认     │    │ 默认      │
        └─────────┘    └──────────┘    └───────────┘
            │              │              │
        ┌───┴───┐      ┌───┴───┐      ┌───┴───┐
        │ Neo4j │      │Weaviate│      │PostgreSQL│
        │(可选)  │      │(可选v0.2)│     │(未来v0.3)│
        └───────┘      └───────┘      └─────────┘
```

| 存储 | 职责 | 数据 |
|------|------|------|
| **Kuzu** | 实体、关系、图遍历（默认） | Entity nodes, Relation edges, Graph paths |
| **Neo4j** | 实体、关系、图遍历（可选） | 企业级场景，可视化工具更强 |
| **LanceDB** | 语义向量检索 | Chunk embeddings, dense/sparse vectors |
| **SQLite** | 元数据、溯源、版本 | Sources, Documents, Chunks, Evidence, GraphVersions, AnswerTraces |

**存储接口抽象**（预留未来扩展）：

```python
class GraphStore:      # Kuzu（默认）/ Neo4j（可选）/ FalkorDB（未来）
class VectorStore:     # LanceDB / Qdrant / pgvector
class MetadataStore:   # SQLite / PostgreSQL
```

### 4.4 GraphRAG 融合引擎（核心差异化）

Eidos 的检索不是单一向量搜索，而是**三层融合**：

```text
用户查询
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Layer 1: 精确图遍历  (Kuzu / Neo4j, < 100ms)      │
│  Cypher 查询：entity name match / relation hop       │
│  命中 → 直接返回精确子图                              │
└──────────────────┬──────────────────────────────────┘
                   │ 未命中
                   ▼
┌─────────────────────────────────────────────────────┐
│  Layer 2: 语义向量搜索  (LanceDB, 100-500ms)          │
│  dense embedding query → Top-K 相似 chunk            │
│  召回相关实体和文档片段                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Layer 3: GraphRAG 融合推理                           │
│  graph paths + semantic chunks → LLM 生成回答          │
│  强制返回 reasoning path + evidence + confidence       │
└─────────────────────────────────────────────────────┘
```

**推理路径返回格式**：

```json
{
  "answer": "认证流程由 AuthService 发起...",
  "confidence": "INFERRED",
  "paths": [
    {
      "nodes": ["AuthService", "TokenValidator", "UserRepository"],
      "edges": ["CALLS", "READS"],
      "evidence": [
        { "file": "src/auth/service.ts", "span": [10, 42] }
      ]
    }
  ],
  "sources": [
    { "file": "docs/auth.md", "chunk_id": "...", "confidence": "EXTRACTED" }
  ]
}
```

**评分融合**（v0.1 基础版）：

```python
final_score = (
    0.35 * vector_score +
    0.25 * graph_score +
    0.20 * lexical_score +
    0.10 * freshness_score +
    0.10 * confidence_score
)
```

### 4.5 图谱版本控制（v0.2 核心）

```text
snapshot create   — 创建图谱快照
diff              — 对比两个版本
rollback          — 回滚到历史版本
time-travel query — 在历史版本中查询
```

数据模型：

```text
GraphVersion:
  version_id
  created_at
  snapshot_cypher  — Cypher 导出（Kuzu / Neo4j 兼容）
  metadata_diff    — 变更摘要
  parent_version   — 父版本（链式）
```

### 4.6 Web UI 知识工作台

**核心视图**：

```text
Graph View    — Cytoscape.js 交互式图谱（节点/边点击查看详情）
Search View   — 混合搜索（关键词 + 语义 + 图过滤）
Ask View      — 问答界面（回答 + 推理路径面板 + 证据来源）
Trace View    — 推理路径可视化（answer -> paths -> sources）
Timeline View — 知识演化时间线（版本快照、变更历史）
Diff View     — 版本对比（新增/删除/修改的节点和边）
Source View   — 原始文件预览（跳转至具体行/段落）
```

---

## 五、与竞品的差异化边界

```
                            更面向长期知识系统
                                  ↑
                                  |
                Eidos            |          Cognee
        versioned KG OS          |     agent memory infra
                                  |
                                  |
Graphify ---------------- Understand-Anything ----------------→ 更面向最终用户体验
code graph skill          code/docs graph dashboard
                                  |
                                  |
                                  ↓
                          更面向一次性项目理解
```

Eidos 站在 **长期知识系统 + 最终用户产品 + Agent 接口** 的交汇点。

---

## 六、开发路线图

### v0.1 Nebula（12周）—— 静态知识库 MVP

**目标**：建立可信赖的静态知识图谱，证明"Provenance-first GraphRAG"核心能力。

**核心成功标准**：不是"能不能画出图"，而是"能不能基于持久图谱和证据链回答问题，并解释答案从哪里来"。

#### Phase 1：基础设施（第 1-2 周）

- [ ] Python 项目骨架（pyproject.toml、pytest、black、ruff）
- [ ] Pydantic Settings 配置系统（`eidos.yaml` 模板）
- [ ] Kuzu 初始化（纯本地文件，零依赖）/ Neo4j Docker Compose（可选）
- [ ] LanceDB 初始化
- [ ] SQLite Schema（Sources, Documents, Chunks, Entities, Relations, Evidence）
- [ ] 共享类型定义（Pydantic models）
- [ ] 存储抽象接口（GraphStore / VectorStore / MetadataStore）

#### Phase 2：多模态解析（第 3-4 周）

- [ ] tree-sitter 代码解析（Python + TypeScript/Go，先做 2 种）
- [ ] 代码实体抽取（function/class/import/call）
- [ ] 文档解析（PDF 文本提取 + MD 结构解析）
- [ ] 本地文件夹扫描 + 文件类型识别
- [ ] 内容哈希缓存（增量更新基础）
- [ ] 分块策略（代码：函数级；文档：语义段落级）

#### Phase 3：认知层 + 存储（第 5-7 周）

- [ ] 实体抽取（代码符号 + 文档概念）
- [ ] 关系抽取（12 类标准关系的基础实现）
- [ ] 确定性代码边写入图数据库（Kuzu 默认）
- [ ] 语义分块写入 LanceDB（embedding）
- [ ] 溯源/证据模型（每条边记录 source_file, span, extractor）
- [ ] GitHub 仓库克隆与基础扫描

#### Phase 4：GraphRAG + API（第 8-9 周）

- [ ] FastAPI 应用骨架
- [ ] `POST /api/query` — GraphRAG 问答端点
- [ ] 图遍历层（Cypher 精确查询）
- [ ] 语义搜索层（LanceDB 向量查询）
- [ ] 融合推理层（graph paths + semantic chunks → LLM）
- [ ] 推理路径返回（paths + evidence + confidence）
- [ ] 回答溯源面板（source file + span 跳转）

#### Phase 5：CLI + Web UI 骨架（第 10-11 周）

- [ ] CLI：`eidos ingest`、`eidos query`、`eidos trace`
- [ ] React 项目初始化（Vite + Tailwind + Zustand）
- [ ] Cytoscape.js 图谱渲染（基础节点/边）
- [ ] Ask 界面（问答 + 推理路径展示）
- [ ] Graph 界面（节点点击查看详情 + source 跳转）
- [ ] Search 界面（关键词搜索 + 图过滤）

#### Phase 6：验证 + 文档（第 12 周）

- [ ] 端到端验证：ingest 真实项目 → query → trace → UI 展示
- [ ] 性能基准：Token 消耗对比、查询延迟测试
- [ ] 五份文档同步（CLAUDE.md / README 中英 / architecture.md / DONE.md / NEXT.md）
- [ ] v0.1 里程碑标记

---

### v0.2 Pulse（8周）—— 动态演化

**目标**：让知识图谱从"静态快照"变为"持续演化"的系统。

#### Wave 1：增量更新（第 1-2 周）

- [ ] 文件变更监听（watchdog / inotify）
- [ ] 增量图谱构建（changed-file-only reprocessing）
- [ ] SHA-256 缓存命中判断
- [ ] 受影响的节点/边级联更新

#### Wave 2：图谱版本控制（第 3-4 周）

- [ ] 快照创建 API
- [ ] 图谱 Diff 计算
- [ ] 版本历史查询
- [ ] Time-travel query（`--at` 参数）

#### Wave 3：时序感知（第 5-6 周）

- [ ] 节点/边时间戳（created_at, updated_at, deleted_at）
- [ ] 历史状态回溯查询
- [ ] Timeline View UI
- [ ] 知识演化趋势可视化

#### Wave 4：Webhook + 外部触发（第 7-8 周）

- [ ] GitHub push events Webhook
- [ ] 自动触发增量更新
- [ ] PR/Issue 数据接入（基础）
- [ ] v0.2 验证 + 文档同步

---

### v0.3 Synapse（10周）—— 主动智能

**目标**：让知识系统具备主动发现、反馈优化、Agent 接入的能力。

#### Wave 1：异常检测（第 1-3 周）

- [ ] 文档-代码不一致检测
- [ ] 关系冲突识别
- [ ] 低置信度边标记
- [ ] 知识质量评分

#### Wave 2：用户反馈闭环（第 4-5 周）

- [ ] 用户标注纠正（entity/relation 纠错）
- [ ] 反馈信号采集
- [ ] 知识质量优化（权重调整）
- [ ] 负反馈降级机制

#### Wave 3：MCP 协议支持（第 6-7 周）

- [ ] MCP server 实现
- [ ] 暴露工具：`search`, `graph_query`, `explain_answer`, `add_source`
- [ ] Claude Code / Cursor / Cline 集成
- [ ] Agent memory substrate API

#### Wave 4：模式挖掘 + 主动推送（第 8-10 周）

- [ ] 隐含关联发现
- [ ] 跨域模式挖掘
- [ ] 非打扰式通知机制
- [ ] 智能推荐（相关文档、缺失知识）
- [ ] v0.3 验证 + 文档同步

---

## 七、测试与验证

1. **单元测试**：`pytest` —— 各 Python 模块独立测试
2. **前端测试**：`vitest` —— React 组件 + API 客户端测试
3. **集成测试**：启动 Kuzu（默认）/ Neo4j（可选）+ LanceDB + FastAPI，验证完整链路
4. **GraphRAG 测试**：
   - 准确率：50 条标注查询，精确查询 ≥ 90%，语义查询 ≥ 80%
   - 延迟：精确查询 P50 < 500ms，语义查询 P50 < 3s
   - 可追溯率：100%（每条回答必须有 reasoning path）
5. **Token 消耗基准**：对比全量加载，验证降低 50 倍以上
6. **端到端**：ingest 真实项目 → query → trace → UI 展示完整流程
7. **CLI 验证**：`eidos ingest ./project`、`eidos query "认证流程是什么？"`、`eidos trace answer-123`

---

## 八、使用方式

### 8.1 产品定位原则

Eidos 是**本地优先的知识图谱基础设施**，不是 SaaS 平台。对标理念：

> 用户只需 `eidos init` 初始化配置，`eidos ingest ./project` 导入项目，即可在本地拥有一个持续演化、可追溯的知识图谱，无需上传任何数据到云端。

### 8.2 三个使用入口（按优先级）

| 阶段 | 新增入口 |
|------|----------|
| v0.1 | **CLI** — `eidos ingest` / `eidos query` / `eidos trace` |
| v0.1 | **API** — FastAPI RESTful 端点（供 Agent/脚本调用） |
| v0.1 | **Web UI** — 知识图谱可视化工作台 |

#### 入口 1 — CLI（v0.1 核心）

**目标用户**：开发者、研究员、知识工作者

```bash
eidos init                              # 初始化配置（生成 eidos.yaml）
eidos ingest ./my-project               # 扫描并构建知识图谱
eidos query "这个项目的认证流程是什么？"    # GraphRAG 问答
eidos trace answer-123                # 追溯回答的推理路径
eidos snapshot create v0.1              # 创建图谱快照
eidos diff v0.1 HEAD                    # 对比版本差异
eidos serve                             # 启动 FastAPI 服务
```

**好处**：零学习成本，本地优先，与开发工作流无缝集成。
**坏处**：非技术用户门槛较高，需要 Web UI 补充。

#### 入口 2 — API（v0.1 核心）

**目标用户**：希望将 Eidos 能力嵌入自有应用的开发者、AI Agent

```
POST /api/query
→ Eidos 内部执行 GraphRAG → 返回 answer + reasoning path + evidence

GET  /api/graph/entity/:id
→ 返回实体详情 + 关系 + 溯源

GET  /api/graph/relation/:id
→ 返回关系详情 + 证据

GET  /api/trace/:answer_id
→ 返回完整推理路径
```

**好处**：可被任意应用/Agent 调用，MCP 集成的技术基础。
**坏处**：需要维护 API 稳定性，v0.1 期间接口可能变化。

#### 入口 3 — Web UI（v0.1 骨架，v0.2 完善）

**定位**：知识图谱可视化工作台，不是纯 Dashboard。

核心页面：
- **Graph View**：Cytoscape.js 交互式图谱（pan/zoom/click/search）
- **Ask View**：问答 + 推理路径面板 + 证据来源列表
- **Trace View**：推理路径可视化（answer → paths → sources）
- **Timeline View**：版本快照时间线（v0.2）
- **Diff View**：版本对比（新增/删除/修改节点边）（v0.2）

**好处**：面向最终用户的产品体验，知识探索直观。
**坏处**：前端工程复杂度高，需要克制功能范围。

### 8.3 典型使用流程

```
第一次使用：
  1. pip install eidos（或 git clone + pip install -e .）
  2. eidos init → 生成 eidos.yaml（配置 Kuzu（默认）/ Neo4j（可选）/ LanceDB / Ollama）
  3. eidos ingest ./project → 构建知识图谱
  4. eidos serve → 启动 API 服务
  5. 打开浏览器访问 http://localhost:8000 → Web UI 探索图谱

日常使用：
  - 代码变更后：eidos ingest --update（增量更新）
  - 问题查询：eidos query "..." 或 Web UI Ask 面板
  - 追溯证据：eidos trace 或点击回答的 reasoning path
  - 版本管理：eidos snapshot / diff（v0.2）
```

### 8.4 配置文件（eidos.yaml）

```yaml
# eidos.yaml — Eidos 配置文件

storage:
  neo4j:
    uri: bolt://localhost:7687
    user: neo4j
    password: eidos
  lancedb:
    path: ./.eidos/vectors
  sqlite:
    path: ./.eidos/metadata.db

models:
  embedding:
    provider: ollama
    model: nomic-embed-text
  llm:
    provider: ollama
    model: qwen2.5:7b

ingest:
  languages: [python, typescript, go, rust, java, c]
  max_file_size_mb: 10
  exclude_patterns:
    - "node_modules/**"
    - ".git/**"
    - "*.min.js"

graphrag:
  vector_top_k: 10
  graph_max_hops: 3
  confidence_threshold: 0.6
```

---

## 九、核心目标与指标

| 指标 | 目标 | 验证方式 |
|------|------|---------|
| 图谱构建 Token 消耗 | 相比全量加载降低 50 倍以上 | 对比实验（AST vs 全量 LLM） |
| 精确查询延迟 | < 500ms | P50 基准测试 |
| 语义查询延迟 | < 3s | P50 基准测试 |
| 推理可追溯率 | 100% | 每条回答必须有 reasoning path |
| 本地运行需求 | 16GB RAM，无 GPU 亦可 | 实测验证 |
| 增量更新准确率 | 仅变更文件重新处理 | 哈希缓存验证 |

---

## 十、开源策略

- **License**：MIT（待定，需确认）
- **语言**：README 中英双语，代码注释英文
- **贡献指南**：v0.1 GA 后补充 `CONTRIBUTING.md`
- **Issue 模板**：bug report / feature request / question
- **社区**：GitHub Discussions（v0.2 后开启）

---

> **Eidos turns your evolving digital world into a traceable knowledge graph.**
>
> **Eidos 将持续变化的数字世界转化为可追溯的知识图谱。**
