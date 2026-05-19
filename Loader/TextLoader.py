from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional
import os
import chardet
from config.loader_config import TEXT_LOADER_CONFIG


class TextDocumentLoader:
    """文本文档加载器"""
    
    def __init__(self, file_path: str, encoding: Optional[str] = None, 
                 chunk_size: int = None, chunk_overlap: int = None):
        """
        初始化文本文档加载器
        
        Args:
            file_path: 文本文件路径
            encoding: 文件编码，如果为None则自动检测
            chunk_size: 文本块大小（默认从配置读取）
            chunk_overlap: 文本块重叠大小（默认从配置读取）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        self.file_path = file_path
        self.chunk_size = chunk_size if chunk_size is not None else TEXT_LOADER_CONFIG['chunk_size']
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else TEXT_LOADER_CONFIG['chunk_overlap']
        
        if encoding is None:
            encoding = self._detect_encoding(file_path)
        
        self.encoding = encoding
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=TEXT_LOADER_CONFIG['separators']
        )
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码
        """
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding'] or TEXT_LOADER_CONFIG['default_encoding']
    
    def load_and_split(self) -> List:
        """
        加载文本文档并分割成小块
        
        Returns:
            分割后的文档列表
        """
        try:
            loader = TextLoader(self.file_path, encoding=self.encoding)
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)
            
            print(f"成功加载文本文件: {self.file_path}")
            print(f"编码: {self.encoding}")
            print(f"分割后文档块数: {len(splits)}")
            
            return splits
            
        except Exception as e:
            raise Exception(f"加载文本文档时出错: {str(e)}")
    
    def get_metadata(self) -> dict:
        """
        获取文本文档元数据
        
        Returns:
            文档元数据字典
        """
        metadata = {
            'source': self.file_path,
            'encoding': self.encoding,
            'file_name': os.path.basename(self.file_path),
            'file_size': os.path.getsize(self.file_path)
        }
        
        return metadata
