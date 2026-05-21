"""
文档服务 - 封装文档加载、清洗、MD5 检查
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Clean_Document import clean_documents
from MD5Checker import MD5Checker
from Loader.UniversalLoader import UniversalDocumentLoader


class DocumentService:
    """文档处理服务"""

    def __init__(self, upload_dir: str = None, md5_index_path: str = None):
        self.upload_dir = upload_dir or os.path.join(PROJECT_ROOT, 'data', 'uploads')
        self.md5_index_path = md5_index_path or os.path.join(PROJECT_ROOT, 'vector_stores', 'md5_index.json')
        self.md5_checker = MD5Checker(self.md5_index_path)

    def load_document(self, file_path: str, chunk_size: int = 800, chunk_overlap: int = 150):
        """加载并分割文档"""
        loader = UniversalDocumentLoader(
            file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return loader.load_and_split()

    def clean_and_split(self, documents, chunk_size: int = 800, chunk_overlap: int = 150):
        """清洗并分块文档"""
        return clean_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def is_file_uploaded(self, file_path: str) -> bool:
        """检查文件MD5是否已存在"""
        return self.md5_checker.is_uploaded(file_path)

    def mark_uploaded(self, file_path: str, filename: str = None):
        """标记文件已上传"""
        self.md5_checker.mark_as_uploaded(file_path, filename)

    def remove_uploaded(self, file_path: str) -> bool:
        """移除文件上传记录"""
        return self.md5_checker.remove_file(file_path)

    def remove_by_md5(self, md5: str) -> bool:
        """通过MD5直接移除上传记录（文件已删除时使用）"""
        return self.md5_checker.remove_by_md5(md5)

    def get_uploaded_list(self) -> list:
        """获取已上传文件列表"""
        return self.md5_checker.get_uploaded_list()

    def get_md5(self, file_path: str) -> str:
        """计算文件MD5"""
        return MD5Checker.calculate_md5(file_path)


document_service = DocumentService()
