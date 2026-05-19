# Clean_Document.py
"""
文档清洗和分块模块

功能：
- 去除多余空行
- 清理乱码
- 去除页眉页脚
- 使用 RecursiveCharacterTextSplitter 进行文本分块
"""

import re
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.cleaning_config import (
    HEADER_FOOTER_PATTERNS,
    GARBLED_PATTERNS,
    TEXT_SEPARATORS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_REMOVE_EXTRA_BLANK_LINES,
    DEFAULT_REMOVE_GARBLED_TEXT,
    DEFAULT_REMOVE_HEADER_FOOTER
)


class DocumentCleaner:
    """文档清洗器"""
    
    def __init__(self, 
                 chunk_size: int = DEFAULT_CHUNK_SIZE,
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
                 remove_extra_blank_lines: bool = DEFAULT_REMOVE_EXTRA_BLANK_LINES,
                 remove_garbled_text: bool = DEFAULT_REMOVE_GARBLED_TEXT,
                 remove_header_footer: bool = DEFAULT_REMOVE_HEADER_FOOTER):
        """
        初始化文档清洗器
        
        Args:
            chunk_size: 文本块大小 (建议 500-1000)
            chunk_overlap: 文本块重叠大小 (建议 100-200)
            remove_extra_blank_lines: 是否去除多余空行
            remove_garbled_text: 是否清理乱码
            remove_header_footer: 是否去除页眉页脚
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.remove_extra_blank_lines = remove_extra_blank_lines
        self.remove_garbled_text = remove_garbled_text
        self.remove_header_footer = remove_header_footer
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=TEXT_SEPARATORS
        )
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return text
        
        if self.remove_extra_blank_lines:
            text = self._remove_extra_blank_lines(text)
        
        if self.remove_garbled_text:
            text = self._remove_garbled_text(text)
        
        if self.remove_header_footer:
            text = self._remove_header_footer(text)
        
        text = self._clean_spaces(text)
        
        return text
    
    def _remove_extra_blank_lines(self, text: str) -> str:
        """
        去除多余空行，最多保留一个空行
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    def _remove_garbled_text(self, text: str) -> str:
        """
        清理乱码字符
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        for pattern in GARBLED_PATTERNS:
            text = re.sub(pattern, '', text)
        
        return text
    
    def _remove_header_footer(self, text: str) -> str:
        """
        去除页眉页脚（基于常见模式）
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            is_header_footer = False
            for pattern in HEADER_FOOTER_PATTERNS:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_header_footer = True
                    break
            
            if not is_header_footer:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_spaces(self, text: str) -> str:
        """
        清理多余空格
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        text = re.sub(r'[ \t]+', ' ', text)
        
        lines = [line for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text
    
    def clean_and_split(self, documents: List[Document]) -> List[Document]:
        """
        清洗文档并分块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            清洗并分块后的文档列表
        """
        if not documents:
            return []
        
        print(f"开始清洗和分块 {len(documents)} 个文档...")
        
        cleaned_documents = []
        
        for i, doc in enumerate(documents):
            cleaned_text = self.clean_text(doc.page_content)
            
            if not cleaned_text.strip():
                print(f"  文档 {i+1}: 清洗后为空，跳过")
                continue
            
            cleaned_doc = Document(
                page_content=cleaned_text,
                metadata=doc.metadata.copy()
            )
            
            splits = self.text_splitter.split_documents([cleaned_doc])
            cleaned_documents.extend(splits)
            
            print(f"  文档 {i+1}: 清洗并分割为 {len(splits)} 个块")
        
        print(f"清洗完成！总共生成 {len(cleaned_documents)} 个文档块")
        
        return cleaned_documents
    
    def split_single_document(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """
        对单个文档进行清洗和分块
        
        Args:
            text: 原始文本
            metadata: 元数据
            
        Returns:
            分块后的文档列表
        """
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text.strip():
            return []
        
        doc = Document(
            page_content=cleaned_text,
            metadata=metadata or {}
        )
        
        splits = self.text_splitter.split_documents([doc])
        
        return splits


def clean_documents(documents: List[Document],
                   chunk_size: int = DEFAULT_CHUNK_SIZE,
                   chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Document]:
    """
    便捷函数：清洗并分块文档
    
    Args:
        documents: 原始文档列表
        chunk_size: 文本块大小 (500-1000)
        chunk_overlap: 文本块重叠大小 (100-200)
        
    Returns:
        清洗并分块后的文档列表
    """
    cleaner = DocumentCleaner(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return cleaner.clean_and_split(documents)


if __name__ == "__main__":
    from langchain_core.documents import Document
    
    sample_text = """
    这是第一部分内容。
    
    
    这里有很多空行。
    
    
    
    这是第二部分内容。
    
    第 1 页 / 共 10 页
    
    这是第三部分内容，包含一些乱码□□□和特殊字符。
    
    Page 2 of 10
    
    这是第四部分内容。
    
    版权所有 © 2024
    
    这是第五部分内容。
    """
    
    doc = Document(page_content=sample_text, metadata={"source": "test.txt"})
    
    cleaner = DocumentCleaner(
        chunk_size=100,
        chunk_overlap=20
    )
    
    print("原始文本:")
    print(sample_text)
    print("\n" + "="*60)
    
    cleaned_text = cleaner.clean_text(sample_text)
    print("\n清洗后的文本:")
    print(cleaned_text)
    print("\n" + "="*60)
    
    splits = cleaner.clean_and_split([doc])
    
    print(f"\n分块结果: {len(splits)} 个块")
    for i, split in enumerate(splits):
        print(f"\n--- 块 {i+1} ---")
        print(split.page_content)
        print(f"元数据: {split.metadata}")
