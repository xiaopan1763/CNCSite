from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    # 列表页显示核心信息
    list_display = ('user', 'name', 'email', 'company', 'service_type', 'created_at', 'is_processed')
    list_editable = ('is_processed',)
    list_filter = ('is_processed', 'created_at', 'service_type')
    search_fields = ('name', 'email', 'company', 'message')
    readonly_fields = ('user', 'name', 'email', 'phone', 'country', 'company', 'service_type', 'quantity', 'message', 'cad_file', 'created_at')
    
    # 按照区块划分后台详情页
    fieldsets = (
        ('Account Info', {'fields': ('user', 'name', 'email', 'phone', 'country')}),
        ('Project Details', {'fields': ('company', 'service_type', 'quantity', 'message', 'cad_file')}),
        ('Status', {'fields': ('is_processed', 'created_at')}),
    )
    
    def has_add_permission(self, request):
        return False