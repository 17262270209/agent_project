import os
import platform

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from services.vector_store_service import vector_store_manager
from services.llm_service import llm_manager
from services.chat_history_service import chat_history_manager
from services.document_service import document_service
from config.vector_store_config import RETRIEVAL_CONFIG


class StatisticsView(APIView):
    """系统统计"""

    def get(self, request):
        sessions = chat_history_manager.list_sessions()
        total_messages = sum(s.get('message_count', 0) for s in sessions)
        docs = document_service.get_uploaded_list()

        human_count = 0
        ai_count = 0
        for s in sessions:
            messages = chat_history_manager.get_messages(s['session_id'])
            for m in messages:
                if m['role'] == 'human':
                    human_count += 1
                else:
                    ai_count += 1

        return Response({
            'sessions_count': len(sessions),
            'total_messages': total_messages,
            'human_messages': human_count,
            'ai_messages': ai_count,
            'documents_count': len(docs),
            'vector_store': vector_store_manager.get_status(),
        })


class SystemConfigView(APIView):
    """系统配置"""

    def get(self, request):
        return Response({
            'llm': llm_manager.get_config(),
            'retrieval': {
                'default_k': RETRIEVAL_CONFIG.default_k,
                'score_threshold': RETRIEVAL_CONFIG.score_threshold,
            },
            'system': {
                'vector_stores_dir': settings.VECTOR_STORES_DIR,
                'data_dir': settings.DATA_DIR,
                'chat_history_dir': settings.CHAT_HISTORY_DIR,
            },
        })

    def put(self, request):
        if 'llm' in request.data:
            llm_manager.update_config(request.data['llm'])
        if 'retrieval' in request.data:
            r = request.data['retrieval']
            if 'default_k' in r:
                RETRIEVAL_CONFIG.default_k = int(r['default_k'])
            if 'score_threshold' in r:
                RETRIEVAL_CONFIG.score_threshold = float(r['score_threshold'])

        return Response({
            'llm': llm_manager.get_config(),
            'retrieval': {
                'default_k': RETRIEVAL_CONFIG.default_k,
                'score_threshold': RETRIEVAL_CONFIG.score_threshold,
            },
        })


class LogsView(APIView):
    """系统日志"""

    def get(self, request):
        return Response({
            'system_info': {
                'python': platform.python_version(),
                'platform': platform.platform(),
                'django_version': '4.2',
                'langchain': '0.1+',
                'faiss': '1.7+',
                'embedding_model': settings.EMBEDDING_MODEL,
                'llm_model': settings.DEEPSEEK_MODEL,
            },
            'status': {
                'vector_store_loaded': vector_store_manager.is_loaded(),
                'vector_count': vector_store_manager.get_status().get('vector_count', 0),
            },
        })
