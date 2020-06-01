from rest_framework import serializers
from .models import Post, Comment
from apps.users.serializer import UserIntroSerializer, CommentUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

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
        fields = ['post_id', 'user', 'parent_comment_id', 'comment_content','shared_at']

    def create(self, validated_data):
        if "post_id" in validated_data:
            validated_data["post"] = get_object_or_404(Post,id=validated_data["post_id"])
            del validated_data["post_id"]
        if "parent_comment_id" in validated_data:
            validated_data["parent_comment"] = get_object_or_404(Comment,id=validated_data["parent_comment_id"])
            del validated_data["parent_comment_id"]
        return super(CommentPublishSerializer, self).create(validated_data)

    def validate_parent_comment_id(self,parent_comment_id):
        parent_comment = get_object_or_404(Comment, id=parent_comment_id)
        if parent_comment.post.id != int(self.initial_data["post_id"]):
            raise exceptions.APIException("错误数据！")
        return parent_comment_id



class CommentListSerializer(serializers.ModelSerializer):
    '''
    评论列表
    '''

    user = CommentUserSerializer()

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """
        # 重写build_nested_field方法，处理ModelSerializer自关联逻辑
        field_class = CommentListSerializer
        CommentListSerializer.Meta.depth -= 1
        field_kwargs = get_nested_relation_kwargs(relation_info)
        return field_class, field_kwargs

    class Meta:
        model = Comment
        fields = ["user","parent_comment","comment_content","shared_at","likes_count"]
        depth = 5 # 指定评论嵌套最大深度为5
