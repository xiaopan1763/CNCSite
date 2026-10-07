from django.db import models
from django.core.exceptions import ValidationError


# ============================================================
# 分类模型：对应 7 大分类（Manufacturing Services、Fabrication 等）
# ============================================================
class Category(models.Model):
    # 分类名称，如 "Manufacturing Services"，最长 32 字符
    name = models.CharField(max_length=32, verbose_name='分类名')

    # 分类描述，用于首页卡片展示，最长 150 字符，可为空
    desc = models.CharField(max_length=150, verbose_name='描述', null=True, blank=True)

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

    # 行业描述，最长 150 字符，可为空
    desc = models.CharField(max_length=150, verbose_name='描述', null=True, blank=True)

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
    # 材料名称，如 "Aluminium"，最长 32 字符
    name = models.CharField(max_length=32, verbose_name='材料名')

    # 材料描述，如 "Aluminium 6061, 7075 — 轻质、耐腐蚀"，最长 150 字符
    desc = models.CharField(max_length=150, verbose_name='描述', null=True, blank=True)

    # 材料图片，上传后保存到 media/materials/ 目录，可为空
    image = models.ImageField(upload_to='materials/', blank=True, null=True, verbose_name="材料图片")

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

    # 完整工艺描述：详情页展示，支持富文本（无限长度）
    description = models.TextField(verbose_name="工艺描述")

    # 摘要：首页卡片展示，最长 200 字符，建议 80-100 字符以内
    excerpt = models.CharField(max_length=200, blank=True, verbose_name="摘要")

    # 工艺展示图片：上传后保存到 media/capabilities/ 目录
    image = models.ImageField(upload_to='capabilities/', blank=True, verbose_name="展示图片")

    # 是否在首页显示：勾选后该工艺会出现在首页的工艺卡片区
    show_on_home = models.BooleanField(default=False, verbose_name="首页显示")

    # 外键：关联分类。on_delete=CASCADE 表示分类删除时，其下的工艺也一并删除
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="工艺分类")

    # 多对多：一个工艺可服务多个行业，一个行业可被多个工艺服务
    industries = models.ManyToManyField(Industry, blank=True, verbose_name="服务行业")

    # 多对多：一个工艺可用多种材料，一种材料可被多个工艺使用
    materials = models.ManyToManyField(Material, blank=True, verbose_name="适用材料")

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
        为什么用 Service 而不是 Product？
        - 你的业务是"加工服务"，不是出售实体产品
        - Service 类型让 AI 准确理解你提供的"能力"
        - areaServed 声明服务行业，material 声明可加工材料，
          这些字段会被 AI 用于回答"谁能加工钛合金的航空零件"这类问题
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
                "url": "https://www.yourdomain.com"    # TODO: 替换为你的真实域名
            },
            # areaServed 和 material 会被 AI 用作筛选依据
            "areaServed": [ind.name for ind in self.industries.all()],
            "material": [mat.name for mat in self.materials.all()],
            "category": self.category.name,
        }