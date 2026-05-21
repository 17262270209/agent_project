from django.urls import path, include, re_path
from apps.frontend.views import index

urlpatterns = [
    path('api/chat/', include('apps.chat.urls')),
    path('api/knowledge/', include('apps.knowledge.urls')),
    path('api/system/', include('apps.system.urls')),
    # 前端 SPA：所有非 API 路径返回 index.html (Vue Router 处理路由)
    re_path(r'^(?!api/).*$', index),
]
