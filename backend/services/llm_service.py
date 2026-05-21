"""
LLM 服务 - 封装 LLM 调用
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LLMService import LLMService as _LLMService
from config.vector_store_config import LLM_CONFIG


class LLMManager:
    """LLM 管理器"""

    def __init__(self):
        self._service = None

    @property
    def service(self):
        if self._service is None:
            self._service = _LLMService()
        return self._service

    def get_config(self) -> dict:
        return {
            'model_name': LLM_CONFIG.model_name,
            'base_url': LLM_CONFIG.base_url,
            'temperature': LLM_CONFIG.temperature,
            'max_tokens': LLM_CONFIG.max_tokens,
            'api_key': self._mask_key(LLM_CONFIG.api_key),
        }

    def update_config(self, data: dict) -> dict:
        for key in ['model_name', 'base_url', 'temperature', 'max_tokens']:
            if key in data:
                setattr(LLM_CONFIG, key, data[key])
        if 'api_key' in data and data['api_key'] and not data['api_key'].startswith('***'):
            LLM_CONFIG.api_key = data['api_key']
            os.environ['DEEPSEEK_API_KEY'] = data['api_key']
        self._service = None
        return self.get_config()

    @staticmethod
    def _mask_key(key: str) -> str:
        if not key or len(key) < 8:
            return '***'
        return key[:4] + '***' + key[-4:]


llm_manager = LLMManager()
