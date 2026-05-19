# RAGChain.py
"""
RAG 问答链 - 整合向量检索、LLM 生成和会话记忆
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from VectorStoreBuilder import VectorStoreService
from LLMService import LLMService
from ChatHistoryService import FileChatMessageHistory
from utils.formatters import format_context


class RAGChain(object):
    """RAG 问答链（支持会话记忆）"""
    
    def __init__(self, 
                 vector_store_service: VectorStoreService, 
                 llm_service: LLMService = None,
                 session_id: str = "default",
                 storage_path: str = "./chat_history"):
        self.vector_store_service = vector_store_service
        self.llm_service = llm_service or LLMService()
        self.llm = self.llm_service.get_llm()
        
        # 会话记忆
        self.session_id = session_id
        self.chat_history = FileChatMessageHistory(session_id, storage_path)
        
        # 构建 RAG 链
        self.rag_chain = self._build_rag_chain()
    
    def _build_prompt(self) -> ChatPromptTemplate:
        """构建增强的 RAG 提示词模板"""
        template = """
你是一个专业的智能问答助手。

## 核心指令：
1. **优先使用参考文档**：如果提供的参考文档中有相关信息，请基于文档内容回答，并标注来源（如：[文档1]）。
2. **没有文档时**：如果参考文档为空或没有相关信息，你可以基于自身知识回答，但必须在回答开头明确标注：「⚠️ 当前知识库中未找到相关数据，以下回答基于模型自身知识：」
3. **标注信息来源**：引用文档内容时，请标注来源（如：[文档1]）。
4. **处理冲突信息**：如果多个文档内容冲突，请指出差异并提供所有观点。

## 格式要求：
- 回答应结构化，使用清晰的语言
- 复杂问题可分点说明
- 保持回答简洁准确

## 参考文档：
{context}

## 用户问题：
{question}

## 回答：
"""
        
        return ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
    
    def _build_rag_chain(self):
        """构建 RAG 链"""
        prompt = self._build_prompt()
        return prompt | self.llm | StrOutputParser()
    
    def ask(self, query: str, k: int = 5) -> dict:
        """完整的 RAG 问答流程"""
        # 检索相关文档
        context_docs = self.vector_store_service.search_similar(query, k=k)
        
        # 构建上下文文本（使用工具函数）
        context_text = format_context(context_docs)
        
        # 获取会话历史
        chat_history = self.chat_history.messages
        
        # 生成答案
        answer = self.rag_chain.invoke({
            "context": context_text,
            "chat_history": chat_history,
            "question": query
        })
        
        # 保存对话历史
        self.chat_history.add_messages([
            HumanMessage(content=query),
            AIMessage(content=answer)
        ])
        
        return {
            "question": query,
            "answer": answer,
            "context_docs": context_docs,
            "session_id": self.session_id
        }
    
    def invoke(self, query: str) -> str:
        """简化的问答接口，直接返回答案字符串"""
        result = self.ask(query)
        return result['answer']
    
    def clear_history(self) -> None:
        """清空会话历史"""
        self.chat_history.clear()


def create_rag_chain(vector_store_service: VectorStoreService, 
                    llm_service: LLMService = None,
                    session_id: str = "default",
                    storage_path: str = "./chat_history") -> RAGChain:
    """便捷函数：创建 RAG 问答链"""
    return RAGChain(
        vector_store_service, 
        llm_service, 
        session_id=session_id,
        storage_path=storage_path
    )