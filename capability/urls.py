from django.urls import path
from . import views

app_name = 'capability'

urlpatterns = [
    # 列表页（放在最前面，路由为空代表访问 /capabilities/ 时会进入此视图）
    path('', views.CapabilityListView.as_view(), name='list'),
    # 详情页 (放在最后)
    path('<slug:slug>/', views.CapabilityDetailView.as_view(), name='detail'),
]