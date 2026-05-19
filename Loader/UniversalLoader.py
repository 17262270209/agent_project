from .PDFLoader import PDFDocumentLoader
from .TextLoader import TextDocumentLoader
from .WordLoader import WordDocumentLoader
from typing import List, Optional
import os
from config.loader_config import UNIVERSAL_LOADER_CONFIG


class UniversalDocumentLoader:
    """通用文档加载器 - 根据文件类型自动选择对应的加载器"""
    
    def __init__(self, file_path: str, chunk_size: int = None, 
                 chunk_overlap: int = None, encoding: Optional[str] = None):
        """
        初始化通用文档加载器
        
        Args:
            file_path: 文档文件路径
            chunk_size: 文本块大小（默认从配置读取）
            chunk_overlap: 文本块重叠大小（默认从配置读取）
            encoding: 文件编码（仅对文本文件有效）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        self.file_path = file_path
        self.chunk_size = chunk_size if chunk_size is not None else UNIVERSAL_LOADER_CONFIG['chunk_size']
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else UNIVERSAL_LOADER_CONFIG['chunk_overlap']
        self.encoding = encoding
        self.file_extension = os.path.splitext(file_path)[1].lower()
        
        if self.file_extension not in UNIVERSAL_LOADER_CONFIG['supported_extensions']:
            raise ValueError(f"不支持的文件格式: {self.file_extension}")
    
    def load_and_split(self) -> List:
        """
        根据文件类型自动加载并分割文档
        
        Returns:
            分割后的文档列表
        """
        file_type = UNIVERSAL_LOADER_CONFIG['supported_extensions'][self.file_extension]
        
        if file_type == 'pdf':
            loader = PDFDocumentLoader(
                self.file_path,
                self.chunk_size,
                self.chunk_overlap
            )
        elif file_type == 'word':
            loader = WordDocumentLoader(
                self.file_path,
                self.chunk_size,
                self.chunk_overlap
            )
        else:
            loader = TextDocumentLoader(
                self.file_path,
                self.encoding,
                self.chunk_size,
                self.chunk_overlap
            )
        
        return loader.load_and_split()
    
    def get_metadata(self) -> dict:
        """
        获取文档元数据
        
        Returns:
            文档元数据字典
        """
        file_type = UNIVERSAL_LOADER_CONFIG['supported_extensions'][self.file_extension]
        
        if file_type == 'pdf':
            loader = PDFDocumentLoader(self.file_path)
        elif file_type == 'word':
            loader = WordDocumentLoader(self.file_path)
        else:
            loader = TextDocumentLoader(self.file_path, self.encoding)
        
        return loader.get_metadata()
