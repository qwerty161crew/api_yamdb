from typing import Any, Type

from django.views import View
from rest_framework import permissions
from rest_framework.request import Request


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(
        self: 'IsAdminOrReadOnly',
        request: Request,
        view: Type[View],
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False


class IsModerator(permissions.BasePermission):
    def has_object_permission(
        self: 'IsModerator',
        request: Request,
        view: Type[View],
        obj: Any,
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == 'moderator':
            return True


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(
        self: 'IsAuthorOrReadOnly',
        request: Request,
        view: Type[View],
        obj: Any,
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.username == obj.author:
            return True


class IsSelfOrAdmin(permissions.BasePermission):
    def has_permission(
        self: 'IsSelfOrAdmin',
        request: Request,
        view: Type[View],
    ) -> bool:
        is_staff = (
            request.user.is_authenticated and request.user.role == 'admin'
        )
        is_self = view.action == 'get_current_user'
        return is_self or is_staff

    def has_object_permission(
        self: 'IsSelfOrAdmin',
        request: Request,
        view: Type[View],
        obj: Any,
    ) -> bool:
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(
        self: 'IsOwnerOrReadOnly',
        request: Request,
        view: Type[View],
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(
        self: 'IsOwnerOrReadOnly',
        request: Request,
        view: Type[View],
        obj: Any,
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
        )
