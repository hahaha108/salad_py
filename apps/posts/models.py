from django.db import models
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class Post(models.Model):
    public_title = models.CharField(max_length=60,verbose_name='文章标题')
    free_content = models.TextField(verbose_name='正文内容')
    first_shared_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=300,null=True,blank=True)
    title_image = models.ImageField(upload_to="static/%Y/%m", default="image/default.png",
                               max_length=300, null=True, blank=True)
    user = models.ForeignKey(User, null=True,on_delete=models.SET_NULL)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    admiration_count = models.PositiveIntegerField(default=0)
    wordage = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_updated_at']

    def __str__(self):
        return self.public_title

    def save(self,*args,**kwargs):
        if not self.description:
            self.description = strip_tags(self.free_content)[:108]
        if not self.wordage:
            self.wordage = len(strip_tags(self.free_content))
        super(Post, self).save(*args,**kwargs)

    def increase_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])