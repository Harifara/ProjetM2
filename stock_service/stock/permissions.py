from rest_framework import permissions


class IsResponsableStock(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            hasattr(request, 'user_data') and
            request.user_data.get('role') == 'responsable_stock'
        )


class IsMagasinier(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            hasattr(request, 'user_data') and
            request.user_data.get('role') == 'magasinier'
        )


class IsStockPersonnel(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            hasattr(request, 'user_data') and
            request.user_data.get('role') in ['responsable_stock', 'magasinier']
        )


class IsResponsableStockOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user and
                hasattr(request, 'user_data') and
                request.user_data.get('role') in ['responsable_stock', 'magasinier']
            )
        return (
            request.user and
            hasattr(request, 'user_data') and
            request.user_data.get('role') == 'responsable_stock'
        )
