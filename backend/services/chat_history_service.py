"""
聊天历史服务 - 封装会话历史管理
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ChatHistoryService import FileChatMessageHistory, get_chat_history


class ChatHistoryManager:
    """会话历史管理器"""

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(PROJECT_ROOT, 'chat_history')

    def get_history(self, session_id: str):
        return get_chat_history(session_id, self.storage_path)

    def delete_history(self, session_id: str):
        history = self.get_history(session_id)
        history.delete()

    def clear_history(self, session_id: str):
        history = self.get_history(session_id)
        history.clear()

    def list_sessions(self) -> list:
        """列出所有会话及其摘要"""
        sessions = []
        if not os.path.exists(self.storage_path):
            return sessions

        for filename in sorted(os.listdir(self.storage_path), reverse=True):
            filepath = os.path.join(self.storage_path, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                stat = os.stat(filepath)
                history = get_chat_history(filename, self.storage_path)
                message_count = history.get_message_count()
                title = '新对话'
                if message_count > 0:
                    first_msg = history.messages[0]
                    title = first_msg.content[:30] + ('...' if len(first_msg.content) > 30 else '')
                sessions.append({
                    'session_id': filename,
                    'title': title,
                    'message_count': message_count,
                    'created_at': stat.st_ctime,
                    'updated_at': stat.st_mtime,
                })
            except Exception:
                continue
        # 按更新时间降序排列
        sessions.sort(key=lambda s: s.get('updated_at', 0), reverse=True)
        return sessions

    def get_messages(self, session_id: str) -> list:
        """获取会话消息"""
        history = self.get_history(session_id)
        messages = []
        for msg in history.messages:
            messages.append({
                'role': 'human' if msg.__class__.__name__ == 'HumanMessage' else 'ai',
                'content': msg.content,
            })
        return messages


chat_history_manager = ChatHistoryManager()
