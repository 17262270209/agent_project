import os
from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.knowledge'
    verbose_name = '知识库管理'

    def ready(self):
        """Django 启动时自动加载向量存储"""
        from django.conf import settings

        def _autoload():
            from services.vector_store_service import PROJECT_ROOT, vector_store_manager
            from services.rag_service import rag_service

            vs_base = os.path.join(PROJECT_ROOT, 'vector_stores')

            # 优先加载 faiss_index（上传文档后保存的目标路径）
            priority = ['faiss_index']
            other_dirs = []

            if os.path.isdir(vs_base):
                for subdir in sorted(os.listdir(vs_base)):
                    if subdir in priority:
                        continue
                    full_path = os.path.join(vs_base, subdir)
                    if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, 'index.faiss')):
                        other_dirs.append(subdir)

            # faiss_index 优先，其余按向量数降序
            candidates = []
            for subdir in priority + other_dirs:
                full_path = os.path.join(vs_base, subdir)
                if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, 'index.faiss')):
                    candidates.append(subdir)

            for subdir in candidates:
                rel_path = os.path.join('vector_stores', subdir)
                try:
                    vector_store_manager.load_local(rel_path)
                    rag_service._vector_store_service = vector_store_manager.service
                    n = vector_store_manager.service.vector_store.index.ntotal
                    print(f'[启动] 知识库已加载: {subdir}, 向量数: {n}')
                    return
                except Exception as e:
                    print(f'[启动] 加载 {subdir} 失败: {e}')

            print('[启动] 未找到向量库，首次上传文档后将自动构建')

        _autoload()
