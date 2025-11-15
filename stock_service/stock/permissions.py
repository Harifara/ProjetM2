# ============================================
# 📁 stock_service/permissions.py
# ============================================
from rest_framework import permissions

# ============================================================
# 🔐 Vérification de rôle utilisateur
# ============================================================
def has_role(user, roles):
    """
    Vérifie que l'utilisateur est authentifié et possède l'un des rôles spécifiés
    ou qu'il est administrateur (admin).
    """
    return bool(
        user
        and user.is_authenticated
        and (
            getattr(user, "role", None) == "admin"  # ✅ Admin a toujours accès
            or getattr(user, "role", None) in roles
        )
    )


# ============================================================
# 🧱 Permissions spécifiques au module Stock
# ============================================================

class IsResponsableStock(permissions.BasePermission):
    message = "Accès réservé aux responsables de stock."

    def has_permission(self, request, view):
        return has_role(request.user, ["responsable_stock"])


class IsMagasinier(permissions.BasePermission):
    message = "Accès réservé aux magasiniers."

    def has_permission(self, request, view):
        return has_role(request.user, ["magasinier"])


class IsResponsableStockOrMagasinier(permissions.BasePermission):
    message = "Accès réservé aux responsables de stock et magasiniers."

    def has_permission(self, request, view):
        return has_role(request.user, ["responsable_stock", "magasinier"])


class IsResponsableStockOrReadOnly(permissions.BasePermission):
    message = "Seuls les responsables de stock peuvent modifier."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return has_role(request.user, ["responsable_stock", "magasinier"])
        return has_role(request.user, ["responsable_stock"])


class CanAccessOwnMagasinOnly(permissions.BasePermission):
    message = "Vous ne pouvez accéder qu'aux données de votre magasin."

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, "role", None)

        # ✅ L’admin et le responsable stock peuvent tout voir
        if role in ["admin", "responsable_stock"]:
            return True

        # 👤 Le magasinier ne peut voir que son propre magasin
        if role == "magasinier":
            magasinier_id = getattr(user, "id", None)

            if hasattr(obj, 'magasin'):
                return str(obj.magasin.magasinier_id) == str(magasinier_id)
            if hasattr(obj, 'magasinier_id'):
                return str(obj.magasinier_id) == str(magasinier_id)

        return False


# ============================================================
# 🧩 Permission optionnelle : Admin ou Responsable de stock
# ============================================================
class IsAdminOrResponsableStock(permissions.BasePermission):
    """
    Autorise les administrateurs ou les responsables de stock.
    Utile pour certaines routes critiques.
    """
    message = "Accès réservé aux administrateurs ou responsables de stock."

    def has_permission(self, request, view):
        return has_role(request.user, ["responsable_stock"])
