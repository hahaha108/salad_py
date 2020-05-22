from rest_framework import serializers
from .models import UserProfile


class UserLoginSerializer(serializers.ModelSerializer):
    '''
    用户登录
    '''

    class Meta:
        model = UserProfile
        fields = ['username', 'password']


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

    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'nickname', 'email']

    def validate_username(self, username):
        if UserProfile.objects.filter(username=username):
            raise serializers.ValidationError(username + ' 账号已存在')
        return username

    def create(self, validated_data):
        # 密码存密文
        user = super(UserRegisterSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
