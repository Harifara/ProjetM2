from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, AuditLog, Notification
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# ==============================
# 👤 Sérialiseur principal User
# ==============================
class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'role',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==============================
# 🧩 Création d’utilisateur
# ==============================
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'full_name',
            'role',
            'password',
            'password_confirm',
            'is_active',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


# ==============================
# ✏️ Mise à jour utilisateur
# ==============================
# ==============================
# ✏️ Mise à jour utilisateur
# ==============================
class UserUpdateSerializer(serializers.ModelSerializer):
    # Ajouter le mot de passe si besoin
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'role', 'is_active', 'password', 'password_confirm']

    def validate(self, attrs):
        # Vérifier si le mot de passe est modifié
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def update(self, instance, validated_data):
        # Supprimer password_confirm pour éviter erreur
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        # Mettre à jour les champs standards
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Mettre à jour le mot de passe si présent
        if password:
            instance.set_password(password)

        instance.save()
        return instance



# ==============================
# 🔐 Changement de mot de passe
# ==============================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs


# ==============================
# 🔑 Connexion (Login)
# ==============================
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte est désactivé.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Le nom d\'utilisateur et le mot de passe sont requis.')

        return attrs


# ==============================
# 🕵️‍♂️ Audit Log
# ==============================
from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    entity_id = serializers.UUIDField(read_only=True, allow_null=True)
    user_info = serializers.SerializerMethodField()
    action = serializers.CharField(source='action_type', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_info',
            'action',
            'entity_type',
            'entity_id',
            'timestamp',
            'details',
            'ip_address',
            'user_agent',
        ]
        read_only_fields = ['id', 'timestamp']

    def get_user_info(self, obj):
        user = obj.user
        if user:
            return {
                "id": str(user.id),
                "username": getattr(user, "username", None),
                "full_name": getattr(user, "full_name", None),
                "email": getattr(user, "email", None),
            }
        return None



# ==============================
# 🔔 Notifications
# ==============================
class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "title", "message", "type", "read", "created_at"]
        read_only_fields = ["id", "created_at"]


# ==============================
# 🎟️ JWT Token Personnalisé
# ==============================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # UUID doit être converti en string
        token["user_id"] = str(user.id)
        token["username"] = user.username
        token["role"] = user.role
        token["email"] = user.email
        return token
