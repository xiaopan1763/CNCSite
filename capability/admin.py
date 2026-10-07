from django.contrib import admin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Category, Capability, Industry, Material


# ============================================================
# 分类后台管理
# ============================================================
class CategoryAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('name', 'show_on_home', 'order')
    # 允许在列表页直接编辑的字段（无需进入详情页）
    list_editable = ('show_on_home', 'order')
    # 顶部搜索框搜索的字段
    search_fields = ('name', 'desc')
    # 默认按 order 排序（已在模型的 Meta 中定义，此处可省略）


# ============================================================
# 行业后台管理
# ============================================================
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    list_editable = ('icon',)          # 图标类名可直接在列表页编辑
    search_fields = ('name', 'desc')


# ============================================================
# 材料后台管理
# ============================================================
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'desc')


# ============================================================
# 工艺后台管理（核心）
# ============================================================
class CapabilityAdmin(admin.ModelAdmin):
    # 用 CKEditor5 富文本编辑器替换所有 TextField 的默认小部件
    # config_name="extends" 对应 settings.py 中 CKEDITOR_5_CONFIGS 里的配置
    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="extends")},
    }

    # 列表页显示的字段，便于快速浏览
    list_display = ('title', 'category', 'show_on_home', 'order', 'views')

    # 允许在列表页直接编辑 show_on_home 和 order
    list_editable = ('show_on_home', 'order')

    # 右侧过滤器：按分类和行业筛选
    list_filter = ('category', 'industries', 'show_on_home')

    # 顶部搜索框：搜索标题、摘要、描述
    search_fields = ('title', 'excerpt', 'description')

    # 自动生成 slug：输入 title 时自动填充 slug 字段
    prepopulated_fields = {'slug': ('title',)}

    # 多对多字段使用横向穿梭框，选择更直观
    filter_horizontal = ('industries', 'materials')


# ============================================================
# 注册模型到 Admin 后台
# ============================================================
admin.site.register(Category, CategoryAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Capability, CapabilityAdmin)