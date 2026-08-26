from django.shortcuts import render, redirect  # render用于渲染模板，redirect用于重定向
from django.contrib import auth  # Django自带的认证系统，用于登录、登出等操作
from . import models  # 导入本应用的models
from . import forms  # 导入本应用的forms模块

def register(request):  # 定义注册视图函数，接收request请求对象
    """
    用户注册view方法
    :param request: 请求对象
    :return: 返回渲染后的注册页面或重定向
    """
    if request.method == 'POST':
        form_obj = forms.RegForm(request.POST, request.FILES)
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            # 1. 从邮箱提取基础用户名
            email = data.get('email')
            base_username = email.split('@')[0]  # 取 @ 前面的部分
            # 2. 确保用户名唯一
            username = base_username
            counter = 1
            while models.Reguser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            # 3. 将用户名加入 data 字典（移除 repassword）
            data.pop('repassword')
            data['username'] = username   # 添加 username 字段
            # 4. 创建用户（注意 is_staff 和 is_superuser 按需求设置）
            user_obj = models.Reguser.objects.create_user(**data, is_staff=1, is_superuser=0)
            auth.login(request, user_obj)
            return redirect('/')
    else:
        form_obj = forms.RegForm()
    return render(request, 'user/register.html', {'form_obj': form_obj})  # 渲染注册页面，把表单对象传给模板

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=email, password=password)  # 注意参数名仍是 username
        print(user)
        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            error = 'Invalid email or password'
            return render(request, 'user/login.html', {'error': error})
    return render(request, 'user/login.html')

def logout(request):  # 登出视图函数
    auth.logout(request)  # logout清除当前用户的会话信息，变成未登录状态
    # 跳转到首页
    return redirect('/')  # 重定向到首页