from rest_framework import serializers
from .models import Post, Comment
from apps.users.serializer import UserIntroSerializer
from django.shortcuts import get_object_or_404

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
        fields= ["id","title_image","public_title","last_updated_at","description","user","views_count","likes_count","admiration_count","comment_count"]

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

class CommentPublishSerializer(serializers.ModelSerializer):
    '''
    写评论
    '''
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    post_id = serializers.IntegerField(required=True,allow_null=False)
    parent_comment_id = serializers.IntegerField(required=False)
    shared_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = Comment
        fields = ['post_id', 'user', 'parent_comment', 'comment_content','shared_at']

    def create(self, validated_data):
        if "post_id" in validated_data:
            validated_data["post"] = get_object_or_404(Post,id=validated_data["post_id"])
            del validated_data["post_id"]
        if "parent_comment_id" in validated_data:
            validated_data["parent_comment"] = get_object_or_404(Comment,id=validated_data["parent_comment_id"])
            del validated_data["parent_comment_id"]
        return super(CommentPublishSerializer, self).create(validated_data)


class CommentListSerializer(serializers.ModelSerializer):
    '''
    评论列表
    '''
    class Meta:
        model = Comment
        fields = "__all__"
        depth = 3
