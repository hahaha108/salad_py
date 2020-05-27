from rest_framework import serializers
from .models import UserProfile
from captcha.views import CaptchaStore
from datetime import datetime
from rest_framework import exceptions


class UserLoginSerializer(serializers.ModelSerializer):
    '''
    用户登录
    '''

    class Meta:
        model = UserProfile
        fields = ['username', 'password']

class UserUpdateSerializer(serializers.ModelSerializer):
    '''
    用户资料自定义更新
    '''
    id = serializers.CharField(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id','nickname','email']


class UserIntroSerializer(serializers.ModelSerializer):
    '''
    用户基本信息
    '''

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'nickname', 'email', 'avatar']


class UserRegisterSerializer(serializers.ModelSerializer):
    '''
    用户注册
    '''
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True)
    captcha_code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label='验证码',
                                         error_messages={
                                             "blank": "请输入验证码",
                                             "required": "请输入验证码",
                                             "max_length": "验证码格式错误",
                                             "min_length": "验证码格式错误"
                                         },
                                         help_text="验证码")
    captcha_id = serializers.CharField(required=True, write_only=True, help_text="验证码id")

    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'nickname', 'email', 'captcha_code', 'captcha_id']

    def validate_username(self, username):
        if UserProfile.objects.filter(username=username):
            raise exceptions.APIException(username + ' 账号已存在')
        return username

    def validate_captcha_code(self, captcha_code):
        try:
            lower_captcha_code = captcha_code.lower()
        except:
            raise exceptions.APIException("验证码错误")
        rigth_code = CaptchaStore.objects.filter(
            id=self.initial_data['captcha_id']).first()
        if rigth_code and datetime.now() > rigth_code.expiration:
            raise exceptions.APIException("验证码过期")
        elif rigth_code and rigth_code.response == lower_captcha_code:
            return captcha_code
        else:
            raise exceptions.APIException("验证码错误")

    def create(self, validated_data):
        # 密码存密文
        user = super(UserRegisterSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate(self, attrs):
        # 数据库中并没有这些字段，验证完就删除掉,否则save会报错
        del attrs["captcha_code"]
        del attrs["captcha_id"]
        return attrs
