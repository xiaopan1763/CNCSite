from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings # 引入 settings 以关联用户

class Inquiry(models.Model):
    # 关联注册用户 (如果用户被删除，询盘记录保留，user 字段置空)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联账号")

    # 客户基础信息 (前端隐藏，后端自动从注册信息填充)
    name = models.CharField(max_length=150, blank=True, verbose_name="客户姓名")
    email = models.EmailField(blank=True, verbose_name="邮箱地址")
    phone = models.CharField(max_length=50, blank=True, verbose_name="电话号码")
    country = models.CharField(max_length=100, blank=True, verbose_name="国家/地区")
    
    # 客户补充信息 (前端显示让客户填写)
    company = models.CharField(max_length=150, blank=True, verbose_name="公司名称")
    
    # 项目详细信息
    service_type = models.CharField(max_length=100, verbose_name="所需服务", help_text="例如：CNC Turning, 3D Printing")
    quantity = models.CharField(max_length=50, blank=True, verbose_name="需求数量", help_text="例如：1-10, 1000+")
    message = models.TextField(verbose_name="项目描述/要求")
    
    # 文件上传
    cad_file = models.FileField(
        upload_to='inquiries/%Y/%m/', 
        blank=True, 
        null=True, 
        verbose_name="CAD文件 (STEP/STP/IGES/PDF/ZIP)",
        validators=[FileExtensionValidator(allowed_extensions=['step', 'stp', 'iges', 'igs', 'pdf', 'zip', 'rar'])]
    )
    
    # 状态追踪与后台管理
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    is_processed = models.BooleanField(default=False, verbose_name="是否已处理")

    class Meta:
        db_table = 'inquiry_record'
        ordering = ['-created_at']
        verbose_name = '客户询盘'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.email} - {self.service_type} ({self.created_at.strftime('%Y-%m-%d')})"