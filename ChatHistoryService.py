# ChatHistoryService.py
"""
会话记忆服务 - 支持内存缓存和持久化存储
"""

import os
import json
from typing import Sequence, List
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory


class FileChatMessageHistory(BaseChatMessageHistory):
    """基于文件的会话记忆存储（带内存缓存）"""

    def __init__(self, session_id: str, storage_path: str = "./chat_history"):
        """
        初始化会话记忆

        Args:
            session_id: 会话 ID
            storage_path: 存储路径
        """
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path, self.session_id)
        self._messages_cache = None  # 内存缓存

        # 确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """
        添加消息到历史记录

        Args:
            messages: 消息序列
        """
        all_messages = list(self.messages)
        all_messages.extend(messages)

        # 转换为字典并保存
        new_messages = [message_to_dict(message) for message in all_messages]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)
        
        # 更新缓存
        self._messages_cache = all_messages

    @property
    def messages(self) -> List[BaseMessage]:
        """获取历史消息列表（带缓存）"""
        # 如果缓存存在，直接返回
        if self._messages_cache is not None:
            return self._messages_cache
        
        # 否则从文件读取
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                self._messages_cache = messages_from_dict(messages_data)
                return self._messages_cache
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        """清空会话历史"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        # 清空缓存
        self._messages_cache = []

    def delete(self) -> None:
        """删除会话文件"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            self._messages_cache = None

    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)

    def get_recent_messages(self, limit: int = 10) -> List[BaseMessage]:
        """获取最近的消息"""
        all_messages = self.messages
        return all_messages[-limit:] if limit > 0 else all_messages


def get_chat_history(session_id: str, storage_path: str = "./chat_history") -> FileChatMessageHistory:
    """
    便捷函数：获取会话历史

    Args:
        session_id: 会话 ID
        storage_path: 存储路径

    Returns:
        FileChatMessageHistory 实例
    """
    return FileChatMessageHistory(session_id, storage_path)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("测试：会话记忆服务（带缓存）")
    print("=" * 60)

    # 创建会话历史
    history = get_chat_history("test_user_001")

    # 添加消息
    history.add_messages([
        HumanMessage(content="你好"),
        AIMessage(content="你好！有什么可以帮助你的吗？"),
        HumanMessage(content="今天天气怎么样？"),
        AIMessage(content="抱歉，我无法提供实时天气信息。")
    ])

    # 读取消息（测试缓存）
    print("\n历史消息:")
    for msg in history.messages:
        print(f"  {type(msg).__name__}: {msg.content}")
    
    print(f"\n消息总数: {history.get_message_count()}")
    
    # 测试最近消息
    print("\n最近 2 条消息:")
    for msg in history.get_recent_messages(2):
        print(f"  {type(msg).__name__}: {msg.content}")

    # 测试清空
    history.clear()
    print(f"\n清空后消息数: {history.get_message_count()}")

    print("\n✓ 测试完成!")