import os
import json

from rest_framework.views import APIView
from rest_framework.response import Response

from services.document_service import document_service
from services.vector_store_service import vector_store_manager
from services.rag_service import rag_service


class KnowledgeStatusView(APIView):
    """知识库状态"""

    def get(self, request):
        vs_status = vector_store_manager.get_status()
        docs = document_service.get_uploaded_list()
        return Response({
            'vector_store': vs_status,
            'documents': docs,
            'document_count': len(docs),
        })


class DocumentUploadView(APIView):
    """文档上传"""

    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': '请选择文件'}, status=400)

        results = []
        all_documents = []

        for f in files:
            filename = f.name
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.pdf', '.txt', '.docx', '.doc', '.md', '.csv', '.json']:
                results.append({'filename': filename, 'status': 'error', 'message': f'不支持的文件格式: {ext}'})
                continue

            save_path = os.path.join(document_service.upload_dir, filename)
            os.makedirs(document_service.upload_dir, exist_ok=True)

            with open(save_path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            if document_service.is_file_uploaded(save_path):
                os.remove(save_path)
                results.append({'filename': filename, 'status': 'skipped', 'message': '文件已存在'})
                continue

            try:
                docs = document_service.load_document(save_path)
                cleaned = document_service.clean_and_split(docs)
                all_documents.extend(cleaned)
                document_service.mark_uploaded(save_path, filename)

                file_size = os.path.getsize(save_path)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'message': f'已加载 {len(cleaned)} 个文档块',
                    'chunk_count': len(cleaned),
                    'file_size': file_size,
                    'file_type': ext,
                })
            except Exception as e:
                results.append({'filename': filename, 'status': 'error', 'message': str(e)})

        vector_count = 0
        if all_documents:
            try:
                if vector_store_manager.is_loaded():
                    vector_store_manager.add_documents(all_documents)
                else:
                    vector_store_manager.create_from_documents(all_documents)
                vector_store_manager.save_local()
                rag_service._vector_store_service = vector_store_manager.service
                vector_count = vector_store_manager.service.vector_store.index.ntotal
            except Exception as e:
                return Response({'results': results, 'error': f'向量库更新失败: {str(e)}'}, status=500)

        return Response({
            'results': results,
            'added_chunks': len(all_documents),
            'total_vectors': vector_count,
        })


class DocumentListView(APIView):
    """文档列表"""

    def get(self, request):
        docs = document_service.get_uploaded_list()
        return Response({'documents': docs, 'count': len(docs)})


class DocumentDeleteView(APIView):
    """删除文档"""

    def delete(self, request, md5):
        uploaded = document_service.get_uploaded_list()
        target = None
        for doc in uploaded:
            if doc.get('md5') == md5:
                target = doc
                break

        if not target:
            return Response({'error': '文档不存在'}, status=404)

        file_path = target['file_path']
        if not os.path.isabs(file_path):
            from services.vector_store_service import PROJECT_ROOT
            file_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        document_service.remove_by_md5(md5)
        return Response({'message': f'已删除: {target["filename"]}'})


class SearchTestView(APIView):
    """测试检索"""

    def post(self, request):
        query = request.data.get('query', '')
        k = request.data.get('k', 5)

        if not query:
            return Response({'error': '请输入查询内容'}, status=400)

        try:
            docs = rag_service.search_similar(query, k=k)
        except Exception as e:
            return Response({'error': f'检索失败: {str(e)}'}, status=500)

        results = []
        for i, doc in enumerate(docs):
            results.append({
                'index': i + 1,
                'content': doc.page_content[:500],
                'source': doc.metadata.get('source', '未知来源'),
            })

        return Response({'query': query, 'results': results, 'count': len(results)})


class RebuildView(APIView):
    """重建知识库"""

    def post(self, request):
        uploaded = document_service.get_uploaded_list()
        all_documents = []

        for item in uploaded:
            file_path = item['file_path']
            if not os.path.exists(file_path):
                continue
            try:
                docs = document_service.load_document(file_path)
                cleaned = document_service.clean_and_split(docs)
                all_documents.extend(cleaned)
            except Exception as e:
                return Response({'error': f'处理 {item["filename"]} 失败: {str(e)}'}, status=500)

        if not all_documents:
            return Response({'error': '没有可处理的文档'}, status=400)

        try:
            vector_store_manager.create_from_documents(all_documents)
            vector_store_manager.save_local()
            rag_service._vector_store_service = vector_store_manager.service
            rag_service._rag_chain = None

            vector_count = vector_store_manager.service.vector_store.index.ntotal
            return Response({
                'message': '知识库重建完成',
                'vector_count': vector_count,
                'document_count': len(uploaded),
            })
        except Exception as e:
            return Response({'error': f'重建失败: {str(e)}'}, status=500)
