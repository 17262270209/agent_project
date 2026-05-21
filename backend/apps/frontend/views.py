import os
from django.conf import settings
from django.http import HttpResponse


def index(request, path=''):
    """返回前端 index.html (不经过 Django 模板引擎, 避免与 Vue {{ }} 冲突)"""
    file_path = os.path.join(settings.FRONTEND_DIR, 'index.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HttpResponse(html, content_type='text/html; charset=utf-8')
