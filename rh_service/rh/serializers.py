from rest_framework import serializers
from .models import (
    District, Commune, Fokontany, Employee, Contract, LeaveRequest,
    Assignment, PaymentRequest, PurchaseRequest, AuditLog
)
from .utils import get_user_info


# ============================================================
# 📍 DISTRICT
# ============================================================
class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class CommuneSerializer(serializers.ModelSerializer):
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all()
    )

    class Meta:
        model = Commune
        fields = ['id', 'name', 'district', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FokontanySerializer(serializers.ModelSerializer):
    commune = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all()
    )

    class Meta:
        model = Fokontany
        fields = ['id', 'name', 'commune', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']



# ============================================================
# 👤 EMPLOYEE
# ============================================================
class EmployeeSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    user_id = serializers.UUIDField(required=False)  # ✅ UUID compatible
    user_info = serializers.SerializerMethodField()  # 🔥 Ajout

    class Meta:
        model = Employee
        fields = [
            'id', 'user_id', 'user_info',  # ✅ ajouté ici
            'employee_number', 'position', 'department',
            'hire_date', 'status', 'photo_url', 'cv_document_url',
            'district', 'district_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_info(self, obj):
        """
        🔍 Récupère les infos utilisateur depuis le service Auth.
        """
        return get_user_info(obj.user_id)

    def validate_employee_number(self, value):
        qs = Employee.objects.filter(employee_number=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Ce numéro d'employé existe déjà.")
        return value

    def validate_user_id(self, value):
        qs = Employee.objects.filter(user_id=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Cet utilisateur est déjà associé à un employé.")
        return value


# ============================================================
# 📄 CONTRACT
# ============================================================
class ContractSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'employee', 'employee_info', 'contract_type', 'start_date',
            'end_date', 'status', 'salary', 'document_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_employee_info(self, obj):
        return {
            'id': obj.employee.id,
            'employee_number': obj.employee.employee_number,
            'position': obj.employee.position
        }

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("La date de fin doit être après la date de début.")
        return data


# ============================================================
# 🌴 LEAVE REQUEST
# ============================================================
class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()
    days_requested = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_info', 'leave_type', 'start_date',
            'end_date', 'days_requested', 'reason', 'status',
            'validated_by', 'validated_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'validated_by', 'validated_at',
            'created_at', 'updated_at'
        ]

    def get_employee_info(self, obj):
        return {
            'id': obj.employee.id,
            'employee_number': obj.employee.employee_number,
            'position': obj.employee.position
        }

    def get_days_requested(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return delta.days + 1
        return 0

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("La date de fin doit être après la date de début.")
        return data


class LeaveRequestValidationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['status'] == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Une raison de rejet est requise.'
            })
        return data


# ============================================================
# 🧳 ASSIGNMENT
# ============================================================
class AssignmentSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()
    new_district_name = serializers.CharField(source='new_district.name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'employee', 'employee_info', 'assignment_type',
            'new_position', 'new_district', 'new_district_name',
            'start_date', 'end_date', 'status', 'reason',
            'validated_by', 'validated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'validated_by', 'validated_at',
            'created_at', 'updated_at'
        ]

    def get_employee_info(self, obj):
        return {
            'id': obj.employee.id,
            'employee_number': obj.employee.employee_number,
            'position': obj.employee.position,
            'district': obj.employee.district.name
        }

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("La date de fin doit être après la date de début.")
        return data


class AssignmentValidationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])


# ============================================================
# 💰 PAYMENT REQUEST
# ============================================================
class PaymentRequestSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()

    class Meta:
        model = PaymentRequest
        fields = [
            'id', 'employee', 'employee_info', 'request_type', 'amount',
            'reason', 'status', 'requested_by', 'validated_by',
            'validated_at', 'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_by', 'validated_by', 'validated_at',
            'created_at', 'updated_at'
        ]

    def get_employee_info(self, obj):
        if obj.employee:
            return {
                'id': obj.employee.id,
                'employee_number': obj.employee.employee_number,
                'position': obj.employee.position
            }
        return None


class PaymentRequestValidationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['status'] == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Une raison de rejet est requise.'
            })
        return data


# ============================================================
# 🛒 PURCHASE REQUEST
# ============================================================
class PurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'department', 'item_description', 'quantity',
            'estimated_amount', 'status', 'requested_by',
            'validated_by', 'validated_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_by', 'validated_by', 'validated_at',
            'created_at', 'updated_at'
        ]


class PurchaseRequestValidationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['status'] == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Une raison de rejet est requise.'
            })
        return data


# ============================================================
# 🧾 AUDIT LOG
# ============================================================
class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_id', 'action_type', 'entity_type',
            'entity_id', 'timestamp', 'details', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


# ============================================================
# 📊 EMPLOYEE STATS
# ============================================================
class EmployeeStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    by_department = serializers.DictField()
    by_district = serializers.DictField()
