from django.db import models
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from lxml import etree
User = get_user_model()

# Create your models here.


class Post(models.Model):
    public_title = models.CharField(max_length=60,verbose_name='文章标题')
    free_content = models.TextField(verbose_name='正文内容')
    first_shared_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=300,null=True,blank=True)
    title_image = models.TextField(null=True, blank=True) # 暂时直接存图片原数据 data:image 后续需改成 ImageField
    user = models.ForeignKey(User, null=True,on_delete=models.SET_NULL)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    admiration_count = models.PositiveIntegerField(default=0)
    wordage = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_updated_at']

    def __str__(self):
        return self.public_title

    def save(self,*args,**kwargs):
        if not self.description:
            # 截取简介
            self.description = strip_tags(self.free_content)[:108]

        # 获取字数
        self.wordage = len(strip_tags(self.free_content))

        if not self.title_image:
            # 获取第一张图片作为封面图
            content_html = etree.HTML(self.free_content)
            first_img_src = content_html.xpath('//img[1]/@src')
            if first_img_src:
                self.title_image = first_img_src[0]
        super(Post, self).save(*args,**kwargs)

    def increase_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Comment(models.Model):
    post = models.ForeignKey(Post,null=True,blank=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True,blank=True, on_delete=models.SET_NULL)
    parent_comment = models.ForeignKey('self',null=True,blank=True,default=None, on_delete=models.CASCADE)
    comment_content = models.CharField(max_length=1024, verbose_name='评论内容')
    shared_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.PositiveIntegerField(default=0)

    def save(self,*args,**kwargs):
        self.post.comment_count += 1
        self.post.save(update_fields=['comment_count'])
        super(Comment, self).save(*args,**kwargs)

    class Meta:
        ordering = ['-shared_at']

    def __str__(self):
        return self.comment_content
