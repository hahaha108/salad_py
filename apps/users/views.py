from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .permission import IsSelfAuthenticated
from .serializer import UserLoginSerializer, UserIntroSerializer, UserRegisterSerializer
from .models import UserProfile

# Create your views here.

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserAuthView(APIView):

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request, *args, **kwargs):
        '''
        用户登录
        '''
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.token = token
            return Response({'message': 'ok',
                             'token': token}, status=200)
        else:
            return Response({ 'message': '用户名或密码错误!', }, status=400)


class UserInfoView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        '''
        获取当前用户信息
        '''
        if request.user.id is not None:
            data = {
                "id": request.user.id,
                "username": request.user.username,
                "nickname": request.user.nickname,
                "avatar": request._request._current_scheme_host + '/media/' + str(request.user.avatar),
                "email": request.user.email
            }
            return Response(data, status=200)
        else:
            return Response({'message': '请登录后访问!', }, status=400)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    # 用户管理(增改查)

    queryset = UserProfile.objects.all()
    serializer_class = UserIntroSerializer
    authentication_classes = (JSONWebTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserIntroSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        else:
            return [IsSelfAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
