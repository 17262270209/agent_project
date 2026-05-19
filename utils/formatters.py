"""
工具函数模块 - 提供通用的格式化和处理工具
"""

from typing import List
from langchain_core.documents import Document


def format_context(documents: List[Document]) -> str:
    """
    格式化上下文文档
    
    Args:
        documents: 文档列表
        
    Returns:
        格式化后的上下文文本
    """
    if not documents:
        return "未有参考资料"
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get('source', '未知来源')
        content = doc.page_content.strip()
        context_parts.append(f"[文档{i}] (来源: {source})\n{content}")
    
    return "\n\n".join(context_parts)


def format_documents_for_display(documents: List[Document], max_length: int = 200) -> str:
    """
    格式化文档用于显示（截断过长内容）
    
    Args:
        documents: 文档列表
        max_length: 最大显示长度
        
    Returns:
        格式化后的显示文本
    """
    if not documents:
        return "无相关文档"
    
    parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get('source', '未知来源')
        content = doc.page_content.strip()
        if len(content) > max_length:
            content = content[:max_length] + "..."
        parts.append(f"📄 文档{i}: {source}\n{content}")
    
    return "\n\n".join(parts)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix
