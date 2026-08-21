from django.db import models
from django.contrib.auth.models import AbstractUser

class Reguser(AbstractUser):
    """
    用户信息表，扩展了 admin.auth.user
    """
    nickname = models.CharField(max_length=32, verbose_name="nickname", default="")  # 昵称：字符串字段用空字符串表示“未填写”，避免 NULL 与空字符串两种空值并存
    # 手机号：字符串字段用空字符串表示“未填写”，避免 NULL 与空字符串两种空值并存
    mobile = models.CharField(max_length=11, blank=True, unique=True, verbose_name="mobile")  # blank=True表示该字段可以为空，unique=True表示该字段的值在数据库中必须唯一
    head_img = models.ImageField(upload_to="head_image/", blank=True, verbose_name="head_img")

    class Meta:    # Meta类是一个特殊的类，用于定义模型的元数据，告诉Django一些关于模型的信息，比如数据库表名、在admin后台显示的名称等。
        db_table = 'user'  # 设置当前Reguser模型对象对应的数据库的表名，如果没有指定表名，则默认为子应用目录名_模型名称，例如:blog_reguser。
        verbose_name = "User_info"  # 在admin站点中显示的名称。
        verbose_name_plural = verbose_name  # 在admin后台显示的名称复数形式，如果不指定，默认在verbose_name后加s。

    def __str__(self):
        return self.username  # 返回username，用于后台列表显示
