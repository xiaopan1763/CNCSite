from django.contrib import admin
from .models import Reguser

admin.site.register(Reguser)  # 注册后模型出现在后台，可进行增删改查
