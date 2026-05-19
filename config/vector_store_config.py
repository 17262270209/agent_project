"""
向量存储和 LLM 配置 - 使用 Pydantic 进行类型安全管理
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingConfig(BaseSettings):
    """Embedding 模型配置"""
    model_name: str = "text-embedding-v4"
    
    model_config = SettingsConfigDict(env_prefix="EMBEDDING_")


class FAISSConfig(BaseSettings):
    """FAISS 向量库配置"""
    index_path: str = "vector_stores/faiss_index"
    
    model_config = SettingsConfigDict(env_prefix="FAISS_")


class RetrievalConfig(BaseSettings):
    """向量检索配置"""
    default_k: int = 5
    score_threshold: float = 0.7
    
    model_config = SettingsConfigDict(env_prefix="RETRIEVAL_")


class LLMConfig(BaseSettings):
    """LLM 配置（DeepSeek）"""
    model_name: str = "deepseek-chat"
    api_key: str = os.getenv('DEEPSEEK_API_KEY', '')
    base_url: str = "https://api.deepseek.com/v1"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    model_config = SettingsConfigDict(env_prefix="DEEPSEEK_")
    
    def validate_api_key(self) -> None:
        """验证 API Key 是否设置"""
        if not self.api_key or self.api_key.strip() == '':
            raise ValueError(
                "未设置 DeepSeek API Key！\n"
                "请设置环境变量: export DEEPSEEK_API_KEY=your-key\n"
                "获取 API Key: https://platform.deepseek.com/"
            )


# 创建配置实例
EMBEDDING_CONFIG = EmbeddingConfig()
FAISS_CONFIG = FAISSConfig()
RETRIEVAL_CONFIG = RetrievalConfig()
LLM_CONFIG = LLMConfig()

# 完整的配置
VECTOR_STORE_CONFIG = {
    'embedding': EMBEDDING_CONFIG.model_dump(),
    'faiss': FAISS_CONFIG.model_dump(),
    'retrieval': RETRIEVAL_CONFIG.model_dump(),
}