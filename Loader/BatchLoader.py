from .UniversalLoader import UniversalDocumentLoader
from typing import List, Dict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.loader_config import BATCH_LOADER_CONFIG


class BatchDocumentLoader:
    """批量文档加载器"""
    
    def __init__(self, directory_path: str, chunk_size: int = None, 
                 chunk_overlap: int = None, max_workers: int = None):
        """
        初始化批量文档加载器
        
        Args:
            directory_path: 包含文档的目录路径
            chunk_size: 文本块大小（默认从配置读取）
            chunk_overlap: 文本块重叠大小（默认从配置读取）
            max_workers: 最大并行工作线程数（默认从配置读取）
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"路径不是目录: {directory_path}")
        
        self.directory_path = directory_path
        self.chunk_size = chunk_size if chunk_size is not None else BATCH_LOADER_CONFIG['chunk_size']
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else BATCH_LOADER_CONFIG['chunk_overlap']
        self.max_workers = max_workers if max_workers is not None else BATCH_LOADER_CONFIG['max_workers']
    
    def _get_supported_files(self) -> List[str]:
        """
        获取目录下所有支持的文件
        
        Returns:
            支持的文件路径列表
        """
        files = []
        
        for root, dirs, filenames in os.walk(self.directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                extension = os.path.splitext(filename)[1].lower()
                
                if extension in BATCH_LOADER_CONFIG['supported_extensions']:
                    files.append(file_path)
        
        return files
    
    def load_all_documents(self) -> List:
        """
        加载目录下所有支持的文档
        
        Returns:
            所有分割后的文档列表
        """
        files = self._get_supported_files()
        
        if not files:
            print(f"在目录 {self.directory_path} 中未找到支持的文档文件")
            return []
        
        print(f"找到 {len(files)} 个文档文件")
        
        all_splits = []
        failed_files = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {}
            
            for file_path in files:
                future = executor.submit(
                    self._load_single_document,
                    file_path
                )
                future_to_file[future] = file_path
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    splits = future.result()
                    if splits:
                        all_splits.extend(splits)
                except Exception as e:
                    print(f"加载文件 {file_path} 失败: {str(e)}")
                    failed_files.append(file_path)
        
        print(f"成功加载 {len(files) - len(failed_files)}/{len(files)} 个文件")
        print(f"总共生成 {len(all_splits)} 个文档块")
        
        if failed_files:
            print(f"失败的文件: {failed_files}")
        
        return all_splits
    
    def _load_single_document(self, file_path: str) -> List:
        """
        加载单个文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            分割后的文档列表
        """
        try:
            loader = UniversalDocumentLoader(
                file_path,
                self.chunk_size,
                self.chunk_overlap
            )
            return loader.load_and_split()
        except Exception as e:
            raise Exception(f"加载文件 {file_path} 时出错: {str(e)}")
    
    def get_directory_stats(self) -> Dict:
        """
        获取目录统计信息
        
        Returns:
            统计信息字典
        """
        files = self._get_supported_files()
        
        stats = {
            'total_files': len(files),
            'file_types': {},
            'total_size': 0
        }
        
        for file_path in files:
            extension = os.path.splitext(file_path)[1].lower()
            if extension not in stats['file_types']:
                stats['file_types'][extension] = 0
            stats['file_types'][extension] += 1
            stats['total_size'] += os.path.getsize(file_path)
        
        return stats
