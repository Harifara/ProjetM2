import uuid
from django.db import models

# ============================================================
# 📍 DISTRICT
# ============================================================



class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'districts'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['name']

    def __str__(self):
        return self.name

class Commune(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district = models.ForeignKey('District', on_delete=models.PROTECT, related_name='communes')  # <-- correction related_name
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'communes'
        verbose_name = 'Communes'
        verbose_name_plural = 'Communes'
        ordering = ['name']

    def __str__(self):
        return self.name

class Fokontany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commune = models.ForeignKey('Commune', on_delete=models.PROTECT, related_name='fokontanys')  # <-- correction related_name
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fokontany'
        verbose_name = 'Fokontany'
        verbose_name_plural = 'Fokontany'
        ordering = ['name']

    def __str__(self):
        return self.name


# ============================================================
# 👤 EMPLOYEE
# ============================================================
class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('on_leave', 'En congé'),
        ('suspended', 'Suspendu'),
        ('terminated', 'Terminé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    hire_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    photo_url = models.URLField(blank=True, null=True)
    cv_document_url = models.URLField(blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.PROTECT, related_name='employees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee_number} - {self.position}"


# ============================================================
# 📄 CONTRACT
# ============================================================
class Contract(models.Model):
    CONTRACT_TYPES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('stage', 'Stage'),
        ('consultant', 'Consultant'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('terminated', 'Résilié'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    document_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contracts'
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.contract_type}"


# ============================================================
# 🌴 LEAVE REQUEST
# ============================================================
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Congé Annuel'),
        ('sick', 'Congé Maladie'),
        ('maternity', 'Congé Maternité'),
        ('paternity', 'Congé Paternité'),
        ('unpaid', 'Congé Sans Solde'),
        ('other', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    validated_by = models.UUIDField(blank=True, null=True)  # ✅ UUID
    validated_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_requests'
        verbose_name = 'Demande de congé'
        verbose_name_plural = 'Demandes de congé'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.leave_type} ({self.status})"


# ============================================================
# 📦 ASSIGNMENT
# ============================================================
class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('transfer', 'Mutation'),
        ('promotion', 'Promotion'),
        ('temporary', 'Affectation Temporaire'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('completed', 'Terminé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments')
    assignment_type = models.CharField(max_length=50, choices=ASSIGNMENT_TYPES)
    new_position = models.CharField(max_length=255, blank=True, null=True)
    new_district = models.ForeignKey(District, on_delete=models.PROTECT, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField()
    validated_by = models.UUIDField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        verbose_name = 'Affectation'
        verbose_name_plural = 'Affectations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.assignment_type}"


# ============================================================
# 💰 PAYMENT REQUEST
# ============================================================
class PaymentRequest(models.Model):
    REQUEST_TYPES = [
        ('salary', 'Salaire'),
        ('bonus', 'Prime'),
        ('allowance', 'Indemnité'),
        ('reimbursement', 'Remboursement'),
        ('other', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('processing', 'En traitement'),
        ('paid', 'Payé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payment_requests', blank=True, null=True)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    requested_by = models.UUIDField()  # ✅ UUID
    validated_by = models.UUIDField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests'
        verbose_name = 'Demande de paiement'
        verbose_name_plural = 'Demandes de paiement'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} - {self.amount} ({self.status})"


# ============================================================
# 🛒 PURCHASE REQUEST
# ============================================================
class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.CharField(max_length=255, default='RH')
    item_description = models.TextField()
    quantity = models.IntegerField()
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    requested_by = models.UUIDField()  # ✅ UUID
    validated_by = models.UUIDField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_requests'
        verbose_name = "Demande d'achat"
        verbose_name_plural = "Demandes d'achat"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item_description[:50]} - {self.status}"


# ============================================================
# 🧾 AUDIT LOG
# ============================================================
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()  # ✅ UUID
    action_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, blank=True, null=True)
    entity_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'rh_audit_logs'
        verbose_name = "Journal d'audit RH"
        verbose_name_plural = "Journaux d'audit RH"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.user_id} - {self.timestamp}"
