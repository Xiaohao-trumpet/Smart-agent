# Memory System 代码详解

## 📚 目录

1. [系统概述](#系统概述)
2. [阅读顺序](#阅读顺序)
3. [核心组件详解](#核心组件详解)
4. [完整工作流程](#完整工作流程)
5. [关键设计模式](#关键设计模式)
6. [使用示例](#使用示例)

---

## 系统概述

Memory System 是一个完整的记忆管理系统，包含**短期记忆**和**长期记忆**两部分：

- **短期记忆**：会话级别的对话上下文，使用滑动窗口和摘要压缩
- **长期记忆**：持久化的用户偏好和信息，支持语义搜索

### 技术栈

- **数据库**：SQLite（轻量级本地数据库）
- **向量搜索**：Chroma（优先）或本地文件（降级）
- **文本向量化**：OpenAI Embeddings API（优先）或本地哈希（降级）

### 文件结构

```
backend/memory/
├── embeddings.py       # 文本向量化
├── vector_index.py     # 向量存储和搜索
├── repository.py       # SQLite 数据持久化
├── short_term.py       # 短期记忆管理
├── service.py          # 高层服务（整合所有组件）
└── __init__.py         # 模块导出
```

---

## 阅读顺序

建议按照从底层到高层的顺序阅读：

1. **embeddings.py** - 理解文本如何转换为向量
2. **vector_index.py** - 理解向量如何存储和搜索
3. **repository.py** - 理解数据如何持久化
4. **short_term.py** - 理解短期记忆如何管理
5. **service.py** - 理解如何整合所有组件
6. **__init__.py** - 理解对外接口

---

## 核心组件详解

### 1. embeddings.py - 文本向量化

**作用**：将文本转换为数字向量，用于语义搜索。

**核心类**：`EmbeddingProvider`

**关键方法**：


```python
def embed_text(self, text: str) -> List[float]:
    """将文本转换为向量"""
    # 1. 优先使用远程 API（OpenAI）
    # 2. 失败时使用本地哈希方法
    # 3. 返回归一化的向量
```

**工作原理**：

1. **远程方案**：调用 OpenAI Embeddings API
   - 优点：语义理解准确
   - 缺点：需要网络，有成本

2. **本地方案**：基于哈希的确定性向量化
   - 将文本分词
   - 每个词通过 SHA256 哈希映射到向量的某个位置
   - 相同的词总是映射到相同位置
   - 优点：无需网络，免费，确定性
   - 缺点：语义理解较弱

**示例**：
```python
provider = EmbeddingProvider(
    base_url="https://api.openai.com/v1",
    api_key="sk-xxx",
    embedding_model="text-embedding-3-small",
    dimension=256,
    use_remote=True
)

vector = provider.embed_text("I prefer concise answers")
# 返回: [0.1, -0.3, 0.5, ..., 0.2]  # 256维向量
```

**关键代码位置**：
- 第 48-70 行：`embed_text()` - 主要方法
- 第 35-46 行：`_fallback_embedding()` - 本地备用方案
- 第 28-33 行：`_normalize()` - 向量归一化

---

### 2. vector_index.py - 向量存储和搜索

**作用**：存储向量并支持快速语义搜索。

**核心类**：
- `BaseVectorIndex` - 基类接口
- `LocalFileVectorIndex` - 本地文件实现
- `ChromaVectorIndex` - Chroma 数据库实现

**关键方法**：
```python
def upsert(memory_id, user_id, vector, metadata):
    """插入或更新向量"""

def search(user_id, query_vector, top_k):
    """搜索最相似的 top_k 个向量"""
    # 返回: [VectorSearchResult(memory_id, score), ...]

def delete(memory_id):
    """删除向量"""
```

**余弦相似度计算**（第 20-30 行）：
```python
def _cosine_similarity(a, b):
    """计算两个向量的相似度（0-1）"""
    # 公式: cos(θ) = (a·b) / (|a| * |b|)
    # 1.0 = 完全相同
    # 0.0 = 无关
    # -1.0 = 完全相反
```

**两种实现对比**：

| 特性 | LocalFileVectorIndex | ChromaVectorIndex |
|------|---------------------|-------------------|
| 存储 | JSON 文件 | Chroma 数据库 |
| 性能 | 较慢（遍历所有向量） | 快速（优化的索引） |
| 依赖 | 无 | 需要 chromadb |
| 适用 | 开发/小规模 | 生产/大规模 |

**搜索流程**：
```
查询向量: [0.2, 0.4, -0.1, ...]
    ↓
遍历所有向量，计算余弦相似度
    ↓
排序，返回 top-k
    ↓
结果: [
    VectorSearchResult(memory_id="abc", score=0.92),
    VectorSearchResult(memory_id="def", score=0.85),
    VectorSearchResult(memory_id="ghi", score=0.73)
]
```

**关键代码位置**：
- 第 86-95 行：`LocalFileVectorIndex.search()` - 本地搜索
- 第 120-135 行：`ChromaVectorIndex.search()` - Chroma 搜索
- 第 138-144 行：`build_vector_index()` - 工厂函数

---

### 3. repository.py - 数据持久化

**作用**：将记忆数据持久化到 SQLite 数据库。

**核心类**：
- `MemoryRow` - 数据模型
- `MemoryRepository` - 数据访问层

**数据模型**（第 14-24 行）：
```python
@dataclass
class MemoryRow:
    id: str              # 唯一标识符
    user_id: str         # 用户ID
    text: str            # 记忆文本
    tags: List[str]      # 标签列表
    created_at: float    # 创建时间戳
    updated_at: float    # 更新时间戳
    metadata: Dict       # 元数据
```

**数据库表结构**（第 41-58 行）：
```sql
CREATE TABLE memory_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    tags_json TEXT NOT NULL,      -- JSON 格式
    metadata_json TEXT NOT NULL,  -- JSON 格式
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE INDEX idx_memory_user ON memory_items(user_id);
```

**CRUD 操作**：

1. **Create** - 添加记忆（第 71-92 行）
```python
def add(memory_id, user_id, text, tags, metadata):
    # 1. 生成时间戳
    # 2. 插入数据库
    # 3. 返回 MemoryRow 对象
```

2. **Read** - 查询记忆
```python
def get(memory_id):              # 获取单条
def list_by_user(user_id):       # 获取用户所有记忆
def get_many(memory_ids):        # 批量获取
```

3. **Update** - 更新记忆（第 132-161 行）
```python
def update(memory_id, text=None, tags=None, metadata=None):
    # 1. 获取现有记录
    # 2. 部分更新（只更新提供的字段）
    # 3. 更新 updated_at 时间戳
```

4. **Delete** - 删除记忆（第 163-173 行）
```python
def delete(memory_id):
    # 返回 True/False 表示是否成功
```

**关键设计**：
- **线程安全**：使用 `Lock()` 保证并发安全
- **JSON 存储**：tags 和 metadata 存储为 JSON 字符串
- **索引优化**：user_id 索引加速查询
- **部分更新**：update 方法支持只更新部分字段

**关键代码位置**：
- 第 41-58 行：`_init_db()` - 初始化数据库
- 第 71-92 行：`add()` - 添加记忆
- 第 94-105 行：`list_by_user()` - 按用户查询
- 第 132-161 行：`update()` - 更新记忆

---

### 4. short_term.py - 短期记忆管理

**作用**：管理会话级别的对话上下文，使用滑动窗口和摘要压缩。

**核心类**：`ShortTermMemoryManager`

**配置参数**（第 11-21 行）：
```python
window_turns=6              # 保留最近 6 轮对话
enable_summary=True         # 启用摘要
summary_trigger_turns=10    # 超过 10 轮触发摘要
summary_max_chars=800       # 摘要最大字符数
```

**核心概念**：

1. **滑动窗口**：只保留最近 N 轮对话
   - 1 轮 = 1 个用户消息 + 1 个助手回复 = 2 条消息
   - window_turns=6 → 保留 12 条消息

2. **摘要压缩**：当对话超过阈值时，将旧对话压缩成摘要
   - 前 N 轮 → 压缩成摘要
   - 最近 M 轮 → 保留原文

**工作流程**（第 46-68 行）：
```python
def append_turn(session, user_message, assistant_message):
    # 1. 添加消息到会话
    session.add_message("user", user_message)
    session.add_message("assistant", assistant_message)
    
    # 2. 检查是否需要压缩
    if len(messages) > trigger_messages:
        # 3. 将旧消息压缩成摘要
        messages_for_summary = messages[:-keep_messages]
        session.metadata["summary"] = self._summarize(...)
        
        # 4. 只保留最近的消息
        session.conversation_history = messages[-keep_messages:]
```

**示例**：
```
配置: window_turns=6, trigger=10

第 1-10 轮：保留所有对话
第 11 轮：
  - 前 5 轮（10 条消息）→ 压缩成摘要
  - 最近 6 轮（12 条消息）→ 保留原文

结果：
  摘要: "用户讨论了工作和爱好..."
  最近对话: [msg11, msg12, ..., msg22]
```

**上下文构建**（第 70-92 行）：
```python
def build_context(session):
    """构建短期上下文"""
    return {
        "summary": "用户讨论了工作和爱好...",
        "recent_messages": [
            {"role": "user", "content": "今天天气怎么样？"},
            {"role": "assistant", "content": "今天天气晴朗。"}
        ]
    }

def render_context(context):
    """渲染为文本，注入到提示词"""
    return """
Session summary:
用户讨论了工作和爱好...

Recent conversation:
user: 今天天气怎么样？
assistant: 今天天气晴朗。
"""
```

**关键代码位置**：
- 第 46-68 行：`append_turn()` - 添加对话并压缩
- 第 31-44 行：`_summarize()` - 生成摘要
- 第 70-77 行：`build_context()` - 构建上下文
- 第 79-92 行：`render_context()` - 渲染为文本

---

### 5. service.py - 高层服务

**作用**：整合所有底层组件，提供完整的记忆管理功能。

**核心类**：`MemoryService`

**依赖组件**（第 37-48 行）：
```python
class MemoryService:
    def __init__(self, repository, embedding_provider, vector_index):
        self.repository = repository          # SQLite 数据库
        self.embedding_provider = embedding_provider  # 文本向量化
        self.vector_index = vector_index      # 向量搜索
```

**主要功能**：

#### 1. 添加记忆（第 62-84 行）
```python
def add_memory(user_id, text, tags, metadata):
    # 1. 生成 UUID
    memory_id = uuid.uuid4().hex
    
    # 2. 保存到数据库
    row = self.repository.add(...)
    
    # 3. 生成向量
    vector = self.embedding_provider.embed_text(text)
    
    # 4. 保存向量到索引
    self.vector_index.upsert(memory_id, user_id, vector, ...)
    
    # 5. 返回 MemoryItem
    return self._to_item(row)
```

#### 2. 语义搜索（第 124-141 行）
```python
def search_memories(user_id, query, top_k=3):
    # 1. 查询文本 → 向量
    query_vector = self.embedding_provider.embed_text(query)
    
    # 2. 向量搜索 → 返回 ID 和分数
    hits = self.vector_index.search(user_id, query_vector, top_k)
    
    # 3. 根据 ID 批量获取完整记忆
    rows = self.repository.get_many([hit.memory_id for hit in hits])
    
    # 4. 组合结果
    return [
        MemorySearchResult(memory=..., score=hit.score)
        for hit in hits
    ]
```

#### 3. 自动提取记忆（第 153-181 行）
```python
def extract_and_store(user_id, user_message):
    """从用户消息中自动提取偏好"""
    
    # 1. 定义偏好模式
    patterns = [
        r"\bi prefer\b",
        r"\bi like\b",
        r"\bmy name is\b",
        ...
    ]
    
    # 2. 检查是否匹配
    if any(re.search(pattern, text.lower()) for pattern in patterns):
        # 3. 自动保存为记忆
        return self.add_memory(
            user_id=user_id,
            text=text,
            tags=["auto_extracted", "user_preference"],
            metadata={"source": "rule_extractor"}
        )
```

**示例**：
```python
# 用户说："I prefer concise answers."
# 系统自动检测到 "i prefer" 模式
# 自动保存为记忆，标记为 auto_extracted
```

#### 4. 生成记忆上下文（第 143-151 行）
```python
def memory_context_text(user_id, query, top_k):
    """生成可注入到提示词的文本"""
    results = self.search_memories(user_id, query, top_k)
    
    return """
Relevant long-term memories:
- (0.920) I prefer concise answers
- (0.850) Please use Chinese
- (0.730) I'm a programmer
"""
```

**数据一致性保证**：
- 添加：同时写入数据库和向量索引
- 更新：同时更新数据库和重新索引
- 删除：同时从数据库和索引删除

**关键代码位置**：
- 第 62-84 行：`add_memory()` - 添加记忆
- 第 124-141 行：`search_memories()` - 语义搜索
- 第 153-181 行：`extract_and_store()` - 自动提取
- 第 184-211 行：`build_memory_service()` - 工厂函数

---

## 完整工作流程

### 场景 1：用户首次对话

```
用户: "My name is Alice, I prefer concise answers."

1. 短期记忆 (ShortTermMemoryManager)
   └─ append_turn() 保存到会话历史

2. 长期记忆 (MemoryService)
   └─ extract_and_store() 检测到 "I prefer"
      ├─ add_memory() 保存记忆
      │  ├─ Repository.add() → SQLite
      │  ├─ EmbeddingProvider.embed_text() → 向量
      │  └─ VectorIndex.upsert() → 索引
      └─ 返回 MemoryItem

3. 模型回复
   "Nice to meet you, Alice! I'll keep my answers concise."
```

### 场景 2：用户第二次对话（新会话）

```
用户: "How should you answer my questions?"

1. 短期记忆
   └─ 新会话，没有历史

2. 长期记忆
   └─ search_memories("How should you answer my questions?")
      ├─ EmbeddingProvider.embed_text() → 查询向量
      ├─ VectorIndex.search() → 找到相似记忆
      │  └─ 返回: [("abc", 0.92), ("def", 0.85)]
      ├─ Repository.get_many(["abc", "def"]) → 获取完整记忆
      └─ 返回: [
           {memory: "I prefer concise answers", score: 0.92},
           {memory: "Please use Chinese", score: 0.85}
         ]

3. 注入到提示词
   """
   Relevant long-term memories:
   - (0.920) I prefer concise answers
   - (0.850) Please use Chinese
   
   User: How should you answer my questions?
   """

4. 模型回复
   "Based on your preference, I'll provide concise answers in Chinese."
```

### 场景 3：长对话触发摘要

```
对话进行到第 12 轮...

1. append_turn() 检测到超过 10 轮
   ├─ 前 6 轮 → 压缩成摘要
   │  └─ "用户讨论了工作、爱好和编程..."
   └─ 最近 6 轮 → 保留原文

2. 下次对话时
   ├─ build_context() 构建上下文
   │  ├─ summary: "用户讨论了工作、爱好..."
   │  └─ recent_messages: [最近 12 条消息]
   └─ render_context() 渲染为文本
      """
      Session summary:
      用户讨论了工作、爱好和编程...
      
      Recent conversation:
      user: 今天天气怎么样？
      assistant: 今天天气晴朗。
      ...
      """
```

---

## 关键设计模式

### 1. 双重保障（Fallback Pattern）

**Embedding**：
```
远程 API (OpenAI) → 失败 → 本地哈希
```

**Vector Index**：
```
Chroma 数据库 → 失败 → 本地文件
```

**优势**：
- 高可用性：一个方案失败，自动切换
- 开发友好：无需配置即可运行
- 生产就绪：可选择高性能方案

### 2. Repository 模式

**分离关注点**：
```
Service Layer (业务逻辑)
    ↓
Repository Layer (数据访问)
    ↓
Database (SQLite)
```

**优势**：
- 业务逻辑不依赖具体数据库
- 易于测试（可以 mock repository）
- 易于切换数据库（只需实现新的 repository）

### 3. 工厂模式

```python
def build_memory_service(app_config, model_config):
    # 根据配置创建所有组件
    repository = MemoryRepository(...)
    embeddings = EmbeddingProvider(...)
    vector_index = build_vector_index(...)
    
    # 组装服务
    return MemoryService(repository, embeddings, vector_index)
```

**优势**：
- 集中管理依赖创建
- 配置驱动行为
- 易于测试和替换组件

### 4. 门面模式（Facade Pattern）

`MemoryService` 隐藏了底层复杂性：
```python
# 简单的接口
service.add_memory(user_id, text)

# 背后的复杂操作
# 1. 保存到数据库
# 2. 生成向量
# 3. 保存到索引
# 4. 保持一致性
```

---

## 使用示例

### 初始化服务

```python
from backend.memory import build_memory_service
from backend.config import get_app_config, get_model_config

# 创建服务
memory_service = build_memory_service(
    app_config=get_app_config(),
    model_config=get_model_config()
)
```

### 添加记忆

```python
# 手动添加
memory = memory_service.add_memory(
    user_id="user123",
    text="I prefer concise answers",
    tags=["preference"],
    metadata={"source": "manual"}
)

# 自动提取
user_message = "My name is Alice, I like detailed explanations."
extracted = memory_service.extract_and_store("user123", user_message)
```

### 搜索记忆

```python
# 语义搜索
results = memory_service.search_memories(
    user_id="user123",
    query="How should you answer me?",
    top_k=3
)

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Text: {result.memory.text}")
    print(f"Tags: {result.memory.tags}")
```

### 生成上下文

```python
# 生成可注入到提示词的文本
context_text = memory_service.memory_context_text(
    user_id="user123",
    query="current user message",
    top_k=3
)

# 注入到提示词
prompt = f"""
{context_text}

User: {user_message}
Assistant:
"""
```

### 短期记忆管理

```python
from backend.memory import ShortTermMemoryManager

# 创建管理器
stm = ShortTermMemoryManager(
    window_turns=6,
    enable_summary=True,
    summary_trigger_turns=10
)

# 添加对话
stm.append_turn(
    session=session,
    user_message="Hello",
    assistant_message="Hi! How can I help?"
)

# 构建上下文
context = stm.build_context(session)
context_text = stm.render_context(context)
```

---

## 性能优化建议

### 1. 批量操作

```python
# ❌ 不好：多次查询
for memory_id in memory_ids:
    memory = repository.get(memory_id)

# ✅ 好：批量查询
memories = repository.get_many(memory_ids)
```

### 2. 向量索引选择

```python
# 开发环境：使用本地文件
MEMORY_VECTOR_BACKEND=local

# 生产环境：使用 Chroma
MEMORY_VECTOR_BACKEND=chroma
```

### 3. 嵌入缓存

```python
# 相同的文本不需要重复生成向量
# 可以添加缓存层（未实现，可扩展）
```

---

## 常见问题

### Q1: 为什么需要同时保存到数据库和向量索引？

**A**: 
- **数据库**：存储完整信息（文本、标签、元数据、时间戳）
- **向量索引**：只存储向量，用于快速语义搜索
- 两者配合：先用向量索引找到相关 ID，再从数据库获取完整信息

### Q2: 本地哈希方法的向量质量如何？

**A**: 
- 本地哈希是**确定性**的，相同文本总是产生相同向量
- 语义理解较弱，但足够用于开发和小规模应用
- 生产环境建议使用远程 Embedding API

### Q3: 如何处理向量维度不匹配？

**A**: 
- `embed_text()` 方法会自动处理（第 48-70 行）
- 向量太长：截断
- 向量太短：填充 0
- 最后归一化

### Q4: 短期记忆的摘要是如何生成的？

**A**: 
- Phase 2 使用简单的截断方法（第 31-44 行）
- 未来可以使用模型生成更好的摘要
- 当前实现：保留最后 N 个字符

### Q5: 如何扩展到多租户？

**A**: 
- 添加 `tenant_id` 字段
- 修改搜索逻辑：同时过滤 `user_id` 和 `tenant_id`
- 向量索引添加 `tenant_id` 元数据

---

## 扩展点

### 1. 替换数据库

```python
# 实现新的 Repository
class PostgresRepository(BaseRepository):
    def add(self, ...): ...
    def get(self, ...): ...
    # ...

# 在工厂函数中使用
repository = PostgresRepository(...)
```

### 2. 使用模型生成摘要

```python
def _summarize(self, existing_summary, messages):
    # 调用 LLM 生成摘要
    prompt = f"Summarize: {messages}"
    summary = model.generate(prompt)
    return summary
```

### 3. 添加记忆分类

```python
def extract_and_store(self, user_id, user_message):
    # 使用模型分类
    category = classifier.classify(user_message)
    
    if category == "preference":
        return self.add_memory(...)
```

### 4. 添加记忆过期

```python
def cleanup_old_memories(self, days=90):
    """删除超过 N 天的记忆"""
    cutoff = time.time() - (days * 86400)
    # 删除 created_at < cutoff 的记忆
```

---

## 总结

### 核心价值

1. **双重记忆系统**：短期（会话）+ 长期（持久化）
2. **语义搜索**：基于向量相似度，理解用户意图
3. **自动化**：自动提取偏好，自动压缩对话
4. **高可用**：双重保障，降级策略
5. **易扩展**：清晰的接口，模块化设计

### 技术亮点

- **Repository 模式**：分离数据访问和业务逻辑
- **工厂模式**：配置驱动，易于测试
- **门面模式**：简化接口，隐藏复杂性
- **降级策略**：保证系统可用性

### 学习路径

1. 先理解每个文件的单一职责
2. 再理解组件之间的协作
3. 最后理解完整的工作流程
4. 尝试修改和扩展功能

---

**文档版本**: 1.0  
**最后更新**: 2026-03-01  
**作者**: Kiro AI Assistant
