from django.contrib import admin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Category, Tag, Capability

class CapabilityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="extends")},  # 使用 CKEditor5Widget 替换 TextField 的默认小部件
    }
    list_filter = ('category', 'tags')   # 右侧过滤器
    search_fields = ('title', 'description')    # 顶部搜索框
    prepopulated_fields = {'slug': ('title',)}        # 自动生成 slug

admin.site.register(Category)   # 将Category模型注册到admin后台
admin.site.register(Tag)    # 将Tag模型注册到admin后台
admin.site.register(Capability, CapabilityAdmin) # 将Capability模型注册到admin后台，并使用CapabilityAdmin自定义管理类