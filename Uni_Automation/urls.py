"""
URL configuration for Uni_Automation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from Uni_Automation import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('courses/',include('course_module.urls')),
    path('',include('news_module.urls')),
    path('semesters/',include('semester_module.urls')),
    path('permits/',include('permits_module.urls')),
    path('review/',include('review_module.urls')),
    path('user_module/',include('user_module.urls')),
    path('ticket_module/',include('ticket_module.urls')),
    path('auth/',include('auth_module.urls')),
    path('exam_module/',include('exam_module.urls'))
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
