from django.db import models
from django.core.exceptions import ValidationError


# ============================================================
# 分类模型：对应 7 大分类（Manufacturing Services、Fabrication 等）
# ============================================================
class Category(models.Model):
    # 分类名称，如 "Manufacturing Services"，最长 32 字符
    name = models.CharField(max_length=32, verbose_name='分类名')

    # 分类描述，用于首页卡片展示，最长 255 字符，可为空
    desc = models.CharField(max_length=255, verbose_name='描述', null=True, blank=True)

    # 分类图片：上传后保存到 media/category/ 目录，用于首页圆形卡片
    image = models.ImageField(upload_to='category/', blank=True, null=True, verbose_name="分类图片")

    # 是否在首页显示：勾选后该分类会出现在首页的圆形卡片区
    # 通过下方的 clean() 方法限制最多只能勾选 3 个
    show_on_home = models.BooleanField(default=False, verbose_name="首页显示")

    # 排序字段：数字越小越靠前，便于手动调整首页显示顺序
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        db_table = 'capa_category'          # 自定义数据库表名，避免与 Django 内置表冲突
        ordering = ['order', 'name']        # 默认按 order 升序、name 升序排列
        verbose_name = '分类表'
        verbose_name_plural = verbose_name  # 后台显示复数名称与单数一致

    def __str__(self):
        # 后台列表和下拉框显示分类名
        return self.name

    def clean(self):
        """
        自定义验证：限制首页最多显示 3 个分类。
        注意：clean() 在 Django Admin 保存时会自动触发；
        如果通过代码直接 save()，需要手动调用 full_clean()。
        """
        super().clean()
        if self.show_on_home:
            # 查询所有已勾选 show_on_home 的分类
            qs = Category.objects.filter(show_on_home=True)
            # 编辑已有记录时，排除自身，避免把自己算进去
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # 如果已有 3 个分类勾选，则抛出验证错误
            if qs.count() >= 3:
                raise ValidationError({'show_on_home': '最多同时选择三个分类'})

    @property
    def structured_data(self):
        """
        GEO 优化：返回该分类的 Schema.org 结构化数据（JSON-LD）。
        CollectionPage 表示这是一个"集合页"（即某分类下的工艺列表）。
        在模板中通过 {% json_ld_for obj %} 标签渲染为 <script type="application/ld+json">。
        """
        return {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": self.name,
            "description": self.desc or "",
            "image": self.image.url if self.image else "",
        }


# ============================================================
# 行业模型：替代原 Tag，用于标记工艺服务的行业
# ============================================================
class Industry(models.Model):
    # 行业名称，如 "Aerospace"，最长 32 字符
    name = models.CharField(max_length=32, verbose_name='行业名')

    # 行业描述，最长 255 字符，可为空
    desc = models.CharField(max_length=255, verbose_name='描述', null=True, blank=True)

    # Bootstrap Icons 类名，如 'bi-rocket-takeoff'，用于首页行业板块展示图标
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标类名')

    class Meta:
        db_table = 'capa_industry'
        verbose_name = '行业表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def structured_data(self):
        """
        GEO 优化：DefinedTerm 表示这是一个"术语定义"（行业名称），
        帮助 AI 理解你的网站定义了哪些行业分类。
        """
        return {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": self.name,
            "description": self.desc or "",
        }


# ============================================================
# 材料模型：用于标记工艺可加工的材料
# ============================================================
class Material(models.Model):
    # 【新增】材料分类选项：用于前端详情页的 "金属/塑料" Tab 切换
    CATEGORY_CHOICES = (
        ('metal', 'Metals'),
        ('plastic', 'Plastics'),
        ('other', 'Other'),
    )

    # 材料名称，如 "Aluminium"，最长 32 字符
    name = models.CharField(max_length=32, verbose_name='材料名')

    # 材料描述，如 "Aluminium 6061, 7075 — 轻质、耐腐蚀"，最长 255 字符
    desc = models.CharField(max_length=255, verbose_name='描述', null=True, blank=True)

    # 材料图片，上传后保存到 media/materials/ 目录，可为空
    image = models.ImageField(upload_to='materials/', blank=True, null=True, verbose_name="材料图片")

    # 【新增】材料分类字段：默认归类为 metal
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='metal', 
        verbose_name="材料大类"
    )

    class Meta:
        db_table = 'capa_material'
        verbose_name = '材料表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def structured_data(self):
        """GEO 优化：与 Industry 同理，用 DefinedTerm 声明材料术语。"""
        return {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": self.name,
            "description": self.desc or "",
        }


# ============================================================
# 【新增】表面处理模型：用于详情页第6板块的卡片展示
# ============================================================
class SurfaceFinish(models.Model):
    # 表面处理名称，如 "Anodizing"
    name = models.CharField(max_length=50, verbose_name="表面处理名称")
    
    # 处理描述，展示在卡片下方
    desc = models.CharField(max_length=255, verbose_name="描述", blank=True)
    
    # Bootstrap 图标类名（在未上传图片前，用图标占位）
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标类名")

    # 【新增这一行】表面处理图片
    image = models.ImageField(upload_to='finishes/', blank=True, null=True, verbose_name="展示图片")
    
    # 排序字段
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        db_table = 'capa_surface_finish'
        ordering = ['order', 'id']
        verbose_name = '表面处理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# ============================================================
# 【新增】工艺规格模型：用于详情页第3板块的规格表格 (Fact Table)
# ============================================================
class CapabilitySpec(models.Model):
    # 类型选项
    SPEC_TYPE_CHOICES = (
        ('tolerance', 'Service Tolerances (左侧表格)'),
        ('guideline', 'Design Guidelines (右侧表格)'),
    )
    # 外键关联核心工艺。使用字符串 'Capability' 防止循环引用；related_name 允许我们用 capability.specs.all() 反向查询
    capability = models.ForeignKey('Capability', on_delete=models.CASCADE, related_name='specs', verbose_name="所属工艺")

    # 类型字段，默认左侧
    spec_type = models.CharField(
        max_length=20, 
        choices=SPEC_TYPE_CHOICES, 
        default='tolerance', 
        verbose_name="表格类型"
    )
    # 表格左侧的项目名（如 Max Part Size）
    label = models.CharField(max_length=100, verbose_name="规格名称")
    # 表格右侧的具体数值（如 Ø500 mm）
    value = models.CharField(max_length=200, verbose_name="规格数值")
    # 排序
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        db_table = 'capa_spec'
        ordering = ['order', 'id']
        verbose_name = '工艺规格表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.capability.title} - {self.label}"


# ============================================================
# 工艺模型：核心内容，对应具体的加工能力（CNC Turning 等）
# ============================================================
class Capability(models.Model):
    # 工艺名称，如 "CNC Turning"，最长 100 字符
    title = models.CharField(max_length=100, verbose_name="工艺名称")

    # URL 标识：用于生成友好的 URL，如 /capabilities/cnc-turning/
    # unique=True 保证每条记录的 slug 唯一，避免 URL 冲突
    slug = models.SlugField(unique=True, verbose_name="URL标识")

    # 排序字段：数字越小越靠前
    order = models.PositiveIntegerField(default=0, verbose_name="排序")

    # 【新增】详情页Hero首屏卖点（按行输入，前端自动转成打勾列表）
    hero_features = models.TextField(
        blank=True, 
        verbose_name="详情页首屏核心卖点",
        help_text="每行输入一个卖点，前端会自动显示为带打勾图标的列表。"
    )

    # 完整工艺描述：详情页展示，支持富文本（无限长度）
    description = models.TextField(verbose_name="工艺描述")

    # 摘要：首页卡片展示，最长 200 字符，建议 80-100 字符以内
    excerpt = models.CharField(max_length=200, blank=True, verbose_name="摘要")

    # 工艺展示图片：上传后保存到 media/capabilities/ 目录
    image = models.ImageField(upload_to='capabilities/', blank=True, verbose_name="展示图片")

    # 是否在首页显示：勾选后该工艺会出现在首页的工艺卡片区
    show_on_home = models.BooleanField(default=False, verbose_name="首页显示")

    # 外键：关联分类。on_delete=CASCADE 表示分类删除时，其下的工艺也一并删除
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='capabilities', verbose_name="工艺分类")

    # 多对多：一个工艺可服务多个行业，一个行业可被多个工艺服务
    industries = models.ManyToManyField(Industry, blank=True, related_name='capabilities', verbose_name="服务行业")

    # 多对多：一个工艺可用多种材料，一种材料可被多个工艺使用
    materials = models.ManyToManyField(Material, blank=True, related_name='capabilities', verbose_name="适用材料")

    # 多对多：一个工艺可支持多种表面处理
    surface_finishes = models.ManyToManyField(SurfaceFinish, blank=True, related_name='capabilities', verbose_name="适用表面处理")

    # 浏览量：默认 0，可在详情页累加
    views = models.IntegerField(default=0, verbose_name="浏览量")

    # 以下为可选技术参数，用于详情页展示专业性
    max_part_size = models.CharField(max_length=100, blank=True, verbose_name="最大加工尺寸")
    tolerance = models.CharField(max_length=100, blank=True, verbose_name="公差精度")

    class Meta:
        ordering = ['order', 'title']       # 默认按 order 升序、名称升序
        db_table = 'capa_info'
        verbose_name = '工艺表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    @property
    def structured_data(self):
        """
        GEO 优化：返回 Service 类型的结构化数据。
        """
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": self.title,
            # 优先使用摘要，没有摘要则截取描述的前 160 字符
            "description": self.excerpt or self.description[:160],
            "image": self.image.url if self.image else "",
            "provider": {
                "@type": "Organization",
                "name": "Forest Machining",
                "url": "https://guanhaoauto.com"  # 修正了之前的 TODO 域名
            },
            # areaServed 和 material 会被 AI 用作筛选依据
            "areaServed": [ind.name for ind in self.industries.all()],
            "material": [mat.name for mat in self.materials.all()],
            # 【新增】表面处理也加入 GEO 数据
            "surfaceFinish": [sf.name for sf in self.surface_finishes.all()],
            "category": self.category.name,
        }