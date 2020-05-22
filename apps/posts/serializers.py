from rest_framework import serializers
from .models import Post
from apps.users.serializer import UserIntroSerializer


class PostSerializer(serializers.ModelSerializer):
    '''
    文章详情
    '''
    user = UserIntroSerializer()
    class Meta:
        model = Post
        fields = "__all__"

class PostListSerializer(serializers.ModelSerializer):
    '''
    文章列表
    '''
    user = UserIntroSerializer()
    class Meta:
        model = Post
        fields= ["id","public_title","last_updated_at","description","user","views_count","likes_count"]

class PostPublishSerializer(serializers.ModelSerializer):
    '''
    文章发表
    '''
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    first_shared_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    last_updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = Post
        fields= ["user","first_shared_at","last_updated_at","public_title","free_content","description"]