from django import forms  # 导入Django表单模块
from django.core.exceptions import ValidationError  # 导入校验异常类
from . import models  # 导入当前应用中的models模块
from django_countries import countries  # 导入国家列表

class RegForm(forms.Form):  # 定义一个继承自forms.Form的表单类RegForm
    email = forms.EmailField(  # 邮箱字段，EmailField自带邮箱格式校验
        required=True,  # required=True表示该字段为必填
        label='Email',
        error_messages={
            'required': 'Please enter your email',
            'invalid': 'Please enter a valid email address'  # invalid键表示格式不合法时的提示
        },
        widget=forms.EmailInput(  # 渲染为type=email的输入框
            attrs={
                'class': "form-control",
                'placeholder': 'Enter your email'
            }
        )
    )
    password = forms.CharField(  # 密码字段
        label='Password',  # 字段标签
        min_length=6,  # 最小长度限制
        error_messages={  # 自定义错误提示
            'required': 'Please enter your password',  # 必填为空时提示
            'min_length': 'Password must be at least 6 characters long'  # 长度不足时提示
        },
        # <input type='password' />
        widget=forms.PasswordInput(  # 渲染为密码输入框，输入内容被掩码
            attrs={
                'class': "form-control",
                'placeholder': 'Enter your password'
            }
        )
    )
    repassword = forms.CharField(  # 确认密码字段
        label='Confirm Password',
        error_messages={  # 自定义错误提示
            'required': 'Please re-enter the password',  # 必填为空时提示
            'min_length': 'Password must be at least 6 characters long'  # 长度不足时提示
        },
        # <input type='password' />
        widget=forms.PasswordInput(  # 同样渲染为密码框
            attrs={
                'class': "form-control",
                'placeholder': 'Confirm your password'
            }
        )
    )
    first_name = forms.CharField(  # 用户名字段，CharField对应普通的文本输入框
        label='First Name',  # 字段标签，渲染到HTML时显示为元素
        max_length=50,  # 最大长度限制，超出则校验失败
        required=False,
        error_messages={  # 自定义错误提示信息
            'max_length': 'Name cannot exceed 50 characters'  # 长度超限时提示
        },
        widget=forms.TextInput(  # widget决定渲染成什么HTML控件，这里渲染为文本框
            attrs={  # attrs用于设置HTML属性
                'class': "form-control",  # 套用Bootstrap样式类名
                'placeholder': 'Enter your first name'  # placeholder设置输入框提示占位符
            }
        )
    )
    last_name = forms.CharField(  # 用户名字段，CharField对应普通的文本输入框
        label='Last Name',  # 字段标签，渲染到HTML时显示为元素
        max_length=50,  # 最大长度限制，超出则校验失败
        required=False,
        error_messages={  # 自定义错误提示信息
            'max_length': 'Name cannot exceed 50 characters'  # 长度超限时提示
        },
        widget=forms.TextInput(  # widget决定渲染成什么HTML控件，这里渲染为文本框
            attrs={  # attrs用于设置HTML属性
                'class': "form-control",  # 套用Bootstrap样式类名
                'placeholder': 'Enter your last name'  # placeholder设置输入框提示占位符
            }
        )
    )
    mobile = forms.CharField(  # 手机号码字段
        label='Mobile',
        required=True,  # required=True表示必填
        min_length=8,  # 最小长度限制为8位
        error_messages={
            'required': 'Please enter your mobile number',
            'min_length': 'Please enter a valid mobile number',
        },
        widget=forms.TextInput(
            attrs={
                'class': "form-control",
                'placeholder': 'Enter your mobile number'
            }
        )
    )
    country = forms.ChoiceField(
        choices=countries,  # 使用英文列表
        label='Country/Region',
        initial='US',                # 默认选中美国
        required=True,
        error_messages={
            'required': 'Please select a country/region'
        },
        widget=forms.Select(
            attrs={
                'class': "form-control"
            }
        )
    )    
    # 确认密码和密码一致性检查
    # clean_字段名()方法：Django表单校验中，名字以clean_开头的方法会被自动调用，用于该字段的业务校验
    def clean_repassword(self):  # 校验确认密码字段
        passwd = self.cleaned_data.get('password')  # cleaned_data是字典，用get获取已经校验过的password值
        repasswd = self.cleaned_data.get('repassword')
        if repasswd and repasswd != passwd:  # 如果确认密码非空且与密码不一致
            self.add_error("repassword", ValidationError("Passwords do not match"))  # add_error给该字段添加错误信息
        else:  # 如果一致，则返回字段值
            return repasswd  # 校验通过务必return该值，否则cleaned_data中会缺少该字段
        
    # Email存在性检查
    def clean_email(self):
        input_email = self.cleaned_data.get('email')  # 获取用户填写的邮箱
        # ORM：filter返回一个QuerySet，相当于一个对象列表；如果结果非空说明邮箱已存在
        email = models.Reguser.objects.filter(email=input_email)  # 在数据库Reguser表中查找email等于input_email的记录
        if email:  # 如果QuerySet非空（有记录）
            self.add_error("email", ValidationError("This email has been registered"))  # 添加错误信息
        else:  # 如果不存在
            return input_email  # 返回该邮箱