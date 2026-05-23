<h1 align="center" style="font-size: 64px;">Eidos</h1>

<p align="center">
  <strong>Local-first, versioned, traceable multimodal knowledge graph OS</strong><br/>
  Code · Documents · Images · Project history → evolving traceable GraphRAG memory
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文文档</a> ·
  <a href="./docs/architecture.md">Architecture</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.0--alpha-blue" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
  <img src="https://img.shields.io/badge/python-%3E%3D3.11-brightgreen" />
  <img src="https://img.shields.io/badge/node-%3E%3D20-brightgreen" />
</p>

---

## What is Eidos?

Eidos is a **local-first, versioned, traceable multimodal knowledge graph operating system**. It continuously turns code, documents, images, and project history into evolving, traceable GraphRAG memory for humans and AI agents.

- 🧠 **Multimodal knowledge extraction** — tree-sitter AST for zero-token code parsing, LLM for document semantics, OCR + vision for images
- 🔍 **Traceable GraphRAG** — every answer carries reasoning path, source evidence, and confidence labels (EXTRACTED / INFERRED / AMBIGUOUS)
- 📊 **Graph version control** — snapshots, diff, rollback, and time-travel queries over your knowledge graph

> Eidos is not a replacement for vector databases or code graph tools. It is an **orchestration layer** that combines graph DB + vector DB + metadata store into a unified knowledge system with provenance, versioning, and reasoning.

---

## ⚡ Quick Start

```bash
pip install eidos

eidos init              # generate eidos.yaml (zero external dependencies)
eidos ingest ./project  # build knowledge graph from local files
eidos serve             # start FastAPI server + Web UI
```

Then open `http://localhost:8000` to explore your knowledge graph.

**Requirements**:

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥ 3.11 | Core engine (FastAPI, parsing, GraphRAG) |
| Node.js | ≥ 20 | Web UI development only |
| 16 GB RAM | — | Local LLM + embedding (no GPU required) |

---

## 🧠 GraphRAG Engine

The core of Eidos is a **traceable GraphRAG fusion engine**:

```
User Query
    │
    ▼  ─────────────────────────────────────────
    │  Layer 1: Graph Traversal  Kuzu/Neo4j  <500ms │
    │  ─────────────────────────────────────────│
    │  Layer 2: Semantic Search  LanceDB     <3s    │
    │  ─────────────────────────────────────────│
    │  Layer 3: Fusion + Reasoning  LLM      variable│
    └──────────────────────────────────────────
                              │
                              ▼
                    Answer + Reasoning Path + Evidence
```

| Layer | Store | Latency | Role |
|-------|-------|---------|------|
| L1 | Kuzu (default) / Neo4j (optional) | < 500ms | Exact graph traversal, entity/relation queries |
| L2 | LanceDB | < 3s | Dense vector semantic search over chunks |
| L3 | Fusion Engine + Ollama | variable | Combine graph paths + semantic chunks → LLM reasoning |

Every answer includes:
- `paths`: graph traversal route (nodes → edges → evidence)
- `sources`: original file references with line/span
- `confidence`: EXTRACTED / INFERRED / AMBIGUOUS

---

## 📡 API

Eidos exposes a **FastAPI** server:

```
POST /api/query              # GraphRAG question answering
GET  /api/graph/entity/:id   # entity details + relations + provenance
GET  /api/trace/:answer_id   # full reasoning path with evidence
POST /api/ingest             # trigger knowledge graph ingestion
GET  /api/snapshot           # list graph versions (v0.2)
```

---

## 📦 Project Structure

```
Eidos/
├── eidos/                  # Python main package
│   ├── core/               # types, config, constants
│   ├── ingest/             # data ingestion (local files, GitHub)
│   ├── parse/              # multimodal parsing (code, docs, images)
│   ├── cognify/            # entity/relation extraction, embedding
│   ├── store/              # hybrid storage (Kuzu + LanceDB + SQLite)
│   ├── graphrag/           # traversal + semantic search + fusion
│   ├── api/                # FastAPI REST endpoints
│   └── cli/                # Typer CLI
├── packages/
│   └── web/                # React + Cytoscape.js knowledge workspace
├── tests/
├── docs/
└── docker-compose.yml
```

---

## 🗺️ Roadmap

| Milestone | Scope | Status |
|-----------|-------|--------|
| v0.1 Nebula | Static knowledge graph MVP: ingest, GraphRAG, traceable answers, Web UI skeleton | 🔧 In progress |
| v0.2 Pulse | Dynamic evolution: file watcher, incremental updates, graph versioning, snapshots | 🔜 Planned |
| v0.3 Synapse | Proactive intelligence: MCP server, anomaly detection, user feedback loop, conflict resolution | 🔜 Planned |

---

## 🛠️ Development

```bash
pytest              # Python unit tests
```

---

## 🤝 Contributing

Contributions are welcome. Before starting:

1. Read [CLAUDE.md](./CLAUDE.md) for full architecture and development guidelines
2. Open an issue to discuss your proposed change before submitting a PR

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

<p align="center">Eidos — from the Greek εἶδος: form, essence, the true nature of things</p>
