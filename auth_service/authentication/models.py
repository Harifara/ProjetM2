import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ============================================================
# 👤 Rôles utilisateurs
# ============================================================
class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Administrateur'
    RESPONSABLE_RH = 'responsable_rh', 'Responsable RH'
    RESPONSABLE_STOCK = 'responsable_stock', 'Responsable Stock'
    RESPONSABLE_FINANCE = 'responsable_finance', 'Responsable Finance'
    MAGASINIER = 'magasinier', 'Magasinier'
    COORDINATEUR = 'coordinateur', 'Coordinateur'


# ============================================================
# ⚙️ Gestionnaire utilisateur personnalisé
# ============================================================
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire")
        if not email:
            raise ValueError("L'email est obligatoire")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


# ============================================================
# 🧩 Modèle utilisateur (UUID)
# ============================================================
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.MAGASINIER
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        db_table = 'authentication_user'  # ✅ cohérent avec ta BDD existante
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ============================================================
# 🕵️‍♂️ Journal d’audit (UUID)
# ============================================================
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs'
    )
    action_type = models.CharField(max_length=100, help_text="Type d’action (ex: LOGIN, UPDATE, DELETE...)")
    entity_type = models.CharField(max_length=100, null=True, blank=True, help_text="Type d’entité concernée")
    entity_id = models.UUIDField(null=True, blank=True, help_text="Identifiant de l’entité concernée")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Journal d’audit'
        verbose_name_plural = 'Journaux d’audit'
        ordering = ['-timestamp']

    def __str__(self):
        user_display = self.user.username if self.user else "inconnu"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {user_display} → {self.action_type}"


# ============================================================
# 🔔 Notifications (UUID)
# ============================================================
class Notification(models.Model):
    TYPE_CHOICES = [
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('info', 'Info'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"
