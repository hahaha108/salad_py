from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from common.custom import ApiResponse
from rest_framework import mixins, serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework import exceptions
from drf_yasg.utils import swagger_auto_schema
from captcha.views import CaptchaStore, captcha_image
from .permission import IsSelfAuthenticated
from .serializer import UserLoginSerializer, UserIntroSerializer, UserRegisterSerializer, UserUpdateSerializer
from .models import UserProfile
import base64
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired
from django.core.mail import send_mail
from django.http import HttpResponse

# Create your views here.

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class EmailVerifyView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    ser = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 1800)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # 这时候self.request 类型为django的WSGIRequest
        if self.request.method.lower() == 'post':
            return [IsAuthenticated()]
        return []

    def get(self,request, *args, **kwargs):
        # 验证回调
        sign_token = request.query_params.get("sign_token")
        if not sign_token:
            raise exceptions.APIException("校验参数错误")
        try:
            info = self.ser.loads(sign_token)
            uid = info.get('uid')
            email = info.get('email')
            user = UserProfile.objects.get(id=uid)
            if user.email == email and user.verify == False:
                user.verify = True
                user.save()
                return HttpResponse("激活成功")
        except SignatureExpired:
            pass
        return HttpResponse("激活链接已过期！")

    def post(self, request, *args, **kwargs):
        # 邮件验证
        email = request.data.get("email",None)
        if not email:
            raise exceptions.APIException("email参数必传")
        if request.user.verify:
            raise exceptions.APIException("用户已激活")
        info = {
            'uid': request.user.id,
            'email': email
        }
        sign_token = self.ser.dumps(info).decode()
        verify_url = request._request._current_scheme_host + request.path_info + f'?sign_token={sign_token}'
        html_message = '<h1>{}，欢迎注册</h1>请点击下面链接激活您的用户<br><a href="{}" rel="external nofollow" >{}</a>'.format(
            request.user.username, verify_url, verify_url)
        try:
            send_mail('Salad邮箱验证','',settings.EMAIL_FROM,[email,],html_message=html_message)
        except:
            raise exceptions.APIException("邮件发送失败，请确认邮箱地址是否正确")
        request.user.email = email
        request.user.save()
        return ApiResponse(info,code=200, msg='ok')



class UserAvatarManageView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        '''
        用户头像上传更新 上传图片类型文件，参数名: avatar
        '''
        if request.user.id is not None:
            avatar = request.FILES.get('avatar',None)
            if not avatar:
                raise exceptions.APIException("avatar文件未指定")
            ext = avatar.name.split('.')[-1]
            if ext.lower() not in ["jpg","jpeg","png"]:
                raise exceptions.APIException("上传文件类型必须为:jpg,jpeg,png")
            request.user.avatar = avatar
            request.user.save()
            data = {
                "uid": request.user.id,
                "username": request.user.username,
                "avatar": request._request._current_scheme_host + '/media/' + str(request.user.avatar)
            }
            return ApiResponse(data, code=200, msg='ok')
        else:
            raise exceptions.APIException('用户不存在!')


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
            return ApiResponse({'token': token}, code=200, msg='ok')
        else:
            return ApiResponse(code=400, msg='用户名或密码错误')


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
                "email": request.user.email,
                "verify": request.user.verify
            }
            return ApiResponse(data, code=200, msg='ok')
        else:
            raise exceptions.APIException('用户不存在!')


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    # 用户注册、修改资料、详情页(增改查)

    queryset = UserProfile.objects.all()
    serializer_class = UserIntroSerializer
    authentication_classes = (JSONWebTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action in ('update','partial_update'):
            return UserUpdateSerializer
        return UserIntroSerializer

    def get_permissions(self):
        if self.action in ('update','partial_update'):
            return [IsSelfAuthenticated()]
        else:
            return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ApiResponse(serializer.data, code=200, msg='ok', status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ApiResponse(serializer.data, code=200, msg='ok')

class ImageCaptchaView(APIView):
    def get(self, request):
        '''
        获取图片验证码
        :param request:
        :return:
        '''
        hashkey = CaptchaStore.generate_key()
        _id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
        image = captcha_image(request, hashkey)
        # 将图片转换为base64
        image_base = base64.b64encode(image.content)
        data = {"id": _id, "image_base": image_base.decode('utf-8'), "type": "image/png", "encoding": "base64"}
        return ApiResponse(data, code=200, msg='ok', status=status.HTTP_201_CREATED)
