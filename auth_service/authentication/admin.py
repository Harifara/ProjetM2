from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


# ==========================================================
# 👤 Gestion des utilisateurs dans l’interface d’administration
# ==========================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['short_id', 'username', 'email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'full_name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('email', 'full_name')}),
        ('Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Dates importantes', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'full_name',
                'role',
                'password1',
                'password2',
                'is_active',
            ),
        }),
    )

    def short_id(self, obj):
        """Affiche une version raccourcie de l’UUID."""
        return str(obj.id)[:8]
    short_id.short_description = "ID"


# ==========================================================
# 🕵️‍♂️ Gestion des journaux d’audit (lecture seule)
# ==========================================================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Affichage et filtrage des logs d’audit dans l’admin."""
    list_display = [
        'short_id',
        'action_type',
        'get_username',
        'entity_type',
        'entity_id',
        'timestamp',
        'ip_address',
    ]
    list_filter = ['action_type', 'entity_type', 'timestamp']
    search_fields = ['action_type', 'entity_type', 'entity_id', 'details']
    readonly_fields = [
        'id',
        'user',
        'action_type',
        'entity_type',
        'entity_id',
        'timestamp',
        'details',
        'ip_address',
        'user_agent',
    ]
    ordering = ['-timestamp']

    def short_id(self, obj):
        """Affiche une version courte de l’UUID."""
        return str(obj.id)[:8]
    short_id.short_description = "ID"

    def get_username(self, obj):
        """Affiche le nom complet ou le username si disponible."""
        if obj.user:
            return f"{obj.user.full_name or obj.user.username} ({obj.user.id})"
        return "—"
    get_username.short_description = "Utilisateur"

    def has_add_permission(self, request):
        """Empêche l’ajout manuel de logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Empêche la modification manuelle de logs."""
        return False
