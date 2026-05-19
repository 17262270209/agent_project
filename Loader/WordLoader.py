from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
from config.loader_config import WORD_LOADER_CONFIG


class WordDocumentLoader:
    """Word文档加载器"""
    
    def __init__(self, file_path: str, chunk_size: int = None, chunk_overlap: int = None):
        """
        初始化Word文档加载器
        
        Args:
            file_path: Word文件路径 (.docx)
            chunk_size: 文本块大小（默认从配置读取）
            chunk_overlap: 文本块重叠大小（默认从配置读取）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not file_path.lower().endswith(tuple(WORD_LOADER_CONFIG['supported_extensions'])):
            raise ValueError(f"仅支持{WORD_LOADER_CONFIG['supported_extensions']}格式的Word文档")
        
        self.file_path = file_path
        self.chunk_size = chunk_size if chunk_size is not None else WORD_LOADER_CONFIG['chunk_size']
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else WORD_LOADER_CONFIG['chunk_overlap']
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=WORD_LOADER_CONFIG['separators']
        )
    
    def load_and_split(self) -> List:
        """
        加载Word文档并分割成小块
        
        Returns:
            分割后的文档列表
        """
        try:
            loader = Docx2txtLoader(self.file_path)
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)
            
            print(f"成功加载Word文档: {self.file_path}")
            print(f"分割后文档块数: {len(splits)}")
            
            return splits
            
        except Exception as e:
            raise Exception(f"加载Word文档时出错: {str(e)}")
    
    def get_metadata(self) -> dict:
        """
        获取Word文档元数据
        
        Returns:
            文档元数据字典
        """
        metadata = {
            'source': self.file_path,
            'file_name': os.path.basename(self.file_path),
            'file_size': os.path.getsize(self.file_path),
            'file_type': 'docx'
        }
        
        return metadata
