from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserProfile(AbstractUser):

    nickname = models.CharField("昵称",max_length=30,null=True,blank=True)
    email = models.EmailField("邮箱",max_length=100,null=True,blank=True)
    avatar = models.ImageField(upload_to="static/%Y/%m", default="image/default.png",
                              max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

