from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField

class Reguser(AbstractUser):
    """
    用户信息表，扩展了 admin.auth.user
    """
    """
    继承 AbstractUser 后，默认有 username、email 等字段
    我们将 email 设为唯一的，并作为登录凭证
    如果需要保留 username 字段（用于显示或后台），可以保留，但不再作为登录凭证
    不需要额外修改，因为 AbstractUser 自带 username
    注意：如果保留 username，需要确保其唯一性（默认就是唯一）
    """
    email = models.EmailField(unique=True, verbose_name="邮箱地址")   # 确保唯一
    USERNAME_FIELD = 'email'   # 登录时使用 email 字段
    REQUIRED_FIELDS = []       # 创建 superuser 时不需要额外字段

    mobile = models.CharField(max_length=15, blank=True, unique=True, verbose_name="电话号码")  # blank=True表示该字段可以为空，unique=True表示该字段的值在数据库中必须唯一
    country = CountryField(
        blank_label='(select country)',  # 设置空白选项的标签
        verbose_name="国家地区",  # 设置在admin后台显示的名称
        default='US'  # 设置默认值为美国
    )

    class Meta:    # Meta类是一个特殊的类，用于定义模型的元数据，告诉Django一些关于模型的信息，比如数据库表名、在admin后台显示的名称等。
        db_table = 'user'  # 设置当前Reguser模型对象对应的数据库的表名，如果没有指定表名，则默认为子应用目录名_模型名称，例如:blog_reguser。
        verbose_name = "用户信息"  # 在admin站点中显示的名称。
        verbose_name_plural = verbose_name  # 在admin后台显示的名称复数形式，如果不指定，默认在verbose_name后加s。

    def __str__(self):
        return self.username  # 返回username，用于后台列表显示
