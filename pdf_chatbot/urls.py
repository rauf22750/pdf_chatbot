"""
URL configuration for pdf_chatbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth import views 
from pdf_chatbot import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as auth_views
from pdf_chatbot import api_views
urlpatterns = [
    path('accounts/login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('', views.chat_view, name='chat'),
    path('logout/', views.logout_view, name='logout'),
    # API endpoints
    path('admin/', admin.site.urls),
    path('api/login/', api_views.login_api, name='login_api'),
    path('api/register/', api_views.register_api, name='register_api'),
    path('api/chat/', api_views.chat_api, name='chat_api'),
    path('api/upload_pdf/', api_views.upload_pdf, name='upload_pdf_api'),
    path('api/logout/', api_views.logout_api, name='logout_api'),
    
]

if settings.DEBUG:
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
