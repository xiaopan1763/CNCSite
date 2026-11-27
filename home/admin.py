from django.contrib import admin
from .models import Banner, FactSpec, FAQ, StatItem, OrderStep, Testimonial, CaseStudy

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'eyebrow', 'extra_html', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle', 'eyebrow')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'subtitle', 'eyebrow', 'image')
        }),
        ('按钮', {
            'fields': (
                'primary_btn_text', 'primary_btn_url',
                'secondary_btn_text', 'secondary_btn_url',
            )
        }),
        ('附加内容', {
            'fields': ('extra_html',),
            'description': '可粘贴 HTML 片段，例如特性标签、邮件提示等。'
        }),
        ('状态', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(FactSpec)
class FactSpecAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')
    search_fields = ('label', 'value')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'suffix', 'display_in', 'order', 'is_active')
    list_editable = ('value', 'suffix', 'display_in', 'order', 'is_active')
    list_filter = ('display_in', 'is_active')
    search_fields = ('label', 'value')

@admin.register(OrderStep)
class OrderStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'content', 'rating', 'order', 'is_active')
    list_editable = ('rating', 'order', 'is_active')
    search_fields = ('author', 'title', 'content')
    list_filter = ('rating', 'is_active')

@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_industry', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'client_industry')
    search_fields = ('title', 'challenge', 'solution')
    
    # 按照区块划分编辑页面，更清晰
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'client_industry', 'image')
        }),
        ('案例详情', {
            'fields': ('challenge', 'solution', 'result'),
            'description': '请详细描述客户的痛点和我们提供的价值，这将直接显示在前端页面上。'
        }),
        ('状态与排序', {
            'fields': ('order', 'is_active')
        }),
    )