from rest_framework import permissions

class IsCoordinateur(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request, 'user_role') and request.user_role == 'coordinateur'

class IsCoordinateurOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return hasattr(request, 'user_role') and request.user_role == 'coordinateur'
