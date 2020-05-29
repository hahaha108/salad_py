from rest_framework import mixins, viewsets, status
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
# from .permission import IsSelfItemAuthenticated
from rest_framework.permissions import IsAuthenticated
from common.custom import ApiResponse, get_object_or_None
from rest_framework import exceptions
from .serializers import PostSerializer, PostListSerializer, PostPublishSerializer, CommentPublishSerializer, CommentListSerializer
from .models import Post, Comment


# Create your views here.

class PostsPagination(PageNumberPagination):
    '''
    文章自定义分页
    '''

    # 默认每页显示的个数
    page_size = 10
    # 可以动态改变每页显示的个数
    page_size_query_param = 'page_size'
    # 页码参数
    page_query_param = 'page'
    # 最多能显示多少页
    max_page_size = 100

    def get_paginated_response(self, data):
        return ApiResponse(data, code=200, msg="ok", **OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
        ]))


class PostsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "create":
            return PostPublishSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        else:
            return []

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 阅读量增加
        instance.increase_views()

        serializer = self.get_serializer(instance)
        return ApiResponse(serializer.data, code=200, msg="ok")

    def create(self, request, *args, **kwargs):
        if not request.user.verify:
            raise exceptions.APIException("需要验证邮箱，激活后才能发布文章")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ApiResponse(serializer.data, code=200, msg="ok", status=status.HTTP_201_CREATED, headers=headers)

class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CommentPublishSerializer
    pagination_class = PostsPagination

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        user_id = self.request.query_params.get('user_id')
        if post_id:
            return Comment.objects.filter(post=post_id)
        elif user_id:
            return Comment.objects.filter(user=user_id)
        return Comment.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        return CommentPublishSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        else:
            return []