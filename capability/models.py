from django.db import models  # 导入 Django 模型模块

class Category(models.Model):
    # 分类名字
    name = models.CharField(max_length=32, verbose_name='分类名')  # 分类名称
    # 分类描述
    desc = models.CharField(max_length=150, verbose_name='描述', null=True)  # 分类描述，可为空

    class Meta:
        db_table = 'capa_category'  # 指定数据库表名
        verbose_name = '分类表'  # 后台单数名称
        verbose_name_plural = verbose_name  # 后台复数名称

    def __str__(self):
        return self.name  # 后台显示分类名

class Tag(models.Model):
    # 标签名字
    name = models.CharField(max_length=32, verbose_name='标签名')  # 标签名称
    # 标签描述
    desc = models.CharField(max_length=150, verbose_name='描述', null=True)  # 标签描述，可为空

    class Meta:
        db_table = 'capa_tag'  # 指定数据库表名
        verbose_name = '标签表'  # 后台单数名称
        verbose_name_plural = verbose_name  # 后台复数名称

    def __str__(self):
        return self.name # 后台显示标签名

class Capability(models.Model):
    # 标题
    title = models.CharField(max_length=100, verbose_name="工艺名称")
    # 自动生成友好的URL
    slug = models.SlugField(unique=True, verbose_name="URL标识")
    # 排序字段
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    # 正文
    description = models.TextField(verbose_name="工艺描述")
    # 上传的图片
    image = models.ImageField(upload_to='capabilities/', blank=True, verbose_name="展示图片")
     # 归属的分类
    # 代表一对多的映射关系
    # on_delete CASCADE表示：category记录删除的同时，关联的文章也会被删除
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="工艺分类")  # 外键，关联分类
    # 文章标签
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="行业标签")  # 多对多，自动生成第三张关联表
    # 浏览量
    views = models.IntegerField(default=0, verbose_name="浏览量")  # 浏览量，默认为0
    
    

    """以下为可选的详细字段，根据需要自行删减"""
    # icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome 图标类名，如 'fa-cogs'", verbose_name="图标")
    # is_featured = models.BooleanField(default=False, verbose_name="首页推荐")
    # max_part_size = models.CharField(max_length=100, blank=True, verbose_name="最大加工尺寸")
    # tolerance = models.CharField(max_length=100, blank=True, verbose_name="公差精度")
    # materials = models.ManyToManyField('materials.Material', blank=True, verbose_name="适用材料")
    # 创建时间
    # created_time = models.DateTimeField(verbose_name="创建时间")  # 创建时间
    # 最后修改时间
    # updated_time = models.DateTimeField(verbose_name="最后修改时间")  # 最后修改时间
    # 摘要
    # excerpt = models.CharField(max_length=200, blank=True, verbose_name="文章摘要")  # 摘要，可为空
    # 作者
    # author = models.ForeignKey(Reguser, on_delete=models.CASCADE, verbose_name="作者")  # 外键，关联用户
   

    class Meta:
        ordering = ['order', 'title']  # 按照排序字段和名称排序
        db_table = 'capa_info'  # 指定数据库表名
        verbose_name = '工艺表'  # 后台单数名称
        verbose_name_plural = verbose_name  # 后台复数名称

    def __str__(self):
        return self.title  # 后台显示工艺名