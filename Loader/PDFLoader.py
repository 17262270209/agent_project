from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional
import os
from config.loader_config import PDF_LOADER_CONFIG
class PDFDocumentLoader:
    """PDF文档加载器"""
    
    def __init__(self, file_path: str, chunk_size: int = None, chunk_overlap: int = None):
        """
        初始化PDF文档加载器
        
        Args:
            file_path: PDF文件路径
            chunk_size: 文本块大小（默认从配置读取）
            chunk_overlap: 文本块重叠大小（默认从配置读取）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        self.file_path = file_path
        self.chunk_size = chunk_size if chunk_size is not None else PDF_LOADER_CONFIG['chunk_size']
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else PDF_LOADER_CONFIG['chunk_overlap']
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=PDF_LOADER_CONFIG['separators']
        )
    
    def load_and_split(self) -> List:
        """
        加载PDF文档并分割成小块
        
        Returns:
            分割后的文档列表
        """
        try:
            loader = PyPDFLoader(self.file_path)
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)
            
            print(f"成功加载PDF: {self.file_path}")
            print(f"原始文档页数: {len(documents)}")
            print(f"分割后文档块数: {len(splits)}")
            
            return splits
            
        except Exception as e:
            raise Exception(f"加载PDF文档时出错: {str(e)}")
    
    def get_metadata(self) -> dict:
        """
        获取PDF文档元数据
        
        Returns:
            文档元数据字典
        """
        try:
            loader = PyPDFLoader(self.file_path)
            documents = loader.load()
            
            metadata = {
                'source': self.file_path,
                'total_pages': len(documents),
                'file_name': os.path.basename(self.file_path)
            }
            
            return metadata
            
        except Exception as e:
            raise Exception(f"获取PDF元数据时出错: {str(e)}")
