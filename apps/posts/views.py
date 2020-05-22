from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

# from .permission import IsSelfItemAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import PostSerializer,PostListSerializer,PostPublishSerializer
from .models import Post


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
        return Response(serializer.data)
