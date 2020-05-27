from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import datetime
import os
# Create your models here.

def change_file_path(instance,filename):
    # 随机生成新的图片名，自定义路径
    ext = filename.split('.')[-1]
    filename = f'{str(uuid.uuid1())}.{ext}'
    sub_folder =  datetime.datetime.now().strftime('avatar/%Y/%m')
    return os.path.join(sub_folder,str(instance.id),  filename)

class UserProfile(AbstractUser):

    nickname = models.CharField("昵称",max_length=30,null=True,blank=True)
    email = models.EmailField("邮箱",max_length=100,null=True,blank=True)
    avatar = models.ImageField(upload_to=change_file_path, default="image/default.png",
                              max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

    def save(self,*args,**kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        if not self.nickname:
            # 分配nickname
            self.nickname = '用户'+ str(self.id)


