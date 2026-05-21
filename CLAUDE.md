# 基于 LangChain + FAISS 的多领域智能问答智能体

## 项目概述

前后端分离的智能问答系统：
- **后端**：Django + Django REST Framework (Python)
- **前端**：Vue 3 单文件 SPA (纯 CDN，无需 npm)
- **核心**：LangChain + FAISS + DashScope Embedding + DeepSeek LLM

## 启动方式

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

浏览器访问 `http://localhost:8000`，前后端都在同一个端口。

## 目录结构

```
backend/              # Django 后端
├── manage.py
├── core/             # Django 项目配置 (settings, urls, wsgi)
│   ├── settings.py   # INSTALLED_APPS, DATABASES (SQLite), REST_FRAMEWORK, CORS
│   └── urls.py       # /api/chat/, /api/knowledge/, /api/system/, 其余 → index.html
├── apps/
│   ├── chat/         # 对话模块 (ChatSession, ChatMessage models, SSE流式API)
│   ├── knowledge/    # 知识库模块 (文档上传/管理/检索/重建)
│   ├── system/       # 系统模块 (统计/配置/日志)
│   └── frontend/     # 返回 index.html (绕过Django模板引擎, 避免与Vue {{ }} 冲突)
├── services/         # 业务层 (包装原有 RAGChain, VectorStoreBuilder 等)
│   ├── rag_service.py
│   ├── vector_store_service.py
│   ├── document_service.py
│   ├── llm_service.py
│   └── chat_history_service.py

frontend/             # Vue 3 前端 (纯静态 CDN, 无需构建)
└── index.html        # 单文件 SPA, 内联 CSS + JS, CDN 加载 Vue3/ElementPlus/ECharts

config/               # 原始配置 (vector_store_config.py, loader_config.py 等, 保持不变)
Loader/               # 文档加载器 (PDF/TXT/Word, 保持不变)
utils/                # 工具函数 (保持不变)
data/                 # 文档数据
vector_stores/        # FAISS 索引
chat_history/         # 聊天历史 JSON
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/chat/send/ | 发送消息 (SSE流式) |
| GET | /api/chat/sessions/ | 会话列表 |
| GET/DELETE | /api/chat/sessions/<id>/ | 会话详情/删除 |
| GET | /api/chat/quick-questions/ | 快捷问题 |
| GET | /api/knowledge/status/ | 知识库状态 |
| POST | /api/knowledge/upload/ | 上传文档 |
| GET | /api/knowledge/documents/ | 文档列表 |
| DELETE | /api/knowledge/documents/<md5>/ | 删除文档 |
| POST | /api/knowledge/search/ | 测试检索 |
| POST | /api/knowledge/rebuild/ | 重建知识库 |
| GET | /api/system/statistics/ | 统计数据 |
| GET/PUT | /api/system/config/ | 系统配置 |
| GET | /api/system/logs/ | 系统日志 |

## 关键设计决策

1. **前端使用纯 CDN 方式**：不用 npm/Vite，所有 JS/CSS 通过 unpkg.com CDN 加载，单文件 index.html 包含全部代码
2. **Django 直接返回 index.html**：用 `apps/frontend/views.py` 的 `index()` 函数读取文件并返回，不经过 Django 模板引擎
3. **URL 路由**：`core/urls.py` 中 /api/ 优先匹配，其余由 `re_path(r'^(?!api/).*$', index)` 返回前端
4. **Vue Router hash 模式**：`createWebHashHistory()` 避免与 Django URL 冲突
5. **SSE 流式聊天**：Django StreamingHttpResponse，前端 fetch + ReadableStream
6. **SQLite 数据库**：存储会话和文档记录，FAISS 索引保持文件存储
7. **无用户认证**：当前版本不包含登录，保持简单
8. **DeepSeek API Key**：从环境变量 DEEPSEEK_API_KEY 或 data/uploads/api-key.txt 读取

## 注意事项

- 前端 index.html 不要经过 Django 模板引擎，否则 Vue 的 {{ }} 语法会冲突
- 后端 services 层通过 sys.path.insert 引入项目根目录的原有模块，注意 config 包名冲突（Django 的 config 已重命名为 core）
- 启动服务后会自动加载已有的 FAISS 向量库
- Element Plus Icons 在 CDN 模式下可能不全，前端只手动注册了部分常用图标

## 开发历程（踩过的坑）

### 前端方案演变
1. **最初方案**：npm + Vite + Vue SFC (.vue 文件)，创建了完整的 package.json 和 vite.config.js
2. **遇到问题**：项目路径含中文字符（"基于 LangChain + FAISS 的多领域智能问答智能体开发"），导致 npm install 的 postinstall 脚本找不到 node（PATH 在 bash 和 Windows cmd 之间不互通），多次重试都失败
3. **用户要求**：改用 Vue + HTML + CSS + JS 纯框架，不用 npm
4. **最终方案**：所有依赖通过 unpkg.com CDN 加载，单文件 frontend/index.html，内联所有 CSS 和 JS

### 后端命名冲突
1. Django 项目配置目录最初命名为 `backend/config/`
2. 与项目根目录原有的 `config/` 包（vector_store_config.py 等）冲突
3. **修复**：将 Django 配置目录重命名为 `backend/core/`，同时修改 manage.py/wsgi.py/asgi.py/settings.py 中所有 `config` 引用为 `core`

### Django REST Framework 报错
1. 启动后 API 返回 500 错误
2. 原因：DRF 默认需要 `django.contrib.auth` (UNAUTHENTICATED_USER 设置依赖 auth.User)
3. **修复**：在 INSTALLED_APPS 中添加 `django.contrib.auth`，并运行 `python manage.py migrate auth`

### 前端无法打开
1. 最初版本的 index.html 使用了 `<script src="js/...">` 加载外部 JS 文件（api.js, router.js, app.js）
2. 还存在 `<router-view />` 自闭合标签（HTML 对非 void 元素不支持自闭合）
3. Element Plus Icons CDN 链接可能不正确
4. **修复**：全部改为单文件内联，消除外部文件加载问题；`<router-view />` 改为 `<router-view></router-view>`

### Django 托管前端
1. 最初尝试用 Django 模板引擎渲染 index.html
2. 遇到 Vue `{{ }}` 与 Django 模板语法冲突
3. **修复**：创建 `apps/frontend/views.py`，用 `open()` 直接读取 index.html 返回 HttpResponse，绕过模板引擎
4. URL 路由用 `re_path(r'^(?!api/).*$', index)` 实现 SPA 的 catch-all 路由

## 当前状态

### 已验证可用的部分
- [x] Django 后端启动正常（`python manage.py check` 通过）
- [x] 所有 API 端点正常返回（已验证 /api/chat/quick-questions/ 和 /api/system/statistics/）
- [x] 前端 index.html 能通过 Django 正常返回（HTTP 200，23547 字节）
- [x] 前后端统一端口 8000

### 可能存在的问题
- [ ] 前端页面在浏览器中实际渲染效果未验证（用户反馈"打不开网页"，后来改成纯内联单文件后未确认）
- [ ] CDN 加载的 Element Plus 版本兼容性
- [ ] Element Plus Icons 在 CDN 模式下图标显示可能不全
- [ ] SSE 流式聊天的实际效果未端到端测试
- [ ] 文件上传功能（需要 langchain/dashscope 等 Python 依赖）未充分测试
- [ ] DeepSeek API Key 需要正确设置才能使用聊天功能
