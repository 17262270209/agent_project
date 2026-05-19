# LLMService.py
"""
DeepSeek LLM 服务

提供 LLM 模型初始化和调用功能
"""

import os
from langchain_openai import ChatOpenAI

from config.vector_store_config import LLM_CONFIG


class LLMService(object):
    """DeepSeek LLM 服务"""

    def __init__(self, llm=None):
        """
        初始化 LLM 服务

        Args:
            llm: LLM 实例，如果为 None 则自动创建
        """
        self.llm = llm or self._create_llm()

    def _create_llm(self):
        """创建 DeepSeek LLM 实例"""
        api_key = LLM_CONFIG.api_key

        if not api_key or api_key == '':
            raise ValueError(
                "未设置 DeepSeek API Key！\n"
                "请设置环境变量: export DEEPSEEK_API_KEY=your-key\n"
                "获取 API Key: https://platform.deepseek.com/"
            )

        print(f"正在初始化 DeepSeek LLM...")
        print(f"  - 模型: {LLM_CONFIG.model_name}")
        print(f"  - Base URL: {LLM_CONFIG.base_url}")

        llm = ChatOpenAI(
            model=LLM_CONFIG.model_name,
            api_key=api_key,
            base_url=LLM_CONFIG.base_url,
            temperature=LLM_CONFIG.temperature,
            max_tokens=LLM_CONFIG.max_tokens
        )

        print("[OK] DeepSeek LLM 初始化完成")
        return llm

    def get_llm(self):
        """
        获取 LLM 实例

        Returns:
            LLM 实例
        """
        return self.llm

    def invoke(self, messages, **kwargs):
        """
        直接调用 LLM

        Args:
            messages: 消息列表或字符串
            **kwargs: 额外参数

        Returns:
            LLM 响应
        """
        return self.llm.invoke(messages, **kwargs)


def create_llm_service(llm=None) -> LLMService:
    """
    便捷函数：创建 LLM 服务

    Args:
        llm: LLM 实例（可选）

    Returns:
        LLMService 实例
    """
    return LLMService(llm=llm)