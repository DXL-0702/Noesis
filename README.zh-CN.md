<h1 align="center" style="font-size: 64px;">Eidos</h1>

<p align="center">
  <strong>本地优先、可版本化、可追溯的多模态知识图谱操作系统</strong><br/>
  代码 · 文档 · 图片 · 项目历史 → 可演化可追溯的 GraphRAG 记忆
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./CLAUDE.md">架构文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/版本-v0.1.0--alpha-blue" />
  <img src="https://img.shields.io/badge/许可证-MIT-green" />
  <img src="https://img.shields.io/badge/python-%3E%3D3.11-brightgreen" />
  <img src="https://img.shields.io/badge/node-%3E%3D20-brightgreen" />
</p>

---

## Eidos 是什么？

Eidos 是一个**本地优先、可版本化、可追溯的多模态知识图谱操作系统**。它将代码、文档、图片和项目历史持续转化为可演化、可追溯的 GraphRAG 记忆，供人类与 AI Agent 共同使用。

- 🧠 **多模态知识提取** — tree-sitter AST 零 Token 代码解析，LLM 文档语义提取，OCR + 视觉模型图片解析
- 🔍 **可追溯 GraphRAG** — 每条回答附带推理路径、证据来源和置信度标签（EXTRACTED / INFERRED / AMBIGUOUS）
- 📊 **图谱版本控制** — 快照、Diff、回滚、历史版本时序查询

> Eidos 不是向量数据库或代码图谱工具的替代品。它是将**图数据库 + 向量数据库 + 元数据存储**融合为统一知识系统的**编排层**，具备溯源、版本控制和推理能力。

---

## ⚡ 快速开始

```bash
pip install eidos

eidos init              # 生成 eidos.yaml（零外部依赖）
eidos ingest ./project  # 从本地文件构建知识图谱
eidos serve             # 启动 FastAPI 服务 + Web UI
```

然后打开 `http://localhost:8000` 探索你的知识图谱。

**前置要求**：

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.11 | 核心引擎（FastAPI、解析、GraphRAG） |
| Node.js | ≥ 20 | Web UI 开发 |
| 16 GB 内存 | — | 本地 LLM + 嵌入（无需 GPU） |

---

## 🧠 GraphRAG 引擎

Eidos 的核心是**可追溯的 GraphRAG 融合引擎**：

```
用户查询
    │
    ▼  ─────────────────────────────────────────
    │  Layer 1: 图遍历        Kuzu/Neo4j  <500ms │
    │  ─────────────────────────────────────────│
    │  Layer 2: 语义搜索      LanceDB    <3s    │
    │  ─────────────────────────────────────────│
    │  Layer 3: 融合推理      LLM        视查询而定 │
    └──────────────────────────────────────────
                              │
                              ▼
                    回答 + 推理路径 + 证据来源
```

| 层级 | 存储 | 延迟 | 职责 |
|------|------|------|------|
| L1 | Kuzu（默认）/ Neo4j（可选） | < 500ms | 精确图遍历，实体/关系查询 |
| L2 | LanceDB | < 3s | 稠密向量语义搜索 |
| L3 | 融合引擎 + Ollama | 视查询而定 | 图路径 + 语义片段 → LLM 推理 |

每条回答包含：
- `paths`：图遍历路径（节点 → 边 → 证据）
- `sources`：原始文件引用，含行号/段落
- `confidence`：EXTRACTED / INFERRED / AMBIGUOUS

---

## 📡 API

Eidos 暴露 **FastAPI** 服务：

```
POST /api/query              # GraphRAG 问答
GET  /api/graph/entity/:id   # 实体详情 + 关系 + 溯源
GET  /api/trace/:answer_id   # 完整推理路径与证据
POST /api/ingest             # 触发知识图谱构建
GET  /api/snapshot           # 图谱版本列表（v0.2）
```

---

## 📦 项目结构

```
Eidos/
├── eidos/                  # Python 主包
│   ├── core/               # 类型、配置、常量
│   ├── ingest/             # 数据接入（本地文件、GitHub）
│   ├── parse/              # 多模态解析（代码、文档、图片）
│   ├── cognify/            # 实体/关系抽取、向量嵌入
│   ├── store/              # 混合存储（Kuzu + LanceDB + SQLite）
│   ├── graphrag/           # 遍历 + 语义搜索 + 融合
│   ├── api/                # FastAPI REST 端点
│   └── cli/                # Typer CLI
├── packages/
│   └── web/                # React + Cytoscape.js 知识工作台
├── tests/
├── docs/
└── docker-compose.yml
```

---

## 🗺️ 开发路线图

| 里程碑 | 范围 | 状态 |
|--------|------|------|
| v0.1 Nebula | 静态知识图谱 MVP：接入、GraphRAG、可追溯回答、Web UI 骨架 | 🔧 进行中 |
| v0.2 Pulse | 动态演化：文件监听、增量更新、图谱版本控制、快照 | 🔜 计划中 |
| v0.3 Synapse | 主动智能：MCP 服务、异常检测、用户反馈闭环、冲突解决 | 🔜 计划中 |

---

## 🛠️ 开发

```bash
pytest              # Python 单元测试
```

---

## 🤝 参与贡献

欢迎贡献。开始前请：

1. 阅读 [CLAUDE.md](./CLAUDE.md) 了解完整架构与开发规范
2. 提 Issue 讨论你的改动方案，再提交 PR

---

## 📄 许可证

MIT — 详见 [LICENSE](./LICENSE)

---

<p align="center">Eidos — 源自希腊语 εἶδος：形式、本质、事物的真实面目</p>
