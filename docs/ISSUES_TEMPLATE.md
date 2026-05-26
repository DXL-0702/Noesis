# Eidos v0.1 Nebula — Phase 2 任务清单

> 多模态解析层（第 3–4 周）。Phase 2 的目标是完成本地文件扫描、内容哈希缓存、代码/文档解析和基础分块，为 Phase 3 的实体/关系抽取与存储写入提供稳定输入。

---

## [ingest] #15 本地文件扫描与文件类型识别

**Scope**: `ingest`
**优先级**: P0
**预估工作量**: 1 天

### 描述
实现本地目录扫描器，负责递归发现项目文件、应用忽略规则、识别文件类型和模态，为后续解析器分发提供统一入口。

### 任务

- [ ] 创建 `eidos/ingest/__init__.py`
- [ ] 创建 `eidos/ingest/local_scanner.py`
- [ ] 定义 `ScannedFile` 模型或复用现有 Pydantic 类型扩展字段：
  - `path`
  - `relative_path`
  - `suffix`
  - `size_bytes`
  - `modality`
  - `language`
- [ ] 支持递归扫描指定目录
- [ ] 应用 `Settings.ingest.exclude_patterns`
- [ ] 跳过超过 `max_file_size_mb` 的文件
- [ ] 根据后缀识别模态：
  - code：`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`
  - document：`.md`, `.txt`, `.log`, `.pdf`
  - image：`.png`, `.jpg`, `.jpeg`, `.webp`
- [ ] 根据后缀识别语言：python、typescript、javascript、go、rust、java、c、cpp、markdown、text、pdf、image

### 验收标准

- [ ] 扫描一个包含代码、Markdown、PDF、图片的测试目录，能返回正确文件列表
- [ ] `node_modules/**`、`.git/**`、`.eidos/**` 被正确忽略
- [ ] 超过大小限制的文件被跳过
- [ ] 每个返回文件都包含相对路径、模态、语言、大小信息

### 依赖
- Phase 1 #2（配置系统）
- Phase 1 #6（共享类型）

---

## [ingest] #16 内容哈希缓存

**Scope**: `ingest`
**优先级**: P0
**预估工作量**: 1 天

### 描述
实现 SHA-256 内容哈希计算，为增量解析和后续 changed-file-only reprocessing 打基础。Phase 2 只实现哈希计算与缓存读写，不做完整增量更新。

### 任务

- [ ] 创建 `eidos/ingest/hash_cache.py`
- [ ] 实现 `compute_file_hash(path: Path) -> str`
- [ ] 实现 `HashCache`：
  - `load()`
  - `save()`
  - `get(path)`
  - `set(path, hash, metadata)`
  - `has_changed(path, current_hash)`
- [ ] 缓存文件默认写入 `.eidos/cache/file_hashes.json`
- [ ] 缓存 metadata 至少包含：
  - `hash`
  - `size_bytes`
  - `mtime`
  - `parser_version`
- [ ] 与 #15 `ScannedFile` 结合，标记 `changed: bool`

### 验收标准

- [ ] 同一文件内容不变时，连续两次 hash 一致
- [ ] 修改文件内容后，hash 变化
- [ ] `HashCache.has_changed()` 能正确识别新增、未变更、已变更文件
- [ ] 缓存 JSON 可重复加载，不丢失 metadata

### 依赖
- #15 本地文件扫描

---

## [parse] #17 tree-sitter 代码解析基础框架

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1 天

### 描述
建立代码解析器的通用框架，负责根据语言选择 tree-sitter parser，并输出统一的代码结构结果。该任务只做框架，不实现具体语言查询逻辑。

### 任务

- [ ] 创建 `eidos/parse/__init__.py`
- [ ] 创建 `eidos/parse/code_parser.py`
- [ ] 定义 `CodeSymbol` 模型：
  - `id`
  - `name`
  - `kind`（function/class/method/import/call）
  - `file_path`
  - `start_line`
  - `end_line`
  - `text`
- [ ] 定义 `CodeParseResult` 模型：
  - `file_path`
  - `language`
  - `symbols`
  - `imports`
  - `calls`
  - `errors`
- [ ] 实现 `CodeParserRegistry`
  - 根据 language 返回对应 parser
  - 不支持语言时返回清晰错误
- [ ] 实现基础 `parse_file(path, language)` 入口
- [ ] 抽象语言解析器基类 `LanguageParser`

### 验收标准

- [ ] 传入不支持语言时，返回明确错误而不是崩溃
- [ ] Registry 能根据 `python`、`typescript`、`go` 返回对应 parser 占位实现
- [ ] `CodeParseResult` 可序列化为 JSON
- [ ] 框架不依赖具体业务存储层

### 依赖
- Phase 1 #6（共享类型）
- #15 本地文件扫描

---

## [parse] #18 Python 代码解析器

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1–2 天

### 描述
基于 tree-sitter 实现 Python 代码解析，抽取函数、类、方法、import 和函数调用。Python 是 Phase 2 首个完整语言实现。

### 任务

- [ ] 在 `code_parser.py` 或 `python_parser.py` 中实现 `PythonParser`
- [ ] 加载 tree-sitter Python grammar
- [ ] 抽取：
  - function definition
  - class definition
  - method definition
  - import statement
  - from-import statement
  - call expression
- [ ] 记录每个 symbol 的起止行号和源码片段
- [ ] 为 symbol 生成稳定 ID：`{relative_path}:{kind}:{name}:{start_line}`
- [ ] 对语法错误文件返回 `errors`，不中断整体解析

### 验收标准

- [ ] 解析包含函数、类、方法、import、调用的 Python fixture
- [ ] 函数/类/方法数量正确
- [ ] import 与 from-import 被识别
- [ ] 调用表达式被识别
- [ ] 起止行号正确
- [ ] 语法错误文件不会导致解析器崩溃

### 依赖
- #17 tree-sitter 代码解析基础框架

---

## [parse] #19 TypeScript / JavaScript 代码解析器

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1–2 天

### 描述
基于 tree-sitter 实现 TypeScript / JavaScript 代码解析，抽取函数、类、方法、import/export 和调用表达式。前端项目分析依赖此能力。

### 任务

- [ ] 实现 `TypeScriptParser`
- [ ] 加载 tree-sitter JavaScript / TypeScript grammar
- [ ] 抽取：
  - function declaration
  - arrow function
  - class declaration
  - method definition
  - import statement
  - export statement
  - call expression
- [ ] 支持 `.ts`, `.tsx`, `.js`, `.jsx`
- [ ] 记录 symbol 起止行和源码片段
- [ ] 生成稳定 ID：`{relative_path}:{kind}:{name}:{start_line}`

### 验收标准

- [ ] 解析包含 React 组件、class、函数、import 的 TS fixture
- [ ] arrow function 被识别
- [ ] import/export 被识别
- [ ] 调用表达式被识别
- [ ] `.ts` 和 `.tsx` 都能解析

### 依赖
- #17 tree-sitter 代码解析基础框架

---

## [parse] #20 Go 代码解析器

**Scope**: `parse`
**优先级**: P1
**预估工作量**: 1 天

### 描述
基于 tree-sitter 实现 Go 代码解析，抽取 package、import、function、method 和 call expression。Go 是 Phase 2 的第三个语言目标。

### 任务

- [ ] 添加 Go tree-sitter grammar 依赖
- [ ] 实现 `GoParser`
- [ ] 抽取：
  - package declaration
  - import declaration
  - function declaration
  - method declaration
  - call expression
- [ ] 记录 symbol 起止行和源码片段
- [ ] 生成稳定 ID

### 验收标准

- [ ] 解析包含 package/import/function/method/call 的 Go fixture
- [ ] package 名称可识别
- [ ] 函数和方法数量正确
- [ ] 调用表达式被识别

### 依赖
- #17 tree-sitter 代码解析基础框架

---

## [parse] #21 代码实体抽取与关系抽取

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1–2 天

### 描述
将代码解析结果转为 Eidos 的标准 Entity / Relation 模型。该任务不写入数据库，只负责构建确定性抽取结果，为 Phase 3 存储写入做准备。

### 任务

- [ ] 创建 `eidos/parse/code_entities.py`
- [ ] 实现 `symbols_to_entities(result: CodeParseResult) -> list[Entity]`
- [ ] 实现 `symbols_to_relations(result: CodeParseResult) -> list[Relation]`
- [ ] 关系映射：
  - 文件 → 函数/类：`DEFINES`
  - 类 → 方法：`CONTAINS`
  - 文件 → import：`IMPORTS`
  - 函数/方法 → 调用：`CALLS`
- [ ] 所有确定性关系 confidence = `EXTRACTED`
- [ ] 所有关系 extractor = `tree-sitter`
- [ ] Entity/Relation ID 必须稳定、可重复

### 验收标准

- [ ] Python fixture 能生成 Entity 列表和 Relation 列表
- [ ] TypeScript fixture 能生成 Entity 列表和 Relation 列表
- [ ] `DEFINES`、`IMPORTS`、`CALLS` 至少三类关系可生成
- [ ] 同一文件重复解析两次，Entity/Relation ID 完全一致

### 依赖
- #18 Python 代码解析器
- #19 TypeScript / JavaScript 代码解析器
- Phase 1 #6（共享类型）

---

## [parse] #22 Markdown / TXT 文档解析

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1 天

### 描述
实现 Markdown 和纯文本解析，输出文档结构、标题层级、链接、代码块和文本段落，为后续文档实体抽取与分块提供输入。

### 任务

- [ ] 创建 `eidos/parse/doc_parser.py`
- [ ] 定义 `DocumentParseResult`：
  - `file_path`
  - `title`
  - `sections`
  - `links`
  - `code_blocks`
  - `paragraphs`
  - `errors`
- [ ] 使用 `markdown-it-py` 解析 Markdown
- [ ] 抽取标题层级（h1–h6）
- [ ] 抽取链接和代码块
- [ ] TXT 按空行分段
- [ ] 对异常编码文件返回 errors，不中断解析

### 验收标准

- [ ] Markdown fixture 的标题、链接、代码块数量正确
- [ ] TXT fixture 能按段落切分
- [ ] 非 UTF-8 文件不导致解析器崩溃
- [ ] `DocumentParseResult` 可 JSON 序列化

### 依赖
- #15 本地文件扫描

---

## [parse] #23 PDF 文档解析

**Scope**: `parse`
**优先级**: P1
**预估工作量**: 1 天

### 描述
实现 PDF 文本提取，保留页码信息和基本段落结构。Phase 2 不做复杂版面理解，只提供可用于分块和溯源的文本层。

### 任务

- [ ] 在 `doc_parser.py` 中实现 PDF parser
- [ ] 使用 PyMuPDF 提取每页文本
- [ ] 保留 page number
- [ ] 按页和空行构建段落
- [ ] 对扫描版 PDF 返回清晰提示（无文本层，后续 OCR 处理）

### 验收标准

- [ ] 文本型 PDF fixture 能提取页码和文本
- [ ] 每个段落能追溯到页码
- [ ] 空白 PDF 或扫描版 PDF 不崩溃，返回 errors

### 依赖
- #22 Markdown / TXT 文档解析

---

## [parse] #24 分块策略：代码函数级 + 文档语义段落级

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1 天

### 描述
实现统一分块策略，将代码解析结果和文档解析结果转为标准 Chunk。代码按函数/类粒度切分，文档按标题/段落语义切分。

### 任务

- [ ] 创建 `eidos/parse/chunker.py`
- [ ] 实现 `chunk_code(parse_result: CodeParseResult) -> list[Chunk]`
- [ ] 实现 `chunk_document(parse_result: DocumentParseResult) -> list[Chunk]`
- [ ] 代码 chunk：
  - 函数/方法级优先
  - 类定义可作为独立 chunk
  - 保留 start_line / end_line
- [ ] 文档 chunk：
  - 标题 + 段落组合
  - 控制最大字符数
  - 保留标题路径和源文件
- [ ] Chunk ID 稳定：`{file_path}:chunk:{start_line}:{hash}`

### 验收标准

- [ ] Python fixture 生成函数级 chunk
- [ ] TypeScript fixture 生成函数/组件级 chunk
- [ ] Markdown fixture 生成段落级 chunk
- [ ] Chunk 包含 content、start_line、end_line、modality
- [ ] 同一输入重复分块，Chunk ID 一致

### 依赖
- #18 Python 代码解析器
- #19 TypeScript / JavaScript 代码解析器
- #22 Markdown / TXT 文档解析
- #23 PDF 文档解析

---

## [parse] #25 Phase 2 集成验证

**Scope**: `parse`
**优先级**: P0
**预估工作量**: 1 天

### 描述
对 Phase 2 所有解析能力做端到端集成验证：扫描目录 → 哈希判断 → 分发解析 → 抽取实体/关系 → 生成 chunk。该任务不写入 Kuzu/LanceDB/SQLite，只验证解析层输出稳定可靠。

### 任务

- [ ] 创建 `tests/fixtures/phase2_project/`
  - `main.py`
  - `app.tsx`
  - `service.go`
  - `README.md`
  - `notes.txt`
  - `sample.pdf`
- [ ] 创建集成测试 `tests/integration/test_phase2_parse_pipeline.py`
- [ ] 实现测试流程：
  - `LocalScanner.scan()`
  - `HashCache.has_changed()`
  - `CodeParserRegistry.parse_file()`
  - `symbols_to_entities()` / `symbols_to_relations()`
  - `chunk_code()` / `chunk_document()`
- [ ] 输出 Phase 2 解析统计：
  - 扫描文件数
  - 解析成功数
  - Entity 数
  - Relation 数
  - Chunk 数
  - Error 数

### 验收标准

- [ ] Phase 2 fixture 项目端到端解析通过
- [ ] 至少生成 10 个 Entity
- [ ] 至少生成 5 条 Relation
- [ ] 至少生成 5 个 Chunk
- [ ] 第二次运行 hash cache 标记未变更文件
- [ ] 所有解析错误被收集在结果中，而不是导致流程崩溃

### 依赖
- #15 本地文件扫描与文件类型识别
- #16 内容哈希缓存
- #17 tree-sitter 代码解析基础框架
- #18 Python 代码解析器
- #19 TypeScript / JavaScript 代码解析器
- #20 Go 代码解析器
- #21 代码实体抽取与关系抽取
- #22 Markdown / TXT 文档解析
- #23 PDF 文档解析
- #24 分块策略

---

## Phase 2 完成关卡

Phase 3 开始前，Phase 2 必须满足以下条件：

- [ ] 本地目录扫描可稳定输出文件清单
- [ ] 内容哈希缓存可识别 changed / unchanged 文件
- [ ] Python / TypeScript / Go 至少三种语言解析可用
- [ ] Markdown / TXT / PDF 文档解析可用
- [ ] 代码实体与确定性关系可生成
- [ ] 代码和文档均可生成 Chunk
- [ ] 解析层不依赖存储层，可独立测试

---

## 任务依赖图

```text
#15 本地文件扫描
   │
   ├──► #16 内容哈希缓存
   │
   ├──► #17 代码解析框架
   │       │
   │       ├──► #18 Python 解析器 ───────┐
   │       ├──► #19 TS/JS 解析器 ────────┼──► #21 代码实体/关系抽取 ───┐
   │       └──► #20 Go 解析器 ───────────┘                              │
   │                                                                    │
   ├──► #22 Markdown/TXT 解析 ───► #23 PDF 解析 ───► #24 分块策略 ───────┤
   │                                                                    │
   └────────────────────────────────────────────────────────────────────► #25 集成验证
```
