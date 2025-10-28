from rest_framework import permissions


# ==========================================================
# 🔐 Permissions personnalisées pour Auth Service
# ==========================================================

class IsAdmin(permissions.BasePermission):
    """
    ✅ Autorise uniquement les utilisateurs ayant le rôle 'admin'.
    """
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "admin"
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    ✅ Autorise :
        - les requêtes de lecture (GET, HEAD, OPTIONS) à tout utilisateur authentifié.
        - les requêtes d’écriture uniquement aux admins.
    """
    message = "Seuls les administrateurs peuvent modifier ces ressources."

    def has_permission(self, request, view):
        user = request.user

        # 🔹 Lecture : accessible à tout utilisateur connecté
        if request.method in permissions.SAFE_METHODS:
            return bool(user and user.is_authenticated)

        # 🔒 Écriture : réservée aux admins
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "admin"
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    ✅ Autorise :
        - l'accès complet à l'admin,
        - uniquement à soi-même pour les utilisateurs normaux.
    """
    message = "Vous ne pouvez modifier que vos propres informations."

    def has_permission(self, request, view):
        """
        Autorise toujours la permission de base, 
        le filtrage se fera dans has_object_permission.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # 🔓 L'admin a accès à tout
        if getattr(user, "role", None) == "admin":
            return True

        # 👤 L'utilisateur peut accéder seulement à ses propres données
        # (utile pour /api/auth/users/{id}/ par exemple)
        return obj == user
