from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role == "admin":
            return True
        return False


class IsModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == 'moderator':
            return True


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.username == obj.author:
            return True


class IsSelfOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        is_staff = is_authenticated and request.user.is_staff
        is_self = view.action == 'get_current_user'
        return is_self or is_staff

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated
        is_staff = is_authenticated and request.user.is_staff
        return is_staff
