from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from . import models, forms


def register(request):
    if request.method == 'POST':
        form_obj = forms.RegForm(request.POST, request.FILES)
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            data.pop('repassword')

            email = data.get('email')
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while models.Reguser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            data['username'] = username
            user_obj = models.Reguser.objects.create_user(
                **data, is_staff=1, is_superuser=0
            )
            auth.login(request, user_obj)
            return redirect(request.POST.get('next') or '/')

        # 注册失败：存入 session
        request.session['open_modal'] = 'registerModal'
        request.session['register_errors'] = form_obj.errors.as_json()
        return redirect('/')

    # GET 请求（一般不会触发，因为表单在模态框里）
    return redirect('/')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=email, password=password)
        if user:
            auth.login(request, user)
            return redirect(request.POST.get('next') or '/')

        # 登录失败：存 session，重定向首页
        request.session['open_modal'] = 'loginModal'
        request.session['login_error'] = 'Invalid email or password'
        return redirect('/')

    return redirect('/')

def logout(request):  # 登出视图函数
    auth.logout(request)  # logout清除当前用户的会话信息，变成未登录状态
    # 跳转到首页
    return redirect('/')  # 重定向到首页