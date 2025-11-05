from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid
import os

# ==================== Fonctions utilitaires ====================

def cv_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('cv', str(instance.employee.id), filename)

def photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('photos', str(instance.id), filename)

def payslip_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('payslips', str(instance.employee.id), filename)

# ==================== Modèles Géographiques ====================

class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

    def __str__(self):
        return f"{self.name} ({self.region})"


class Commune(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='communes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district', 'name']
        unique_together = [['name', 'district']]
        verbose_name = 'Commune'
        verbose_name_plural = 'Communes'

    def __str__(self):
        return f"{self.name} - {self.district.name}"


class Fokontany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='fokontanies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['commune', 'name']
        unique_together = [['name', 'commune']]
        verbose_name = 'Fokontany'
        verbose_name_plural = 'Fokontanies'

    def __str__(self):
        return f"{self.name} - {self.commune.name}"


# ==================== Modèles RH ====================

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'

    def __str__(self):
        return self.name


class Function(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Fonction'
        verbose_name_plural = 'Fonctions'

    def __str__(self):
        return self.name


class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CONTRACT_TYPE_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('stage', 'Stage'),
        ('alternance', 'Alternance'),
        ('freelance', 'Freelance'),
    ]
    reference = models.CharField(max_length=50, unique=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    contract_file = models.FileField(
        upload_to='contracts/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True, null=True
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'

    def __str__(self):
        return f"{self.reference} - {self.contract_type}"


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    GENDER_CHOICES = [('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')]
    STATUS_CHOICES = [('active', 'Actif'), ('inactive', 'Inactif'), ('suspended', 'Suspendu')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    photo = models.ImageField(
        upload_to=photo_upload_path,
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    fokontany = models.ForeignKey(Fokontany, on_delete=models.SET_NULL, null=True, related_name='employees')
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, related_name='employees')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='employees')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    function = models.ForeignKey(Function, on_delete=models.SET_NULL, null=True, related_name='employees')
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name='employees')
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_employees')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'

    def __str__(self):
        return f"{self.employee_number} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.fokontany:
            self.commune = self.fokontany.commune
            self.district = self.fokontany.commune.district
        elif self.commune:
            self.district = self.commune.district
        super().save(*args, **kwargs)


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ASSIGNMENT_TYPE_CHOICES = [
        ('district', 'Affectation District'),
        ('function', 'Changement Fonction'),
        ('both', 'District et Fonction'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES)
    new_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_employees')
    new_function = models.ForeignKey(Function, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_employees')
    previous_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='previously_assigned_employees')
    previous_function = models.ForeignKey(Function, on_delete=models.SET_NULL, null=True, blank=True, related_name='previously_assigned_employees')
    assignment_date = models.DateField(auto_now_add=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assignments')

    class Meta:
        ordering = ['-effective_date']
        verbose_name = 'Affectation'
        verbose_name_plural = 'Affectations'

    def __str__(self):
        return f"{self.employee} - {self.assignment_type} ({self.effective_date})"


class CV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CV_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='cvs')
    file = models.FileField(
        upload_to=cv_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    version = models.IntegerField(default=1)
    is_current = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CV_STATUS_CHOICES, default='pending')
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_cvs')
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_cvs')

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'CV'
        verbose_name_plural = 'CVs'

    def __str__(self):
        return f"CV {self.version} - {self.employee.first_name} {self.employee.last_name}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
        if self.is_current:
            CV.objects.filter(employee=self.employee, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class LeaveType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    LEAVE_TYPE_CHOICES = [
        ('vacation', 'Congé payé'),
        ('sick', 'Congé maladie'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
        ('unpaid', 'Congé sans solde'),
        ('emergency', 'Congé d\'urgence'),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    max_days_per_year = models.IntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Type de congé'
        verbose_name_plural = 'Types de congé'

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_days = models.IntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_leave_requests')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demande de congé'
        verbose_name_plural = 'Demandes de congé'

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} à {self.end_date})"


class Payslip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('generated', 'Généré'),
        ('validated', 'Validé'),
        ('paid', 'Payé'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    month = models.IntegerField()
    year = models.IntegerField()
    file = models.FileField(
        upload_to=payslip_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True, null=True
    )
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_payslips')
    validated_at = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payslips')

    class Meta:
        ordering = ['-year', '-month']
        unique_together = [['employee', 'month', 'year']]
        verbose_name = 'Bulletin de paie'
        verbose_name_plural = 'Bulletins de paie'

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"


class PaymentRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PAYMENT_TYPE_CHOICES = [
        ('salary', 'Salaire employé'),
        ('rent', 'Loyer'),
        ('lease', 'Location'),
        ('supplies', 'Fournitures'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Services'),
        ('other', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('reviewed', 'Examinée'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('paid', 'Payée'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payment_requests')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    supporting_documents = models.FileField(
        upload_to='payment_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        blank=True, null=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_payment_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payment_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demande de paiement'
        verbose_name_plural = 'Demandes de paiement'

    def __str__(self):
        return f"{self.payment_type} - {self.amount} {self.currency} ({self.status})"
