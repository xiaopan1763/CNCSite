"""
URL configuration for myweb project.

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
from django.contrib import admin  # Django自带的后台管理系统
from django.urls import path, include  # path定义路由，include用于包含其他urls模块
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # 后台管理路由，访问/admin/会进入Django自带的管理后台
    path('', include('user.urls')),  # 把user应用的urls.py文件包含进来，这样才能访问 /register/、/login/ 等路径
    path('capabilities/', include('capability.urls')),  # 把capability应用的urls.py文件包含进来，这样才能访问 /capability/ 下的路径
    path('ckeditor/', include('django_ckeditor_5.urls')),  # 挂载CKEditor5相关URL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 配置媒体文件的访问路径