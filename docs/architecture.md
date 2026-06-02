# Noesis Architecture

> Local-first multimodal knowledge graph system with traceable GraphRAG.

---

## Overview

Noesis turns code, documents, images, and project history into a persistent, versioned knowledge graph. It is not a vector database or a code graph visualizer; it is an orchestration layer that combines graph storage, vector retrieval, metadata provenance, and reasoning traces.

Core principles:

- **Local-first** — no data upload by default; local LLMs via Ollama
- **Provenance-first** — every entity, relation, and answer points back to source evidence
- **Hybrid extraction** — deterministic parsers for code, LLM/OCR for unstructured data
- **Traceable GraphRAG** — every answer includes graph paths, source chunks, and confidence labels
- **Versioned knowledge** — snapshots and diffs track how the graph evolves over time

---

## High-Level Architecture

```text
┌──────────────────────────────────────────────────────────┐
│ User Interfaces                                          │
│ CLI (Typer) · FastAPI REST · React + Cytoscape.js Web UI │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ GraphRAG Engine                                           │
│ Graph traversal · Vector search · Fusion · Trace builder │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Hybrid Storage                                            │
│ Kuzu/Neo4j graph · LanceDB vectors · SQLite metadata      │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Knowledge Construction Pipeline                           │
│ ingest → parse → extract → align → embed → store          │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Sources                                                   │
│ Local files · GitHub repos · PDFs · Markdown · Images     │
└──────────────────────────────────────────────────────────┘
```

---

## Storage Model

Noesis uses three stores because each one solves a different problem:

| Store | Default | Role |
|---|---|---|
| Graph store | Kuzu | Entities, relations, graph traversal |
| Vector store | LanceDB | Semantic retrieval over chunks |
| Metadata store | SQLite | Sources, chunks, evidence, versions, answer traces |

Optional backends:

- **Neo4j** — optional graph backend for users who want a mature graph database and external tooling
- **Weaviate / Qdrant / Milvus** — future vector backends for stronger hybrid search or large-scale deployment
- **PostgreSQL** — future metadata backend for team/production scenarios

---

## Knowledge Model

```text
Source ──contains──> Document ──split_into──> Chunk
   │                      │                       │
   │                      └──mentions────────────> Entity
   │                                              │
   └──provides_evidence_for──────────────────────> Relation

Entity ──Relation──> Entity
AnswerTrace ──uses──> Evidence ──points_to──> Source span
```

Core objects:

- **Source** — file, URL, repository, or external data origin
- **Document** — parsed source artifact
- **Chunk** — text/code segment used for embedding and retrieval
- **Entity** — concept, function, class, module, service, document topic
- **Relation** — typed edge such as `DEFINES`, `CALLS`, `DEPENDS_ON`, `MENTIONS`, `DOCUMENTS`, `TESTS`
- **Evidence** — source span proving an entity or relation
- **AnswerTrace** — persisted reasoning path for a GraphRAG answer

Confidence labels:

- `EXTRACTED` — deterministic extraction from AST, explicit links, or rules
- `INFERRED` — LLM-generated semantic inference
- `AMBIGUOUS` — low-confidence relation requiring review
- `CONFLICT` — detected contradiction, planned for v0.3

---

## GraphRAG Flow

```text
User query
   │
   ├──► Graph traversal
   │      Kuzu/Neo4j Cypher query over entities and relations
   │
   ├──► Semantic retrieval
   │      LanceDB vector search over source chunks
   │
   ▼
Fusion engine
   │  Combines graph paths, semantic chunks, lexical score,
   │  freshness, and confidence labels
   ▼
Local LLM reasoning
   │
   ▼
Answer + graph paths + source evidence + confidence
```

Every answer must be traceable:

```json
{
  "answer": "...",
  "confidence": "INFERRED",
  "paths": [
    {
      "nodes": ["AuthService", "TokenValidator", "UserRepository"],
      "edges": ["CALLS", "READS"],
      "evidence": [{ "file": "src/auth/service.ts", "span": [10, 42] }]
    }
  ],
  "sources": [
    { "file": "docs/auth.md", "chunk_id": "chunk_7f3a2b", "confidence": "EXTRACTED" }
  ]
}
```

---

## Parsing Pipeline

```text
Code
  → tree-sitter AST
  → functions/classes/imports/calls
  → deterministic graph edges

Documents
  → PyMuPDF / pdfplumber / Markdown parser
  → text chunks + headings + links
  → entities and semantic relations

Images
  → OCR text layer
  → optional vision model summary
  → entities and cross-modal links
```

Initial code language support:

- Python
- TypeScript / JavaScript
- Go
- Rust
- Java
- C / C++

---

## API Surface

```text
POST /api/ingest              Build or update the knowledge graph
POST /api/query               GraphRAG question answering
GET  /api/trace/{answer_id}   Reasoning path and evidence
GET  /api/graph/entity/{id}   Entity details and relationships
GET  /api/graph/search        Hybrid graph/vector search
```

Planned:

```text
POST /api/snapshot            Create graph snapshot
GET  /api/snapshot/diff       Compare two graph versions
POST /mcp/search              MCP search tool
POST /mcp/graph_query         MCP graph query tool
```

---

