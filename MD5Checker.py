"""
MD5 文件去重模块
用于检测和记录已上传的文件
"""

import os
import hashlib
import json
from datetime import datetime


class MD5Checker:
    """MD5 文件去重检查器"""

    def __init__(self, index_path: str = "vector_stores/md5_index.json"):
        """
        初始化 MD5 检查器

        Args:
            index_path: MD5 索引文件路径
        """
        self.index_path = index_path
        self.uploaded_files = self._load_index()

    def _load_index(self) -> dict:
        """加载 MD5 索引"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_index(self):
        """保存 MD5 索引"""
        index_dir = os.path.dirname(self.index_path)
        if index_dir and not os.path.exists(index_dir):
            os.makedirs(index_dir)

        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.uploaded_files, f, ensure_ascii=False, indent=2)

    @staticmethod
    def calculate_md5(file_path: str) -> str:
        """
        计算文件的 MD5 值

        Args:
            file_path: 文件路径

        Returns:
            MD5 哈希值
        """
        md5_hash = hashlib.md5()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)

        return md5_hash.hexdigest()

    def is_uploaded(self, file_path: str) -> bool:
        """
        检查文件是否已上传

        Args:
            file_path: 文件路径

        Returns:
            True 如果文件已上传，False 否则
        """
        file_md5 = self.calculate_md5(file_path)
        return file_md5 in self.uploaded_files

    def mark_as_uploaded(self, file_path: str, filename: str = None):
        """
        标记文件为已上传

        Args:
            file_path: 文件路径
            filename: 文件名（可选）
        """
        file_md5 = self.calculate_md5(file_path)

        if filename is None:
            filename = os.path.basename(file_path)

        self.uploaded_files[file_md5] = {
            'filename': filename,
            'file_path': file_path,
            'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'md5': file_md5
        }

        self._save_index()

    def remove_file(self, file_path: str) -> bool:
        """
        从索引中移除文件记录

        Args:
            file_path: 文件路径

        Returns:
            True 如果成功移除，False 如果文件不在索引中
        """
        file_md5 = self.calculate_md5(file_path)

        if file_md5 in self.uploaded_files:
            del self.uploaded_files[file_md5]
            self._save_index()
            return True
        return False

    def get_uploaded_list(self) -> list:
        """
        获取所有已上传文件列表

        Returns:
            已上传文件信息列表
        """
        return list(self.uploaded_files.values())