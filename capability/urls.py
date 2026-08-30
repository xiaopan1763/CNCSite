from django.urls import path
from . import views

app_name = 'capability'  # 定义命名空间，防止不同应用之间的URL重名冲突

urlpatterns = [
    # path('register/', views.register, name='register'),  # path(路径, 视图函数引用, name=别名)
    # path('login/', views.login, name='login'),  # 当用户访问/login/时，调用views.login函数
    # path('logout/', views.logout, name='logout')  # /logout/ 对应登出视图
]