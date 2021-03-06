from rest_framework.response import Response
from rest_framework.serializers import Serializer
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from rest_framework.views import set_rollback
from django.shortcuts import _get_queryset

class ApiResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """
    def __init__(self, data=None, code=None, msg=None, status=200,
                 template_name=None, headers=None,
                 exception=False, content_type=None, **kwargs):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.

        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super().__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"code": code, "message": msg, "data": data}
        self.data.update(kwargs)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value


def exception_handler(exc, context):
    """
    自定义统一错误响应格式
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        status = 200
        if isinstance(exc, exceptions.AuthenticationFailed):
            # 用户校验失败状态码设置为401
            status = 401

        set_rollback()
        if isinstance(exc.detail, dict):
            for k,v in exc.detail.items():
                return ApiResponse(code=400, msg=f'{k}: {v[0]}', status=status, headers=headers)
        elif isinstance(exc.detail, list):
            pass
        else:
            return ApiResponse(code=400, msg=exc.detail, status=status, headers=headers)
        return ApiResponse(data=exc.detail, code=0, msg='ApiError', status=status, headers=headers)

    return None

def get_object_or_None(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_None() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return queryset.none()