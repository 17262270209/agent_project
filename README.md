# 基于 LangChain + FAISS 的多领域智能问答智能体

基于 LangChain + FAISS 向量检索 + DeepSeek 大模型的智能问答系统，支持多领域知识库管理、文档上传与检索、流式对话等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django + Django REST Framework |
| 前端 | Vue 3 (CDN) + Element Plus + ECharts |
| 向量数据库 | FAISS |
| Embedding | DashScope (阿里云) |
| LLM | DeepSeek |
| 文档处理 | LangChain (PDF/TXT/Word) |
| 数据库 | SQLite |

## 功能特性

- **多领域知识库**：支持创建和管理多个知识库，每个知识库独立索引
- **文档管理**：支持 PDF、TXT、Word 文档的上传、解析与向量化
- **智能检索**：基于 FAISS 的语义相似度检索，支持 Top-K 结果返回
- **流式对话**：SSE (Server-Sent Events) 流式输出，实时显示 LLM 回复
- **对话历史**：会话管理，支持历史记录查看与切换
- **系统监控**：知识库统计、文档数量、存储占用等仪表盘

## 快速开始

### 环境要求

- Python 3.9+
- 依赖包见下方安装步骤

### 安装与运行

```bash
# 1. 克隆项目
git clone https://github.com/17262270209/agent_project.git
cd agent_project

# 2. 安装 Python 依赖
pip install django djangorestframework django-cors-headers
pip install langchain langchain-community faiss-cpu dashscope
pip install python-docx openai

# 3. 设置 DeepSeek API Key（二选一）
# 方式一：环境变量
export DEEPSEEK_API_KEY="your-api-key"
# 方式二：写入文件（后端启动时自动读取）
echo "your-api-key" > data/uploads/api-key.txt

# 4. 初始化数据库
cd backend
python manage.py migrate

# 5. 启动服务
python manage.py runserver 0.0.0.0:8000
```

浏览器访问 `http://localhost:8000`，前后端统一端口。

## 目录结构

```
├── backend/                # Django 后端
│   ├── manage.py
│   ├── core/               # Django 配置 (settings, urls, wsgi)
│   └── apps/
│       ├── chat/           # 对话模块 (会话管理, SSE流式)
│       ├── knowledge/      # 知识库模块 (上传/检索/重建)
│       ├── system/         # 系统模块 (统计/配置/日志)
│       └── frontend/       # 前端入口 (返回 index.html)
├── frontend/
│   └── index.html          # Vue 3 单文件 SPA (CDN 加载, 无需构建)
├── services/               # 业务逻辑层
│   ├── rag_service.py      # RAG 检索增强生成
│   ├── vector_store_service.py
│   ├── document_service.py
│   ├── llm_service.py
│   └── chat_history_service.py
├── config/                 # 配置 (向量库配置, 文档加载配置等)
├── Loader/                 # 文档加载器 (PDF/TXT/Word)
├── utils/                  # 工具函数
├── data/                   # 文档数据存储
├── vector_stores/          # FAISS 索引文件
└── chat_history/           # 聊天历史 JSON
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/send/` | 发送消息 (SSE 流式) |
| GET | `/api/chat/sessions/` | 会话列表 |
| GET | `/api/chat/sessions/<id>/` | 会话详情 |
| DELETE | `/api/chat/sessions/<id>/` | 删除会话 |
| GET | `/api/chat/quick-questions/` | 快捷问题 |
| GET | `/api/knowledge/status/` | 知识库状态 |
| POST | `/api/knowledge/upload/` | 上传文档 |
| GET | `/api/knowledge/documents/` | 文档列表 |
| DELETE | `/api/knowledge/documents/<md5>/` | 删除文档 |
| POST | `/api/knowledge/search/` | 测试检索 |
| POST | `/api/knowledge/rebuild/` | 重建知识库 |
| GET | `/api/system/statistics/` | 统计数据 |
| GET | `/api/system/config/` | 系统配置 |
| PUT | `/api/system/config/` | 更新配置 |
| GET | `/api/system/logs/` | 系统日志 |

## 架构说明

- **前端使用纯 CDN 方式**：不依赖 npm/webpack，Vue 3 / Element Plus / ECharts 通过 unpkg.com 加载，单文件 `frontend/index.html` 包含全部代码
- **Vue Router Hash 模式**：`createWebHashHistory()` 避免与 Django URL 路由冲突
- **前后端统一端口**：Django 直接返回 `index.html`，绕过模板引擎避免 `{{ }}` 语法冲突
- **SSE 流式输出**：Django `StreamingHttpResponse`，前端 `fetch` + `ReadableStream` 实现打字机效果
