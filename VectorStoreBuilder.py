# VectorStoreBuilder.py
"""
FAISS 向量库构建模块
"""

import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

from config.vector_store_config import (
    EMBEDDING_CONFIG,
    FAISS_CONFIG,
    RETRIEVAL_CONFIG
)


class VectorStoreService(object):
    """FAISS 向量库服务"""
    
    def __init__(self, embedding=None):
        self.embedding = embedding or DashScopeEmbeddings(
            model=EMBEDDING_CONFIG.model_name
        )
        self.vector_store = None
    
    def create_from_documents(self, documents: List[Document]):
        """从文档列表创建向量库"""
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embedding
        )
        return self.vector_store
    
    def save_local(self, index_path: str = None):
        """保存向量库到本地"""
        index_path = index_path or FAISS_CONFIG.index_path
        index_dir = os.path.dirname(index_path)
        if index_dir and not os.path.exists(index_dir):
            os.makedirs(index_dir)
        
        self.vector_store.save_local(
            folder_path=index_path,
            index_name="index"
        )
    
    def load_local(self, index_path: str = None):
        """从本地加载向量库"""
        index_path = index_path or FAISS_CONFIG.index_path
        
        self.vector_store = FAISS.load_local(
            folder_path=index_path,
            embeddings=self.embedding,
            index_name="index",
            allow_dangerous_deserialization=True
        )
        
        return self.vector_store
    
    def search_similar(self, query: str, k: int = None) -> List[Document]:
        """搜索相似文档"""
        k = k or RETRIEVAL_CONFIG.default_k
        return self.vector_store.similarity_search(query, k=k)
    
    def add_documents(self, documents: List[Document]):
        """向现有向量库添加文档"""
        self.vector_store.add_documents(documents)


def build_vector_store(documents: List[Document],
                      save_path: str = None) -> VectorStoreService:
    """便捷函数：构建并保存向量库"""
    service = VectorStoreService()
    service.create_from_documents(documents)
    
    if save_path:
        service.save_local(index_path=save_path)
    
    return service