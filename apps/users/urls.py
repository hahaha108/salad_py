from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAuthView, UserViewSet, UserInfoView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include(router.urls)),
    path('auth/login/', UserAuthView.as_view()),
    path('auth/info/', UserInfoView.as_view()),
]
