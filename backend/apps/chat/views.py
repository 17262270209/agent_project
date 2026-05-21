import json
import os
import uuid
import re
from datetime import datetime

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from services.rag_service import rag_service
from services.chat_history_service import chat_history_manager
from services.vector_store_service import vector_store_manager


QUICK_QUESTIONS = [
    {"id": 1, "text": "什么是RAG技术？"},
    {"id": 2, "text": "如何使用向量检索？"},
    {"id": 3, "text": "系统支持哪些文档格式？"},
    {"id": 4, "text": "如何管理知识库？"},
]


def _ensure_vector_store_loaded():
    """确保向量存储已加载"""
    # 复位已损坏的状态（service存在但vector_store为None）
    if rag_service._vector_store_service is not None and rag_service._vector_store_service.vector_store is None:
        rag_service._vector_store_service = None

    if not rag_service._vector_store_service:
        from services.vector_store_service import PROJECT_ROOT
        vs_base = os.path.join(PROJECT_ROOT, 'vector_stores')

        # faiss_index 优先（上传文档后保存的目标路径）
        priority = ['faiss_index']
        candidates = []

        if os.path.isdir(vs_base):
            for subdir in priority + sorted([d for d in os.listdir(vs_base) if d not in priority]):
                full_path = os.path.join(vs_base, subdir)
                if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, 'index.faiss')):
                    candidates.append(subdir)

        for subdir in candidates:
            rel_path = os.path.join('vector_stores', subdir)
            try:
                rag_service.init_vector_store(rel_path)
                break
            except Exception as e:
                import traceback
                traceback.print_exc()


class ChatSendView(APIView):
    """发送消息 - SSE 流式响应"""

    def _generate(self, query, session_id, k):
        _ensure_vector_store_loaded()
        result = rag_service.ask(query, session_id=session_id, k=k)

        answer = result.get('answer', '')
        context_docs = result.get('context_docs', [])

        sources = []
        for i, doc in enumerate(context_docs):
            sources.append({
                'index': i + 1,
                'source': doc.metadata.get('source', '未知来源'),
                'content': doc.page_content[:200],
            })

        # 将回答分句发送 (模拟流式效果)
        sentences = re.split(r'(?<=[。！？\n])', answer)
        buffer = ""
        for part in sentences:
            if not part:
                continue
            buffer += part
            yield f"data: {json.dumps({'content': part, 'done': False}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'content': '', 'done': True, 'sources': sources, 'session_id': session_id}, ensure_ascii=False)}\n\n"

    def post(self, request):
        query = request.data.get('query', '')
        session_id = request.data.get('session_id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        k = request.data.get('k', 5)

        if not query.strip():
            return Response({'error': '请输入问题'}, status=400)

        response = StreamingHttpResponse(
            self._generate(query, session_id, k),
            content_type='text/event-stream',
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class SessionListView(APIView):
    """会话列表"""

    def get(self, request):
        sessions = chat_history_manager.list_sessions()
        return Response({'sessions': sessions, 'count': len(sessions)})


class SessionDetailView(APIView):
    """会话详情 - 获取消息"""

    def get(self, request, session_id):
        try:
            messages = chat_history_manager.get_messages(session_id)
            return Response({'session_id': session_id, 'messages': messages})
        except Exception:
            return Response({'session_id': session_id, 'messages': []})

    def delete(self, request, session_id):
        try:
            chat_history_manager.delete_history(session_id)
            return Response({'message': '会话已删除'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ContinueSessionView(APIView):
    """切换/继续会话"""

    def post(self, request, session_id):
        try:
            messages = chat_history_manager.get_messages(session_id)
            if not messages:
                return Response({'error': '会话不存在或为空'}, status=404)
            return Response({
                'session_id': session_id,
                'messages': messages,
                'message': '已切换到该会话',
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class QuickQuestionsView(APIView):
    """快捷问题列表"""

    def get(self, request):
        return Response({'questions': QUICK_QUESTIONS})
