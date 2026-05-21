"""
向量存储服务 - 封装 FAISS 向量库操作
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from VectorStoreBuilder import VectorStoreService as _VectorStoreService
from config.vector_store_config import FAISS_CONFIG


class VectorStoreManager:
    """向量库管理器（处理 FAISS C++ Windows 中文路径兼容）"""

    def __init__(self):
        self._service = None

    @property
    def service(self):
        if self._service is None:
            self._service = _VectorStoreService()
        return self._service

    def _with_project_root(self, func, *args, **kwargs):
        """在项目根目录执行FAISS操作，避免中文路径问题"""
        old_cwd = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            return func(*args, **kwargs)
        finally:
            os.chdir(old_cwd)

    def create_from_documents(self, documents):
        return self._with_project_root(self.service.create_from_documents, documents)

    def save_local(self, index_path: str = None):
        path = index_path or FAISS_CONFIG.index_path
        return self._with_project_root(self.service.save_local, path)

    def load_local(self, index_path: str = None):
        path = index_path or FAISS_CONFIG.index_path
        return self._with_project_root(self.service.load_local, path)

    def add_documents(self, documents):
        return self._with_project_root(self.service.add_documents, documents)

    def is_loaded(self):
        return self._service is not None and self._service.vector_store is not None

    def get_status(self):
        info = {
            'loaded': self.is_loaded(),
            'index_path': FAISS_CONFIG.index_path,
            'vector_count': 0,
        }
        if self.is_loaded():
            try:
                info['vector_count'] = self._service.vector_store.index.ntotal
            except Exception:
                pass
        return info


vector_store_manager = VectorStoreManager()
