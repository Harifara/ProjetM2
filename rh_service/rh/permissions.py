from rest_framework import permissions
from .models import Employee

# ============================================================
# 🧱 BASE PERMISSIONS
# ============================================================

class IsResponsableRH(permissions.BasePermission):
    """
    Autorise uniquement les utilisateurs avec le rôle 'responsable_rh' ou 'admin'.
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.role in ['responsable_rh', 'admin']
        )


class IsResponsableRHOrReadOnly(permissions.BasePermission):
    """
    Lecture seule pour tous les utilisateurs authentifiés.
    Écriture réservée aux rôles 'responsable_rh' et 'admin'.
    """
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return user and user.is_authenticated
        return (
            user
            and user.is_authenticated
            and user.role in ['responsable_rh', 'admin']
        )


class IsAdminOrResponsableRH(IsResponsableRH):
    """Alias : même logique que IsResponsableRH."""
    pass


# ============================================================
# 👩‍💼 EMPLOYÉ OU RH / ADMIN
# ============================================================

class IsEmployeeOwnerOrResponsableRH(permissions.BasePermission):
    """
    🔒 L'employé peut accéder uniquement à ses propres objets.
    👔 Le responsable RH et l'admin ont un accès total.
    """
    def has_permission(self, request, view):
        # Tous les utilisateurs authentifiés peuvent accéder à la liste
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # RH ou Admin : accès complet
        if user.role in ['admin', 'responsable_rh']:
            return True

        # Cas 1️⃣ : l'objet est un employé
        if isinstance(obj, Employee):
            return str(obj.user_id) == str(user.id)

        # Cas 2️⃣ : l'objet a une relation avec un employé
        if hasattr(obj, 'employee') and getattr(obj.employee, 'user_id', None):
            return str(obj.employee.user_id) == str(user.id)

        # Cas 3️⃣ : l'objet contient directement un champ 'user_id'
        if hasattr(obj, 'user_id'):
            return str(obj.user_id) == str(user.id)

        return False


# ============================================================
# ✅ VALIDATION & DEMANDES SPÉCIFIQUES
# ============================================================

class CanValidateLeave(IsResponsableRH):
    """Peut valider les demandes de congé (RH ou admin)."""
    pass


class CanValidateAssignment(IsResponsableRH):
    """Peut valider les affectations (RH ou admin)."""
    pass


class CanCreatePaymentRequest(IsResponsableRH):
    """Peut créer ou valider les demandes de paiement (RH ou admin)."""
    pass
