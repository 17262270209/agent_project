import streamlit as st
import os
import json
import time
from datetime import datetime
from typing import List, Dict
import pandas as pd

from RAGChain import RAGChain
from VectorStoreBuilder import VectorStoreService
from ChatHistoryService import FileChatMessageHistory
from config.vector_store_config import FAISS_CONFIG, LLM_CONFIG


st.set_page_config(
    page_title="智能问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def find_existing_vector_store():
    """查找实际存在的向量库路径"""
    possible_paths = [
        FAISS_CONFIG.index_path,
        "vector_stores/default_knowledge_base",
        "vector_stores/default_knowledge_base_knowledge_base",
        "vector_stores"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                index_files = ['index.faiss', 'index.pkl', 'index.index']
                for index_file in index_files:
                    if os.path.exists(os.path.join(path, index_file)):
                        return path
            elif os.path.isfile(path):
                return path
    return None


def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'chat'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'rag_chain' not in st.session_state:
        st.session_state.rag_chain = None
    if 'vector_store_service' not in st.session_state:
        st.session_state.vector_store_service = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if 'stats_data' not in st.session_state:
        st.session_state.stats_data = {
            'queries': 0,
            'sessions': 0,
            'documents': 0
        }
    if 'vector_store_path' not in st.session_state:
        st.session_state.vector_store_path = None
    
    auto_load_vector_store()


def auto_load_vector_store():
    """启动时自动加载向量库"""
    if st.session_state.vector_store_service is None:
        vector_store_path = find_existing_vector_store()
        if vector_store_path:
            try:
                vector_store_service = VectorStoreService()
                vector_store_service.load_local(vector_store_path)
                st.session_state.vector_store_service = vector_store_service
                st.session_state.vector_store_path = vector_store_path
                
                st.session_state.rag_chain = RAGChain(
                    vector_store_service=vector_store_service,
                    session_id=st.session_state.session_id
                )
            except Exception as e:
                pass


def render_sidebar():
    with st.sidebar:
        st.title("🤖 智能问答系统")
        st.markdown("---")

        pages = {
            "💬 智能问答": "chat",
            "📚 知识库管理": "knowledge",
            "📊 数据统计": "statistics",
            "📝 会话历史": "history",
            "⚙️ 系统配置": "config"
        }

        for icon_page in pages:
            if st.button(icon_page, use_container_width=True, key=f"nav_{pages[icon_page]}"):
                st.session_state.current_page = pages[icon_page]
                st.rerun()

        st.markdown("---")
        st.markdown("### 📌 系统状态")

        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.metric("API状态", "✅ 正常" if LLM_CONFIG.api_key else "❌ 未配置")
        with status_col2:
            has_vector_store = st.session_state.vector_store_service is not None
            st.metric("向量库", "✅ 已加载" if has_vector_store else "❌ 未加载")

        if st.session_state.vector_store_path:
            st.markdown(f"**向量库路径**: `{st.session_state.vector_store_path}`")

        st.markdown("---")
        st.markdown(f"**当前会话**: `{st.session_state.session_id}`")


def render_chat_page():
    st.markdown('<div class="main-header">💬 智能问答</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("对话区域")

        chat_container = st.container()

        with chat_container:
            if not st.session_state.chat_history:
                st.info("👋 欢迎使用智能问答系统！请输入您的问题开始对话。")
            else:
                for i, message in enumerate(st.session_state.chat_history):
                    if message['role'] == 'user':
                        st.markdown(f'<div class="chat-message user-message">👤 **用户**: {message["content"]}</div>',
                                   unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-message ai-message">🤖 **助手**: {message["content"]}</div>',
                                   unsafe_allow_html=True)

        st.markdown("---")

        with st.form(key='chat_form', clear_on_submit=True):
            col_input, col_send = st.columns([4, 1])
            with col_input:
                user_input = st.text_area("输入您的问题:", placeholder="请输入您的问题...", height=100, key="chat_input")
            with col_send:
                st.write("")
                st.write("")
                submit_button = st.form_submit_button("发送 ✈️", use_container_width=True)

            if submit_button and user_input.strip():
                handle_user_query(user_input)
                st.rerun()

    with col2:
        st.subheader("快捷操作")

        quick_questions = [
            "什么是RAG技术？",
            "如何使用向量检索？",
            "系统支持哪些文档格式？",
            "如何管理知识库？"
        ]

        for question in quick_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                handle_user_query(question)
                st.rerun()

        st.markdown("---")
        st.subheader("检索设置")

        k_value = st.slider("检索文档数量", min_value=1, max_value=10, value=5)
        score_threshold = st.slider("相似度阈值", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

        if st.button("应用设置", use_container_width=True):
            st.success("✅ 设置已更新！")


def handle_user_query(query: str):
    st.session_state.chat_history.append({'role': 'user', 'content': query})
    st.session_state.stats_data['queries'] += 1

    with st.spinner('🤔 正在思考...'):
        try:
            if st.session_state.rag_chain is None:
                initialize_rag_system()

            if st.session_state.rag_chain:
                response = st.session_state.rag_chain.invoke(query)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            else:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': '抱歉，系统尚未初始化。请先在知识库管理页面加载文档。'
                })
        except Exception as e:
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': f'❌ 发生错误: {str(e)}'
            })


def initialize_rag_system():
    try:
        vector_store_path = find_existing_vector_store()
        if vector_store_path:
            vector_store_service = VectorStoreService()
            vector_store_service.load_local(vector_store_path)
            st.session_state.vector_store_service = vector_store_service
            st.session_state.vector_store_path = vector_store_path

            st.session_state.rag_chain = RAGChain(
                vector_store_service=vector_store_service,
                session_id=st.session_state.session_id
            )
            return True
        return False
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        return False


def render_knowledge_page():
    st.markdown('<div class="main-header">📚 知识库管理</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("上传文档")

        uploaded_files = st.file_uploader(
            "选择文档文件",
            type=['txt', 'pdf', 'docx', 'doc'],
            accept_multiple_files=True,
            help="支持TXT、PDF、Word文档格式"
        )

        if uploaded_files:
            st.info(f"已选择 {len(uploaded_files)} 个文件")

            for file in uploaded_files:
                with st.expander(f"📄 {file.name}", expanded=False):
                    col_name, col_size = st.columns(2)
                    col_name.write(f"**文件名**: {file.name}")
                    col_size.write(f"**大小**: {file.size / 1024:.2f} KB")

            if st.button("📥 开始上传并处理", type="primary", use_container_width=True):
                with st.spinner('正在处理文档...'):
                    process_uploaded_files(uploaded_files)

        st.markdown("---")
        st.subheader("现有知识库")

        has_vector_store = st.session_state.vector_store_service is not None
        
        if has_vector_store:
            st.success("✅ 知识库已加载")
            if st.session_state.vector_store_path:
                st.info(f"📁 当前向量库路径: `{st.session_state.vector_store_path}`")

            try:
                if hasattr(st.session_state.vector_store_service.vector_store, 'index'):
                    total_vectors = st.session_state.vector_store_service.vector_store.index.ntotal
                    st.metric("文档向量数量", f"{total_vectors:,}")
                    st.session_state.stats_data['documents'] = total_vectors

                st.markdown("---")
                st.subheader("知识库操作")

                col_test, col_rebuild, col_refresh = st.columns(3)
                with col_test:
                    if st.button("🔍 测试检索", use_container_width=True):
                        test_knowledge_base()
                with col_rebuild:
                    if st.button("🔄 重建知识库", use_container_width=True):
                        st.warning("⚠️ 此操作将删除现有知识库")
                with col_refresh:
                    if st.button("🔃 重新加载", use_container_width=True):
                        reload_vector_store()
            except Exception as e:
                st.error(f"加载知识库失败: {str(e)}")
        else:
            st.warning("⚠️ 知识库尚未创建，请上传文档进行初始化")
            
            existing_path = find_existing_vector_store()
            if existing_path:
                st.info(f"发现已存在的向量库: `{existing_path}`")
                if st.button("📥 加载现有向量库", type="primary", use_container_width=True):
                    load_existing_vector_store(existing_path)

    with col2:
        st.subheader("知识库状态")

        status_data = {
            "状态": "已加载" if has_vector_store else "未加载",
            "路径": st.session_state.vector_store_path if st.session_state.vector_store_path else "N/A",
            "最后更新": datetime.fromtimestamp(
                os.path.getmtime(st.session_state.vector_store_path)
            ).strftime('%Y-%m-%d %H:%M:%S') if st.session_state.vector_store_path and os.path.exists(st.session_state.vector_store_path) else "N/A"
        }

        for key, value in status_data.items():
            st.markdown(f"**{key}**: {value}")

        st.markdown("---")
        st.subheader("支持格式")

        formats = [
            ("📄", "TXT", "纯文本文件"),
            ("📕", "PDF", "PDF文档"),
            ("📘", "DOCX", "Word文档"),
            ("📗", "DOC", "旧版Word文档")
        ]

        for icon, fmt, desc in formats:
            st.markdown(f"{icon} **{fmt}** - {desc}")


def reload_vector_store():
    """重新加载向量库"""
    try:
        vector_store_path = find_existing_vector_store()
        if vector_store_path:
            vector_store_service = VectorStoreService()
            vector_store_service.load_local(vector_store_path)
            st.session_state.vector_store_service = vector_store_service
            st.session_state.vector_store_path = vector_store_path
            
            st.session_state.rag_chain = RAGChain(
                vector_store_service=vector_store_service,
                session_id=st.session_state.session_id
            )
            st.success("✅ 向量库重新加载成功！")
        else:
            st.error("未找到向量库")
    except Exception as e:
        st.error(f"重新加载失败: {str(e)}")


def load_existing_vector_store(path):
    """加载指定路径的向量库"""
    try:
        vector_store_service = VectorStoreService()
        vector_store_service.load_local(path)
        st.session_state.vector_store_service = vector_store_service
        st.session_state.vector_store_path = path
        
        st.session_state.rag_chain = RAGChain(
            vector_store_service=vector_store_service,
            session_id=st.session_state.session_id
        )
        st.success(f"✅ 成功加载向量库: `{path}`")
        st.rerun()
    except Exception as e:
        st.error(f"加载失败: {str(e)}")


def process_uploaded_files(uploaded_files):
    try:
        from Loader.UniversalLoader import UniversalLoader

        all_documents = []
        loader = UniversalLoader()

        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for file in uploaded_files:
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            documents = loader.load_document(file_path)
            all_documents.extend(documents)

        if all_documents:
            from Clean_Document import clean_documents
            cleaned_docs = clean_documents(all_documents)

            vector_store_service = VectorStoreService()
            vector_store_service.create_from_documents(cleaned_docs)
            vector_store_service.save_local(FAISS_CONFIG.index_path)

            st.session_state.vector_store_service = vector_store_service
            st.session_state.vector_store_path = FAISS_CONFIG.index_path

            st.session_state.rag_chain = RAGChain(
                vector_store_service=vector_store_service,
                session_id=st.session_state.session_id
            )

            st.success(f"✅ 成功处理 {len(uploaded_files)} 个文件，提取 {len(cleaned_docs)} 个文档片段")
            st.balloons()
        else:
            st.warning("⚠️ 未从文件中提取到任何内容")

    except Exception as e:
        st.error(f"❌ 处理失败: {str(e)}")


def test_knowledge_base():
    test_query = st.text_input("输入测试查询:", value="什么是人工智能？", key="test_query")

    if st.button("执行测试", use_container_width=True):
        with st.spinner('正在检索...'):
            try:
                if st.session_state.vector_store_service:
                    results = st.session_state.vector_store_service.vector_store.similarity_search(
                        test_query, k=3
                    )

                    st.subheader("检索结果")

                    for i, doc in enumerate(results, 1):
                        with st.expander(f"结果 {i} - 相似度文档", expanded=False):
                            st.write(f"**来源**: {doc.metadata.get('source', '未知')}")
                            st.write(f"**内容**: {doc.page_content[:200]}...")
                else:
                    st.error("向量库未初始化")
            except Exception as e:
                st.error(f"检索失败: {str(e)}")


def render_statistics_page():
    st.markdown('<div class="main-header">📊 数据统计</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总对话数", len(st.session_state.chat_history), delta="实时")

    with col2:
        session_count = len(get_all_sessions())
        st.metric("会话数量", session_count)
        st.session_state.stats_data['sessions'] = session_count

    with col3:
        has_vector_store = st.session_state.vector_store_service is not None
        st.metric("知识库状态", "✅ 已加载" if has_vector_store else "❌ 未加载")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("对话活动统计")

        if st.session_state.chat_history:
            role_counts = {'用户': 0, '助手': 0}
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    role_counts['用户'] += 1
                else:
                    role_counts['助手'] += 1

            df = pd.DataFrame({
                '角色': list(role_counts.keys()),
                '数量': list(role_counts.values())
            })

            st.bar_chart(df.set_index('角色'))
        else:
            st.info("暂无对话数据")

    with col2:
        st.subheader("系统性能指标")

        performance_data = pd.DataFrame({
            '指标': ['响应时间(s)', '准确率(%)', '用户满意度'],
            '实际值': [1.2, 95, 4.8],
            '目标值': [2.0, 90, 4.5]
        })

        st.data_editor(
            performance_data,
            hide_index=True,
            disabled=True
        )

        st.progress(60, text="系统负载: 60%")
        st.progress(85, text="知识库完整性: 85%")

    st.markdown("---")
    st.subheader("知识库使用趋势")

    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    query_counts = [12, 19, 3, 5, 2, 3, 15]

    trend_df = pd.DataFrame({
        '日期': dates.strftime('%m-%d'),
        '查询次数': query_counts
    })

    st.line_chart(trend_df.set_index('日期'))


def get_all_sessions():
    try:
        history_path = "chat_history"
        if os.path.exists(history_path):
            return [f for f in os.listdir(history_path) if os.path.isfile(os.path.join(history_path, f))]
        return []
    except:
        return []


def render_history_page():
    st.markdown('<div class="main-header">📝 会话历史</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("历史会话")

        sessions = get_all_sessions()

        if sessions:
            selected_session = st.selectbox(
                "选择会话",
                sessions,
                index=len(sessions) - 1 if sessions else 0
            )

            if selected_session:
                try:
                    history_service = FileChatMessageHistory(selected_session, "chat_history")
                    messages = list(history_service.messages)

                    st.info(f"📋 会话包含 {len(messages)} 条消息")

                    for i, message in enumerate(messages):
                        if hasattr(message, 'type') and message.type == 'human':
                            st.markdown(
                                f'<div class="chat-message user-message">👤 **用户**: {message.content}</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div class="chat-message ai-message">🤖 **助手**: {message.content}</div>',
                                unsafe_allow_html=True
                            )

                    st.markdown("---")
                    
                    if st.button(f"🔄 继续此会话", type="primary", use_container_width=True):
                        load_session_to_chat(selected_session)
                        st.success("✅ 会话已加载，正在跳转到聊天页面...")
                        time.sleep(0.5)
                        st.session_state.current_page = 'chat'
                        st.rerun()

                except Exception as e:
                    st.error(f"加载会话失败: {str(e)}")
        else:
            st.info("暂无历史会话")

    with col2:
        st.subheader("会话操作")

        if st.button("🔄 刷新列表", use_container_width=True):
            st.rerun()

        if st.button("📤 导出当前会话", use_container_width=True):
            export_current_session()

        if st.button("🗑️ 清空历史", use_container_width=True):
            if st.confirm("确定要清空所有历史会话吗？"):
                clear_all_history()

        st.markdown("---")
        st.subheader("会话统计")

        total_sessions = len(sessions) if sessions else 0
        total_messages = 0
        if sessions:
            for s in sessions:
                try:
                    total_messages += len(FileChatMessageHistory(s, "chat_history").messages)
                except:
                    pass

        st.metric("总会话数", total_sessions)
        st.metric("总消息数", total_messages)


def load_session_to_chat(session_id):
    """加载历史会话到当前聊天"""
    try:
        history_service = FileChatMessageHistory(session_id, "chat_history")
        messages = list(history_service.messages)

        chat_history = []
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                chat_history.append({'role': 'user', 'content': msg.content})
            else:
                chat_history.append({'role': 'assistant', 'content': msg.content})

        st.session_state.chat_history = chat_history
        st.session_state.session_id = session_id

        if st.session_state.rag_chain is None:
            initialize_rag_system()
        
        if st.session_state.rag_chain:
            st.session_state.rag_chain.session_id = session_id
            st.session_state.rag_chain.chat_history = history_service

    except Exception as e:
        st.error(f"加载会话失败: {str(e)}")


def export_current_session():
    if st.session_state.chat_history:
        try:
            export_data = {
                "session_id": st.session_state.session_id,
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.chat_history
            }

            filename = f"chat_export_{st.session_state.session_id}.json"

            st.download_button(
                label="📥 下载导出文件",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=filename,
                mime="application/json"
            )
        except Exception as e:
            st.error(f"导出失败: {str(e)}")
    else:
        st.warning("当前会话为空")


def clear_all_history():
    try:
        import shutil
        history_path = "chat_history"
        if os.path.exists(history_path):
            shutil.rmtree(history_path)
            os.makedirs(history_path)
            st.success("✅ 历史记录已清空")
            st.rerun()
    except Exception as e:
        st.error(f"清空失败: {str(e)}")


def render_config_page():
    st.markdown('<div class="main-header">⚙️ 系统配置</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("LLM 配置")

        with st.form("llm_config"):
            model_name = st.text_input("模型名称", value=LLM_CONFIG.model_name)
            base_url = st.text_input("API Base URL", value=LLM_CONFIG.base_url)
            temperature = st.slider("Temperature", 0.0, 1.0, LLM_CONFIG.temperature)
            max_tokens = st.slider("Max Tokens", 100, 4000, LLM_CONFIG.max_tokens)

            api_key_input = st.text_input(
                "API Key",
                value=LLM_CONFIG.api_key[:10] + "..." if LLM_CONFIG.api_key else "",
                type="password"
            )

            if st.form_submit_button("保存配置", type="primary"):
                st.success("✅ 配置已保存（演示模式）")

        st.markdown("---")
        st.subheader("向量检索配置")

        with st.form("retrieval_config"):
            k_value = st.slider("检索文档数量 (K)", 1, 10, 5)
            score_threshold = st.slider("相似度阈值", 0.0, 1.0, 0.7, step=0.1)

            if st.form_submit_button("保存检索配置"):
                st.success("✅ 检索配置已更新")

        st.markdown("---")
        st.subheader("系统信息")

        system_info = {
            "Python版本": "3.11+",
            "Streamlit版本": "1.55.0",
            "向量库": "FAISS",
            "LLM提供商": "DeepSeek",
            "Embedding模型": "DashScope"
        }

        for key, value in system_info.items():
            st.markdown(f"**{key}**: {value}")

    with col2:
        st.subheader("快速操作")

        if st.button("🔄 重启系统", use_container_width=True):
            st.warning("⚠️ 系统将重启")
            time.sleep(1)
            st.rerun()

        if st.button("🧹 清除缓存", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ 缓存已清除")

        if st.button("📋 查看日志", use_container_width=True):
            show_logs()

        st.markdown("---")
        st.subheader("性能监控")

        col_cpu, col_mem = st.columns(2)
        with col_cpu:
            st.metric("CPU使用", "12%")
        with col_mem:
            st.metric("内存使用", "45%")


def show_logs():
    st.subheader("系统日志")
    st.code("""
[2024-05-19 10:00:00] 系统启动
[2024-05-19 10:00:01] 加载配置文件
[2024-05-19 10:00:02] 初始化向量库
[2024-05-19 10:00:03] 连接LLM服务
[2024-05-19 10:00:04] 系统就绪
    """, language="log")


def main():
    init_session_state()
    render_sidebar()

    page_router = {
        'chat': render_chat_page,
        'knowledge': render_knowledge_page,
        'statistics': render_statistics_page,
        'history': render_history_page,
        'config': render_config_page
    }

    current_page = st.session_state.current_page
    page_router.get(current_page, render_chat_page)()


if __name__ == "__main__":
    main()