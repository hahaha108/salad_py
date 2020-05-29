from apps.posts import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts',views.PostsViewSet,basename='posts')
router.register(r'comment',views.CommentViewSet,basename='comment')

urlpatterns = [
    path('v1/', include(router.urls)),
]
