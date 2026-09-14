"""
Configuração de rotas principais do MigrantIA.
"""
from django.contrib import admin
from django.urls import path, include
from apps.chat.views import ChatHomeView

urlpatterns = [
    path('', ChatHomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('api/chat/', include('apps.chat.urls')),
]
