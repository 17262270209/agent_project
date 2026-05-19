# RAGRetriever.py
"""
RAG 检索器服务 - 整合向量库检索和 LLM 生成
"""
import os
from typing import List
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config.vector_store_config import LLM_CONFIG, FAISS_CONFIG
from utils.formatters import format_context


class RAGRetriever(object):
    """RAG 检索器"""

    def __init__(self, vector_store_service=None, llm=None):
        self.vector_store_service = vector_store_service
        
        if llm is not None:
            self.llm = llm
        else:
            self.llm = self._create_llm()
    
    def _create_llm(self):
        """创建 DeepSeek LLM 实例"""
        api_key = LLM_CONFIG.api_key
        
        if not api_key or api_key.strip() == '':
            raise ValueError(
                "未设置 DeepSeek API Key！\n"
                "请设置环境变量: export DEEPSEEK_API_KEY=your-key\n"
                "获取 API Key: https://platform.deepseek.com/"
            )
        
        return ChatOpenAI(
            model=LLM_CONFIG.model_name,
            api_key=api_key,
            base_url=LLM_CONFIG.base_url,
            temperature=LLM_CONFIG.temperature,
            max_tokens=LLM_CONFIG.max_tokens
        )

    def set_vector_store(self, vector_store_service):
        """设置向量库服务"""
        self.vector_store_service = vector_store_service

    def search_documents(self, query: str, k: int = None) -> List[Document]:
        """搜索相关文档"""
        return self.vector_store_service.search_similar(query, k=k)

    def generate_answer(self, query: str, context_docs: List[Document] = None) -> str:
        """基于上下文生成答案"""
        # 如果没有提供上下文，自动检索
        if context_docs is None:
            context_docs = self.search_documents(query)
        
        # 使用工具函数构建上下文文本
        context_text = format_context(context_docs)
        
        # 构建增强的提示词
        template = """
你是一个专业的智能问答助手，擅长根据提供的参考文档回答问题。

## 核心指令：
1. **必须基于文档内容回答**：你的回答必须严格基于提供的上下文文档，不得编造信息。
2. **标注信息来源**：在回答中引用文档内容时，请标注来源（如：[文档1]）。
3. **处理冲突信息**：如果多个文档内容冲突，请指出差异并提供所有观点。
4. **承认知识边界**：如果文档中没有相关信息，请明确告知"根据现有文档无法回答该问题"。

## 格式要求：
- 回答应结构化，使用清晰的语言
- 复杂问题可分点说明
- 保持回答简洁准确

## 参考文档：
{context}

## 用户问题：
{question}

## 回答："""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # 构建 RAG 链并生成答案
        rag_chain = prompt | self.llm | StrOutputParser()
        return rag_chain.invoke({
            "context": context_text,
            "question": query
        })

    def ask(self, query: str, k: int = None) -> dict:
        """完整的 RAG 问答流程"""
        # 检索相关文档
        context_docs = self.search_documents(query, k=k)

        # 生成答案
        answer = self.generate_answer(query, context_docs)

        return {
            "question": query,
            "answer": answer,
            "context_docs": context_docs
        }


def create_rag_retriever(vector_store_service, llm=None) -> RAGRetriever:
    """便捷函数：创建 RAG 检索器"""
    retriever = RAGRetriever(llm=llm)
    retriever.set_vector_store(vector_store_service)
    return retriever


if __name__ == "__main__":
    # 测试代码
    from VectorStoreBuilder import VectorStoreService
    from Loader.UniversalLoader import UniversalDocumentLoader
    from Clean_Document import DocumentCleaner

    print("=" * 80)
    print("测试：RAG 检索器（FAISS + DeepSeek）")
    print("=" * 80)

    # 步骤1：检查是否有已保存的向量库
    index_path = FAISS_CONFIG.index_path

    if os.path.exists(index_path):
        print("\n【步骤1】加载已有的向量库...")
        service = VectorStoreService()
        service.load_local(index_path=index_path)
    else:
        print("\n【步骤1】构建新的向量库...")

        # 加载文档
        pdf_path = "data/基于 MobileNetV2的玉米叶片状态检测及病害解决系统的设计与实现_AIGC原文对照报告.pdf"

        if os.path.exists(pdf_path):
            loader = UniversalDocumentLoader(file_path=pdf_path)
            raw_documents = loader.load_and_split()

            # 清洗文档
            cleaner = DocumentCleaner(chunk_size=800, chunk_overlap=150)
            cleaned_documents = cleaner.clean_and_split(raw_documents)

            # 构建向量库
            service = VectorStoreService()
            service.create_from_documents(cleaned_documents)
            service.save_local()
        else:
            print("PDF 文件不存在，使用示例文档")
            sample_texts = [
                "Python 是一种广泛使用的编程语言，适合人工智能开发。",
                "机器学习是人工智能的一个重要分支，包括监督学习、无监督学习和强化学习。",
                "深度学习使用多层神经网络进行模式识别和特征提取。",
                "自然语言处理让计算机能够理解和生成人类语言。",
                "计算机视觉使计算机能够理解和分析图像和视频内容。"
            ]

            cleaned_documents = [
                Document(page_content=text, metadata={"source": f"sample_{i}.txt"})
                for i, text in enumerate(sample_texts)
            ]

            service = VectorStoreService()
            service.create_from_documents(cleaned_documents)

    # 步骤2：创建 RAG 检索器
    print("\n【步骤2】创建 RAG 检索器...")
    rag = create_rag_retriever(service)

    # 步骤3：测试检索
    print("\n【步骤3】测试 RAG 问答...")
    
    test_questions = [
        "什么是机器学习？",
        "Python 有什么特点？",
        "深度学习的应用有哪些？"
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"问题: {question}")
        print('='*60)

        try:
            result = rag.ask(question, k=3)

            print(f"\n回答:")
            print(result['answer'])

            print(f"\n参考文档 ({len(result['context_docs'])} 个):")
            for i, doc in enumerate(result['context_docs'], 1):
                print(f"\n  [{i}] {doc.page_content[:100]}...")
                print(f"      来源: {doc.metadata.get('source', 'N/A')}")

        except Exception as e:
            print(f"✗ 问答失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✓ RAG 检索器测试完成!")
    print("=" * 80)