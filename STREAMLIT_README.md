# 智能问答系统 - Streamlit 可视化界面

基于 LangChain + FAISS 的多领域智能问答智能体开发项目的可视化界面系统。

## 功能特性

### 🎯 核心功能
- **智能问答对话** - 支持多轮对话，实时响应
- **知识库管理** - 文档上传、处理、向量化和检索
- **数据统计** - 实时数据展示和交互式图表
- **会话历史** - 历史记录查看、导出和管理
- **系统配置** - 参数配置和性能监控

### 📊 可视化组件
- 交互式图表（饼图、柱状图、折线图）
- 实时数据仪表板
- 响应式布局设计
- 动态数据更新

### 🎨 界面特点
- 现代化UI设计
- 响应式布局（适配不同屏幕）
- 流畅的动画效果
- 直观的导航系统
- 实时交互反馈

## 快速开始

### 环境要求
- Python 3.11+
- pip 包管理器

### 安装步骤

1. **安装依赖**
```bash
pip install -r requirements_streamlit.txt
```

2. **配置环境变量**
设置 DeepSeek API Key:
```bash
set DEEPSEEK_API_KEY=your-api-key-here
```

3. **启动应用**
```bash
streamlit run app.py
```

或使用启动脚本（Windows）:
```bash
start_app.bat
```

4. **访问界面**
浏览器自动打开 http://localhost:8501

## 页面导航

### 💬 智能问答
- 实时对话界面
- 快捷问题按钮
- 检索参数调整
- 对话历史显示

### 📚 知识库管理
- 文档上传（支持TXT、PDF、DOCX）
- 知识库状态监控
- 向量检索测试
- 知识库重建

### 📊 数据统计
- 对话活动统计
- 系统性能指标
- 知识库使用趋势
- 可视化图表展示

### 📝 会话历史
- 历史会话列表
- 会话详情查看
- 会话导出功能
- 历史记录管理

### ⚙️ 系统配置
- LLM参数配置
- 向量检索配置
- 系统信息查看
- 性能监控

## 技术架构

### 前端框架
- **Streamlit** - Python Web应用框架
- **Plotly** - 交互式图表库
- **Pandas** - 数据处理和分析

### 后端集成
- **LangChain** - LLM应用框架
- **FAISS** - 向量相似度搜索
- **DashScope** - 文本嵌入服务
- **DeepSeek** - 大语言模型

### 性能优化
- 响应式设计确保快速加载
- 数据缓存机制
- 异步处理支持
- 资源优化管理

## 配置说明

### Streamlit 配置
配置文件: `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

### 系统配置
配置文件: `config/vector_store_config.py`

```python
LLM_CONFIG.api_key = "your-api-key"
FAISS_CONFIG.index_path = "vector_stores/faiss_index"
```

## 项目结构

```
基于 LangChain + FAISS 的多领域智能问答智能体开发/
├── app.py                      # Streamlit 主应用
├── start_app.bat              # 启动脚本
├── requirements_streamlit.txt # 依赖包列表
├── .streamlit/
│   └── config.toml           # Streamlit 配置
├── config/                    # 配置文件
├── Loader/                    # 文档加载器
├── utils/                     # 工具函数
├── chat_history/             # 会话历史存储
└── vector_stores/            # 向量库存储
```

## 使用指南

### 1. 初始化知识库
1. 导航到"知识库管理"页面
2. 上传文档文件（TXT、PDF、DOCX）
3. 点击"开始上传并处理"
4. 等待文档处理完成

### 2. 开始问答
1. 导航到"智能问答"页面
2. 输入问题或选择快捷问题
3. 查看AI回复和相关文档
4. 继续多轮对话

### 3. 查看统计
1. 导航到"数据统计"页面
2. 查看对话活动图表
3. 监控系统性能指标
4. 分析使用趋势

### 4. 管理会话
1. 导航到"会话历史"页面
2. 选择历史会话查看
3. 导出会话数据
4. 清理历史记录

## 性能指标

- **页面加载时间**: < 3秒
- **响应时间**: < 2秒
- **支持并发**: 多用户同时访问
- **文档处理**: 支持大文件上传

## 故障排除

### 常见问题

**Q: 页面加载缓慢**
A: 检查网络连接，清除浏览器缓存

**Q: API连接失败**
A: 验证API Key配置，检查网络连接

**Q: 知识库加载失败**
A: 确认向量库文件存在，检查文件权限

**Q: 图表不显示**
A: 更新Plotly库，检查浏览器兼容性

## 开发说明

### 添加新页面
1. 在 `app.py` 中创建新的渲染函数
2. 在 `page_router` 字典中注册页面
3. 在侧边栏添加导航按钮

### 自定义样式
编辑 `app.py` 中的CSS样式块:
```python
st.markdown("""
<style>
    .custom-class {
        /* 你的样式 */
    }
</style>
""", unsafe_allow_html=True)
```

### 扩展图表功能
使用Plotly创建自定义图表:
```python
import plotly.express as px
fig = px.scatter(data_frame=df, x='x', y='y')
st.plotly_chart(fig)
```

## 许可证

本项目遵循原项目的许可证条款。

## 联系方式

如有问题或建议，请通过项目Issues反馈。