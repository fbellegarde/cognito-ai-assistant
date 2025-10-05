# D:\cognito_ai_assistant\ai_core\urls.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required # Secures views

urlpatterns = [
    # Secures the home page: only logged-in users can see it
    path('', login_required(views.home_view), name='home'),
    path('chat/', login_required(views.ai_chat_view), name='ai_chat'),
    path('recommendations/', login_required(views.recommender_view), name='recommender'),
]