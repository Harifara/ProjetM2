from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    District, Commune, Fokontany,
    Department, Function, Contract,
    Employee, Assignment, CV,
    LeaveType, LeaveRequest,
    Payslip, PaymentRequest
)

# ==================== UTILISATEUR ====================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ==================== GEOGRAPHIE ====================

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class CommuneSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    district_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Commune
        fields = ['id', 'name', 'code', 'district', 'district_id', 'created_at', 'updated_at']


class FokontanySerializer(serializers.ModelSerializer):
    commune = CommuneSerializer(read_only=True)
    commune_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Fokontany
        fields = ['id', 'name', 'code', 'commune', 'commune_id', 'created_at', 'updated_at']


# ==================== RESSOURCES HUMAINES ====================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.CharField(write_only=True, required=False)

    fokontany = FokontanySerializer(read_only=True)
    fokontany_id = serializers.UUIDField(write_only=True, required=False)
    commune = CommuneSerializer(read_only=True)
    commune_id = serializers.UUIDField(write_only=True, required=False)
    district = DistrictSerializer(read_only=True)
    district_id = serializers.UUIDField(write_only=True, required=False)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, required=False)
    function = FunctionSerializer(read_only=True)
    function_id = serializers.UUIDField(write_only=True, required=False)
    contract = ContractSerializer(read_only=True)
    contract_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'employee_number',
            'first_name', 'last_name', 'email', 'phone', 'photo',
            'date_of_birth', 'gender', 'address',
            'fokontany', 'fokontany_id', 'commune', 'commune_id',
            'district', 'district_id', 'department', 'department_id',
            'function', 'function_id', 'contract', 'contract_id',
            'hire_date', 'status', 'salary', 'created_at', 'updated_at'
        ]

    def get_user(self, obj):
        if hasattr(obj, "user") and obj.user:
            return UserSerializer(obj.user).data
        return None

    def create(self, validated_data):
        # Extraire les ForeignKeys
        fokontany_id = validated_data.pop("fokontany_id", None)
        commune_id = validated_data.pop("commune_id", None)
        district_id = validated_data.pop("district_id", None)
        department_id = validated_data.pop("department_id", None)
        function_id = validated_data.pop("function_id", None)
        contract_id = validated_data.pop("contract_id")

        employee = Employee(**validated_data)
        if fokontany_id:
            employee.fokontany_id = fokontany_id
        if commune_id:
            employee.commune_id = commune_id
        if district_id:
            employee.district_id = district_id
        if department_id:
            employee.department_id = department_id
        if function_id:
            employee.function_id = function_id
        employee.contract_id = contract_id
        employee.save()
        return employee

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr.endswith("_id"):
                setattr(instance, attr.replace("_id", ""), value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


# ==================== AFFECTATION ====================

class AssignmentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.UUIDField(write_only=True)
    new_district = DistrictSerializer(read_only=True)
    new_district_id = serializers.UUIDField(write_only=True, required=False)
    new_function = FunctionSerializer(read_only=True)
    new_function_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Assignment
        fields = [
            'id', 'employee', 'employee_id', 'assignment_type',
            'new_district', 'new_district_id', 'new_function', 'new_function_id',
            'previous_district', 'previous_function',
            'assignment_date', 'effective_date', 'end_date',
            'reason', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]


# ==================== CV ====================

class CVSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CV
        fields = [
            'id', 'employee', 'employee_id', 'file',
            'file_name', 'file_size', 'version',
            'is_current', 'status', 'validated_by',
            'validated_at', 'validation_notes',
            'uploaded_at', 'uploaded_by'
        ]
        read_only_fields = ['file_name', 'file_size', 'uploaded_at']

    def create(self, validated_data):
        cv = super().create(validated_data)
        if cv.is_current:
            CV.objects.filter(employee=cv.employee, is_current=True).exclude(id=cv.id).update(is_current=False)
        return cv


# ==================== CONGÉS ====================

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.UUIDField(write_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_id', 'leave_type', 'leave_type_id',
            'start_date', 'end_date', 'number_of_days',
            'reason', 'status', 'approved_by', 'approved_at',
            'rejection_reason', 'created_at', 'updated_at'
        ]


# ==================== BULLETIN DE PAIE ====================

class PayslipSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Payslip
        fields = [
            'id', 'employee', 'employee_id', 'month', 'year', 'file',
            'gross_salary', 'deductions', 'net_salary', 'bonus',
            'overtime_hours', 'overtime_amount', 'status',
            'validated_by', 'validated_at', 'payment_date',
            'payment_method', 'notes', 'created_at', 'updated_at'
        ]


# ==================== DEMANDE DE PAIEMENT ====================

class PaymentRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.UUIDField(write_only=True, required=False)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentRequest
        fields = [
            'id', 'employee', 'employee_id', 'created_by',
            'payment_type', 'amount', 'currency', 'description', 'reference',
            'supporting_documents', 'status', 'reviewed_by', 'reviewed_at',
            'approved_by', 'approved_at', 'rejected_reason',
            'payment_date', 'notes', 'created_at', 'updated_at'
        ]

    def get_created_by(self, obj):
        if hasattr(obj, "created_by") and obj.created_by:
            return {
                "id": getattr(obj.created_by, "id", None),
                "username": getattr(obj.created_by, "username", None)
            }
        return None
