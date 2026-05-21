"""
RAG 服务 - 封装 RAG 问答链
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAGChain import RAGChain as _RAGChain
from LLMService import LLMService as _LLMService
from VectorStoreBuilder import VectorStoreService as _VectorStoreService
from ChatHistoryService import FileChatMessageHistory


class RAGService:
    """RAG 问答服务（Django 适配层）"""

    def __init__(self):
        self._llm_service = None
        self._vector_store_service = None
        self._rag_chain = None
        self._current_session_id = None

    def _get_llm_service(self):
        if self._llm_service is None:
            self._llm_service = _LLMService()
        return self._llm_service

    def init_vector_store(self, index_path: str = None):
        """初始化向量存储（处理 FAISS C++ 中文路径兼容问题）"""
        if index_path is None:
            from config.vector_store_config import FAISS_CONFIG
            index_path = FAISS_CONFIG.index_path

        # FAISS C++ 在 Windows 上无法处理含中文的绝对路径
        # 切换到项目根目录后使用相对路径加载
        old_cwd = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            service = _VectorStoreService()
            service.load_local(index_path)
            self._vector_store_service = service
        finally:
            os.chdir(old_cwd)
        return self._vector_store_service

    def get_rag_chain(self, session_id: str = "default"):
        """获取或创建 RAG 链"""
        if self._vector_store_service is None:
            return None
        if self._vector_store_service.vector_store is None:
            return None

        if self._rag_chain is None or self._current_session_id != session_id:
            self._current_session_id = session_id
            # 使用项目根目录下的 chat_history，与 ChatHistoryManager 统一
            storage_path = os.path.join(PROJECT_ROOT, 'chat_history')
            self._rag_chain = _RAGChain(
                vector_store_service=self._vector_store_service,
                llm_service=self._get_llm_service(),
                session_id=session_id,
                storage_path=storage_path,
            )
        return self._rag_chain

    def ask(self, query: str, session_id: str = "default", k: int = 5) -> dict:
        """执行 RAG 问答"""
        rag_chain = self.get_rag_chain(session_id)
        if rag_chain is None:
            return {
                "question": query,
                "answer": "知识库未加载，请先上传文档。",
                "context_docs": [],
                "session_id": session_id,
            }
        return rag_chain.ask(query, k=k)

    def get_chat_history(self, session_id: str):
        """获取会话历史"""
        history = FileChatMessageHistory(session_id)
        return history.messages

    def clear_chat_history(self, session_id: str):
        """清空会话历史"""
        history = FileChatMessageHistory(session_id)
        history.clear()

    def delete_chat_history(self, session_id: str):
        """删除会话历史"""
        history = FileChatMessageHistory(session_id)
        history.delete()

    def search_similar(self, query: str, k: int = 5):
        """相似文档检索"""
        if self._vector_store_service is None:
            return []
        return self._vector_store_service.search_similar(query, k=k)


rag_service = RAGService()
