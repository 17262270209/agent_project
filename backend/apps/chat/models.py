from django.db import models


class ChatSession(models.Model):
    session_id = models.CharField(max_length=128, unique=True, verbose_name='会话ID')
    title = models.CharField(max_length=256, default='新对话', verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    message_count = models.IntegerField(default=0, verbose_name='消息数量')

    class Meta:
        db_table = 'chat_sessions'
        verbose_name = '会话'
        verbose_name_plural = '会话'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} ({self.session_id})'


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('human', '用户'),
        ('ai', 'AI助手'),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='所属会话'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='角色')
    content = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_messages'
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
