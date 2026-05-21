from django.db import models


class KnowledgeDocument(models.Model):
    md5_hash = models.CharField(max_length=64, unique=True, verbose_name='MD5哈希')
    filename = models.CharField(max_length=512, verbose_name='文件名')
    file_path = models.CharField(max_length=1024, verbose_name='文件路径')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=20, verbose_name='文件类型')
    chunk_count = models.IntegerField(default=0, verbose_name='文档块数量')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        db_table = 'knowledge_documents'
        verbose_name = '知识库文档'
        verbose_name_plural = '知识库文档'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.filename
