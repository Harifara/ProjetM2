from rest_framework import permissions


class IsFinanceResponsable(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.get('role') == 'responsable_finance'
        )


class IsCoordinateur(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.get('role') == 'coordinateur'
        )


class IsFinanceResponsableOrCoordinateur(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.get('role') in ['responsable_finance', 'coordinateur']
        )


class IsFinanceResponsableOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user and
            request.user.is_authenticated and
            request.user.get('role') == 'responsable_finance'
        )
