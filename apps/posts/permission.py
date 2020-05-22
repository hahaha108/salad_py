from rest_framework.permissions import IsAuthenticated


class IsSelfItemAuthenticated(IsAuthenticated):
    """
    限制用户只能对自己作品进行更新、删除操作
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and (request.user.id == obj.user.id ))