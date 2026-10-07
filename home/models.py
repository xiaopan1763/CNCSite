from django.db import models

class Banner(models.Model):
    """首页首屏轮播图"""
    title = models.CharField(max_length=200, verbose_name="主标题")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="副标题")
    image = models.ImageField(upload_to='banners/', verbose_name="背景图")

    # 顶部小标签（如 "Excellent 4.9 out of 5 ★ Trustpilot"）
    eyebrow = models.CharField(max_length=150, blank=True, verbose_name="顶部小标签")

    # 主按钮
    primary_btn_text = models.CharField(max_length=50, blank=True, verbose_name="主按钮文字")
    primary_btn_url = models.CharField(max_length=200, blank=True, verbose_name="主按钮链接")

    # 次按钮
    secondary_btn_text = models.CharField(max_length=50, blank=True, verbose_name="次按钮文字")
    secondary_btn_url = models.CharField(max_length=200, blank=True, verbose_name="次按钮链接")

    # 主内容下方附加 HTML（用于特性标签、邮件提示、格式说明等）
    extra_html = models.TextField(blank=True, verbose_name="附加HTML（可选）")

    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_banner'
        ordering = ['order', 'id']
        verbose_name = '首页轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class FactSpec(models.Model):
    """首页"Manufacturing Capabilities at a Glance"表格的每一行"""
    label = models.CharField(max_length=100, verbose_name="项目名称")
    value = models.CharField(max_length=200, verbose_name="规格数值")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_fact_spec'
        ordering = ['order', 'id']
        verbose_name = '首页事实表格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.label}: {self.value}"


class FAQ(models.Model):
    """首页 FAQ 问答条目"""
    question = models.CharField(max_length=300, verbose_name="问题")
    answer = models.TextField(verbose_name="回答")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_faq'
        ordering = ['order', 'id']
        verbose_name = '首页FAQ'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.question
    
class StatItem(models.Model):
    """首页数据统计条目"""
    DISPLAY_CHOICES = [
        ('partner', 'Trusted Partner CTA'),
        ('order', 'Ready to Order CTA'),
        ('both', 'Both CTAs'),
    ]

    label = models.CharField(max_length=100, verbose_name="标签")
    value = models.CharField(max_length=50, verbose_name="数值")
    suffix = models.CharField(max_length=20, blank=True, verbose_name="后缀")
    display_in = models.CharField(
        max_length=20,
        choices=DISPLAY_CHOICES,
        default='both',
        verbose_name="显示位置"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_stat_item'
        ordering = ['order', 'id']
        verbose_name = '首页数据统计'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.value}{self.suffix} {self.label}"
    
class OrderStep(models.Model):
    """首页"如何下单"流程步骤"""
    title = models.CharField(max_length=100, verbose_name="步骤标题")
    description = models.TextField(verbose_name="步骤描述")
    icon = models.CharField(
        max_length=50, blank=True,
        verbose_name="图标类名",
        help_text="Bootstrap Icons 类名，如 'bi bi-file-earmark-arrow-up'"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_order_step'
        ordering = ['order', 'id']
        verbose_name = '首页下单步骤'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    """客户评价"""
    author = models.CharField(max_length=100, verbose_name="客户名称")
    date_text = models.CharField(max_length=50, verbose_name="日期文本")
    title = models.CharField(max_length=150, verbose_name="评价标题")
    content = models.TextField(verbose_name="评价内容")
    rating = models.PositiveIntegerField(default=5, verbose_name="评分（1-5）")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="启用")

    class Meta:
        db_table = 'home_testimonial'
        ordering = ['order', 'id']
        verbose_name = '客户评价'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.author} - {self.title}"