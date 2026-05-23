# Eidos v0.1 Nebula — Phase 1 任务清单

> 基础设施层（第 1–2 周）。Phase 2 的解析工作开始前，Phase 1 所有任务必须全部完成。

---

## [core] #1 初始化 Python 项目骨架

**Scope**: `core`
**优先级**: P0
**预估工作量**: 1 天

### 描述
搭建 Eidos Python 包的基础结构和现代工具链，为后续所有模块提供一致的开发基座。

### 任务

- [ ] 创建 `pyproject.toml`：
  - 项目元数据（name, version, description, authors, license）
  - Python `>= 3.11` 版本要求
  - 核心依赖：`fastapi`, `pydantic`, `pydantic-settings`, `typer`, `sqlalchemy`, `kuzu`, `lancedb`, `tree-sitter`, `tree-sitter-python`, `tree-sitter-javascript`, `PyMuPDF`, `markdown-it-py`, `Pillow`, `pytesseract`, `fastembed`, `httpx`（Ollama HTTP 调用）
  - 开发依赖：`pytest`, `pytest-asyncio`, `black`, `ruff`, `mypy`
- [ ] 创建 `eidos/__init__.py`，写入版本常量
- [ ] 在 `pyproject.toml` 中配置 `pytest`（从 `tests/` 目录发现测试）
- [ ] 配置 `black`：行长度 88，目标版本 py311
- [ ] 配置 `ruff` 规则：E, F, I, N, W, UP, B, C4, SIM
- [ ] 添加 `.gitignore`（Python、Node、IDE 模式）
- [ ] 添加 `.cursorignore`（忽略图谱缓存文件）

### 验收标准

- [ ] 在干净的虚拟环境中 `pip install -e .` 成功
- [ ] `pytest` 可以运行，零测试、零导入错误
- [ ] `black eidos/` 格式化无错误
- [ ] `ruff check eidos/` 通过，零违规
- [ ] `python -c "import eidos; print(eidos.__version__)"` 正常输出

### 依赖
无（第一个任务）。

---

## [core] #2 Pydantic Settings 配置系统

**Scope**: `core`
**优先级**: P0
**预估工作量**: 1 天

### 描述
构建类型安全、环境感知的配置系统，从 `eidos.yaml` 和环境变量加载配置。所有存储 URI、模型端点、流水线参数的唯一可信来源。

### 任务

- [ ] 创建 `eidos/core/config.py`，定义 `Settings` 类（Pydantic Settings v2）：
  - `storage.kuzu.path` — 默认 `.eidos/graph.db`
  - `storage.lancedb.path` — 默认 `.eidos/vectors`
  - `storage.sqlite.path` — 默认 `.eidos/metadata.db`
  - `models.embedding.provider` — 默认 `"fastembed"`
  - `models.embedding.model` — 默认 `"BAAI/bge-small-en-v1.5"`
  - `models.llm.provider` — 默认 `"ollama"`
  - `models.llm.model` — 默认 `"qwen2.5:7b"`
  - `models.llm.base_url` — 默认 `"http://localhost:11434"`
  - `ingest.languages` — 默认 6 种语言列表
  - `ingest.exclude_patterns` — 默认忽略列表（`node_modules/**`, `.git/**` 等）
- [ ] 在仓库根目录创建 `eidos.yaml` 模板
- [ ] 支持环境变量覆盖：`EIDOS_STORAGE__KUZU__PATH`, `EIDOS_MODELS__LLM__MODEL`
- [ ] 启动时校验配置（检查存储路径可写、Ollama 可访问）

### 验收标准

- [ ] `eidos init` CLI 命令能从默认值生成合法的 `eidos.yaml`
- [ ] 修改环境变量可以覆盖 yaml 中的值
- [ ] 非法配置（如缺少必填项）抛出清晰的 `ValidationError`
- [ ] Config 对象可从 `eidos.core.config` 导入，且单例安全

### 依赖
- #1（项目骨架）

---

## [store] #3 Kuzu 图数据库初始化

**Scope**: `store`
**优先级**: P0
**预估工作量**: 1–2 天

### 描述
使用 Kuzu（嵌入式 Cypher 兼容图数据库）初始化默认图存储。Kuzu 零外部服务，本地文件运行，与 Eidos 本地优先原则对齐。

### 任务

- [ ] 在 `pyproject.toml` 中添加 `kuzu` 依赖
- [ ] 创建 `eidos/store/kuzu_store.py`，实现 `GraphStore` 接口：
  - `connect(db_path: str) -> KuzuConnection`
  - `upsert_node(entity: Entity) -> None`
  - `upsert_edge(relation: Relation) -> None`
  - `traverse(start_id: str, depth: int) -> list[Path]`
  - `execute_cypher(query: str, params: dict) -> list[dict]`
- [ ] 定义核心节点/边的 Cypher Schema：
  - `CREATE NODE TABLE Entity(id STRING PRIMARY KEY, name STRING, type STRING, modality STRING, source_id STRING, confidence STRING)`
  - `CREATE REL TABLE RELATION(FROM Entity TO Entity, type STRING, confidence STRING, extractor STRING)`
- [ ] 管理 Kuzu 连接生命周期（首次使用时打开，关闭时释放）
- [ ] 添加基础连接健康检查

### 验收标准

- [ ] `KuzuStore.connect(".eidos/graph.db")` 创建合法的 Kuzu 数据库文件
- [ ] 插入一个实体和一条关系后，从该实体遍历返回预期路径
- [ ] Cypher `MATCH (e:Entity) RETURN e.id, e.name` 返回已插入数据
- [ ] 同一实体 ID 多次 upsert 是幂等的（更新而非重复）

### 依赖
- #1（项目骨架）
- #2（配置系统，用于 db path）

---

## [store] #4 LanceDB 向量数据库初始化

**Scope**: `store`
**优先级**: P0
**预估工作量**: 1 天

### 描述
使用 LanceDB（本地文件向量数据库）初始化默认向量存储。零运维开销，存放 chunk 嵌入，供 GraphRAG 流水线语义检索。

### 任务

- [ ] 在 `pyproject.toml` 中添加 `lancedb` 依赖
- [ ] 创建 `eidos/store/lancedb_store.py`，实现 `VectorStore` 接口：
  - `connect(db_path: str) -> LanceDBConnection`
  - `upsert_chunks(chunks: list[Chunk]) -> None`
  - `search(query_embedding: list[float], top_k: int, filters: dict | None) -> list[ChunkResult]`
- [ ] 定义 LanceDB 表结构：
  - `chunk_id` (STRING, primary key)
  - `content` (STRING)
  - `source_file` (STRING)
  - `modality` (STRING)
  - `embedding` (固定维度向量，维度从配置读取)
  - `created_at` (TIMESTAMP)
- [ ] 从 `eidos.yaml` 读取向量维度配置
- [ ] 搜索支持元数据过滤（如 `modality == "code"`）

### 验收标准

- [ ] `LanceDBStore.connect(".eidos/vectors")` 创建合法的 LanceDB 数据集目录
- [ ] 成功 upsert 10 条 384 维 embedding 的 chunk
- [ ] 用随机 384 维向量搜索，返回按相似度排序的 chunk
- [ ] 按 `modality` 过滤搜索，只返回匹配 modality 的 chunk

### 依赖
- #1（项目骨架）
- #2（配置系统）

---

## [store] #5 SQLite 元数据 Schema

**Scope**: `store`
**优先级**: P0
**预估工作量**: 1–2 天

### 描述
设计并初始化 SQLite 元数据数据库，存放溯源记录、源文档、chunk 元数据、图谱版本信息。这是知识图谱的审计追踪层。

### 任务

- [ ] 创建 `eidos/store/metadata_store.py`，实现 `MetadataStore` 接口：
  - `connect(db_path: str) -> Engine`
  - `create_tables() -> None` — 幂等建表
- [ ] 定义 SQLAlchemy 2.0 模型：
  - `Source` — id, path, url, type, created_at
  - `Document` — id, source_id, path, title, language, parsed_at
  - `Chunk` — id, document_id, content, start_line, end_line, modality
  - `Entity` — id, name, type, modality, source_id, document_id, chunk_id, confidence, extractor
  - `Relation` — id, source_entity_id, target_entity_id, type, confidence, extractor
  - `Evidence` — id, relation_id | entity_id, source_file, span_start, span_end, extractor, created_at
  - `GraphVersion` — id, created_at, snapshot_path, metadata_diff, parent_version_id
  - `AnswerTrace` — id, query, answer, confidence, created_at, version_id
- [ ] 创建迁移/初始化脚本 `scripts/init-db.py`
- [ ] 在频繁查询的列上添加外键约束和索引

### 验收标准

- [ ] `MetadataStore.create_tables()` 在新的 SQLite 文件中创建全部 8 张表
- [ ] 插入 Source → Document → Chunk → Entity → Relation → Evidence 链路，外键完整性通过
- [ ] `SELECT * FROM evidence WHERE entity_id = ?` 返回关联的 evidence 行
- [ ] Schema 可复现：删除 db 文件后重新执行 `create_tables()`，得到完全相同的 schema

### 依赖
- #1（项目骨架）
- #2（配置系统）

---

## [core] #6 共享类型定义（Pydantic Models）

**Scope**: `core`
**优先级**: P0
**预估工作量**: 1 天

### 描述
定义所有 Eidos 模块共用的标准数据模型。Pydantic v2 模型在系统边界处强制执行类型安全、序列化一致性和 Schema 校验。

### 任务

- [ ] 创建 `eidos/core/types.py`，定义模型：
  - `Source` — 数据来源
  - `Document` — 解析后的文档元数据
  - `Chunk` — 可嵌入的片段，含 span 信息
  - `Entity` — 知识节点，含溯源字段
  - `Relation` — 带置信度和抽取器的类型化边
  - `Evidence` — 证明实体/关系的源片段
  - `GraphVersion` — 快照元数据
  - `AnswerTrace` — 推理路径记录
  - `ChunkResult` — 向量搜索结果包装器
  - `Path` — 图遍历路径（节点 + 边 + 证据）
- [ ] 创建 `eidos/core/constants.py`：
  - `RelationType` 枚举（DEFINES, IMPORTS, CALLS, REFERENCES, EXTENDS, IMPLEMENTS, CONTAINS, DEPENDS_ON, DOCUMENTS, MENTIONS, ALIGNS_WITH, TESTS）
  - `ConfidenceLabel` 枚举（EXTRACTED, INFERRED, AMBIGUOUS, CONFLICT）
  - `Modality` 枚举（CODE, DOCUMENT, IMAGE）
- [ ] 所有模型配置 `model_config = ConfigDict(strict=True)`（如适用）
- [ ] 为 API 响应添加 JSON 序列化方法

### 验收标准

- [ ] 全部 8+ 个模型可用合法数据实例化并序列化为 JSON
- [ ] 非法数据（错误类型、缺少必填字段）抛出 `ValidationError`
- [ ] `RelationType.CALLS.value == "CALLS"`，所有枚举值正确
- [ ] 模型可从 `eidos.core.types` 导入，无循环导入问题

### 依赖
- #1（项目骨架）

---

## [store] #7 存储抽象接口

**Scope**: `store`
**优先级**: P0
**预估工作量**: 1 天

### 描述
为三种存储后端定义抽象基类。这些接口允许在不改动业务逻辑的情况下替换后端实现（如 Kuzu → Neo4j，LanceDB → Qdrant）。

### 任务

- [ ] 创建 `eidos/store/base.py`，定义三个 ABC：
  - `GraphStore`
    - `upsert_node(entity: Entity) -> None`
    - `upsert_edge(relation: Relation) -> None`
    - `get_entity(entity_id: str) -> Entity | None`
    - `get_neighbors(entity_id: str, relation_type: str | None, direction: str) -> list[Entity]`
    - `traverse(start_id: str, depth: int, relation_types: list[str] | None) -> list[Path]`
    - `shortest_path(from_id: str, to_id: str) -> list[str] | None`
    - `execute_cypher(query: str, params: dict | None) -> list[dict]`
  - `VectorStore`
    - `upsert_chunks(chunks: list[Chunk]) -> None`
    - `search(query_embedding: list[float], top_k: int, filters: dict | None) -> list[ChunkResult]`
    - `delete_chunks(chunk_ids: list[str]) -> None`
  - `MetadataStore`
    - `upsert_source(source: Source) -> None`
    - `upsert_document(doc: Document) -> None`
    - `upsert_chunk(chunk: Chunk) -> None`
    - `get_provenance(entity_id: str) -> list[Evidence]`
    - `create_snapshot(version: GraphVersion) -> None`
    - `get_snapshot(version_id: str) -> GraphVersion | None`
- [ ] 创建 `eidos/store/factory.py`：
  - `get_graph_store(config) -> GraphStore` — 默认返回 KuzuStore
  - `get_vector_store(config) -> VectorStore` — 默认返回 LanceDBStore
  - `get_metadata_store(config) -> MetadataStore` — 默认返回 SQLite store
- [ ] 添加 typing stub，让 mypy 能校验实现完整性

### 验收标准

- [ ] `KuzuStore`、`LanceDBStore`、`MetadataStore` 均通过 `isinstance(store, GraphStore/VectorStore/MetadataStore)` 检查
- [ ] 配置指定默认后端时，`get_graph_store(config)` 返回可用的 `KuzuStore` 实例
- [ ] 新增后端（如 `Neo4jStore`）只需实现 ABC 方法，无需改动业务逻辑
- [ ] mypy 在 `eidos/store/` 模块上报零错误

### 依赖
- #1（项目骨架）
- #3（Kuzu 实现，提供具体 GraphStore）
- #4（LanceDB 实现，提供具体 VectorStore）
- #5（SQLite 实现，提供具体 MetadataStore）
- #6（共享类型，用于 ABC 签名）

---

## Phase 1 完成关卡

Phase 2 开始前，Phase 1 所有任务必须通过以下集成检查：

```python
from eidos.core.config import get_settings
from eidos.store.factory import get_graph_store, get_vector_store, get_metadata_store
from eidos.core.types import Entity, Relation, Chunk, Evidence

config = get_settings()
graph = get_graph_store(config)
vector = get_vector_store(config)
meta = get_metadata_store(config)

# 关卡 1：存储可用
entity = Entity(id="test-func", name="test", type="function", ...)
graph.upsert_node(entity)
assert graph.get_entity("test-func") is not None

# 关卡 2：溯源链可写入
chunk = Chunk(id="c1", document_id="d1", content="def test(): pass", ...)
vector.upsert_chunks([chunk])
meta.upsert_chunk(chunk)

# 关卡 3：类型序列化正确
json_str = entity.model_dump_json()
assert "test-func" in json_str
```

---

## 任务依赖图

```
#1 项目骨架
   │
   ├──► #2 配置系统
   │       │
   │       ├──► #3 Kuzu 存储 ──┐
   │       │                   │
   │       ├──► #4 LanceDB 存储 ├─► #7 存储抽象接口
   │       │                   │
   │       └──► #5 SQLite 存储 ─┘
   │
   └──► #6 共享类型 ──────────────► #7 存储抽象接口
```
