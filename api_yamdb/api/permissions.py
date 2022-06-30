from rest_framework import permissions


class ObjectReadOnly(permissions.BasePermission):
    """Базовый пермишен, разрешает только безопасные запросы к объектам.
    """
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class AuthorOrReadOnly(ObjectReadOnly):
    """
    Изменять и удалять объект может его автор, модератор или админ.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_authenticated:
            return user == obj.author or user.is_admin or user.is_moderator
        return super().has_object_permission(request, view, obj)


class AdminOnly(ObjectReadOnly):
    """Разрешает доступ к списку и объекту только пользователям с ролью admin.
    Также доступ имеют суперюзеры.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_admin

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and user.is_admin


class AdminOrReadOnly(ObjectReadOnly):
    """Разрешает доступ к списку и объекту только для чтения.
    Небезопасные запросы доступны только пользователям
    с ролью admin и суперюзерам.
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and user.is_admin
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated and user.is_admin
            or super().has_object_permission(request, view, obj)
        )
