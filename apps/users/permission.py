from rest_framework.permissions import IsAuthenticated


class IsSelfAuthenticated(IsAuthenticated):
    """
    限制普通用户只能对自己进行操作
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and (request.user.id == obj.id ))