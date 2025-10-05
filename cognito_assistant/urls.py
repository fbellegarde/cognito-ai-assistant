# D:\cognito_ai_assistant\cognito_assistant\urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # <<< ADDED: Includes login, logout, password change
    path('', include('ai_core.urls')), # Root URL goes to ai_core
]