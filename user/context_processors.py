from . import forms


def register_form(request):
    """让所有页面都能访问注册表单实例"""
    return {
        'form_obj': forms.RegForm(),
    }