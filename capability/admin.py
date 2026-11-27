from django.contrib import admin
from django.db import models
from django.db.models import Count
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms 
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from .models import Category, Capability, Industry, Material, SurfaceFinish, CapabilitySpec

# ============================================================
# 分类后台管理
# ============================================================
class CategoryAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('name', 'desc', 'show_on_home', 'order')
    # 允许在列表页直接编辑的字段（无需进入详情页）
    list_editable = ('show_on_home', 'order')
    # 顶部搜索框搜索的字段
    search_fields = ('name', 'desc')
    # 默认按 order 排序（已在模型的 Meta 中定义，此处可省略）


# ============================================================
# 行业后台管理
# ============================================================
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'icon')
    list_editable = ('icon',)          # 图标类名可直接在列表页编辑
    search_fields = ('name', 'desc')


# ============================================================
# 材料后台管理
# ============================================================
class MaterialAdmin(admin.ModelAdmin):
    # 【修改】增加了 'category'，方便我们在列表页直接看到它是金属还是塑料
    list_display = ('name', 'category', 'desc')
    # 【新增】允许在列表页直接下拉修改材料分类
    list_editable = ('category',)
    # 【新增】右侧添加分类过滤器
    list_filter = ('category',)
    search_fields = ('name', 'desc')


# ============================================================
# 【新增】表面处理后台管理
# ============================================================
class SurfaceFinishAdmin(admin.ModelAdmin):
    # 在列表页显示名称、图标、排序
    list_display = ('name', 'desc', 'icon', 'order')
    # 允许直接编辑图标和排序
    list_editable = ('icon', 'order')
    search_fields = ('name', 'desc')


# ============================================================
# 【新增】工艺规格内联组件 (Inline)
# ============================================================
# 作用：让你在编辑“CNC Turning”时，能在同一个页面下方直接添加/修改规格表格，无需跳转
class CapabilitySpecInline(admin.TabularInline):
    model = CapabilitySpec
    extra = 0  # 【修改】从 1 改为 0，不再自动生成空白行
    fields = ('spec_type', 'label', 'value', 'order')

    # 【关键修改】把单行输入框强制变成多行文本域
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 40})},
    }

# ============================================================
# 【新增】带数量统计的分类过滤器
# ============================================================
class CategoryCountFilter(SimpleListFilter):
    title = _('工艺分类')  # 过滤器显示的标题
    parameter_name = 'category'  # URL 里的参数名

    def lookups(self, request, model_admin):
        # 【优化】使用 annotate 在数据库层面一次性统计所有分类的数量
        categories = Category.objects.annotate(cap_count=Count('capabilities')).all()
        return [(str(cat.id), f"{cat.name} ({cat.cap_count})") for cat in categories]

    def queryset(self, request, queryset):
        # 当用户点击某个分类时，执行过滤
        if self.value():
            return queryset.filter(category__id=self.value())
        return queryset


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
    list_display = ('title', 'category', 'excerpt', 'show_on_home', 'order', 'views')

    # 允许在列表页直接编辑 show_on_home 和 order
    list_editable = ('show_on_home', 'order')

    # 右侧过滤器：按分类、行业、材料、表面处理筛选
    # 使用 RelatedOnlyFieldListFilter 保证只显示当前有工艺关联的选项，避免列表过长
    list_filter = (
        CategoryCountFilter, 
        'industries', 
        'materials',  # <--- 新增：材料过滤
        'surface_finishes'
    )

    # 顶部搜索框：搜索标题、摘要、描述
    search_fields = ('title', 'excerpt', 'description')

    # 自动生成 slug：输入 title 时自动填充 slug 字段
    prepopulated_fields = {'slug': ('title',)}

    # 多对多字段使用横向穿梭框，选择更直观
    # 【修改】加入了 'surface_finishes' 的穿梭框选择
    filter_horizontal = ('industries', 'materials', 'surface_finishes')

    # 【新增】将刚才写的 Inline 挂载到当前页面的底部
    inlines = [CapabilitySpecInline]

    # 【新增】让 hero_features 强制使用干净的多行文本框
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'hero_features' in form.base_fields:
            form.base_fields['hero_features'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'vLargeTextField'})
        return form
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        active_filters = []
        
        # 获取 URL 里的查询参数
        category_id = request.GET.get('category')
        industry_id = request.GET.get('industries__id__exact')
        material_id = request.GET.get('materials__id__exact')
        surface_id = request.GET.get('surface_finishes__id__exact')
        
        # 动态拼装中文提示
        if category_id:
            try:
                from .models import Category
                active_filters.append(f"分类: {Category.objects.get(id=category_id).name}")
            except Category.DoesNotExist: pass
            
        if industry_id:
            try:
                from .models import Industry
                active_filters.append(f"行业: {Industry.objects.get(id=industry_id).name}")
            except Industry.DoesNotExist: pass
            
        if material_id:
            try:
                from .models import Material
                active_filters.append(f"材料: {Material.objects.get(id=material_id).name}")
            except Material.DoesNotExist: pass
            
        if surface_id:
            try:
                from .models import SurfaceFinish
                active_filters.append(f"表面处理: {SurfaceFinish.objects.get(id=surface_id).name}")
            except SurfaceFinish.DoesNotExist: pass

        # 将拼装好的字符串列表传入上下文
        extra_context['active_filters'] = active_filters

        return super().changelist_view(request, extra_context=extra_context)


# ============================================================
# 注册模型到 Admin 后台
# ============================================================
admin.site.register(Category, CategoryAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Material, MaterialAdmin)
# 【新增】注册表面处理模型
admin.site.register(SurfaceFinish, SurfaceFinishAdmin)
admin.site.register(Capability, CapabilityAdmin)