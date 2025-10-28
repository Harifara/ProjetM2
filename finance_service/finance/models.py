from django.db import models
import uuid


class DecashmentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté'),
        ('processing', 'En traitement'),
        ('completed', 'Complété'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.UUIDField()
    source_service = models.CharField(max_length=50, choices=[
        ('rh', 'RH'),
        ('stock', 'Stock'),
        ('finance', 'Finance'),
    ])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    related_request_type = models.CharField(max_length=50, blank=True, null=True)
    related_request_id = models.UUIDField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    validated_by = models.UUIDField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'decashment_requests'
        verbose_name = 'Demande de décaissement'
        verbose_name_plural = 'Demandes de décaissement'
        ordering = ['-created_at']

    def __str__(self):
        return f"Décaissement {self.amount} - {self.status}"


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('bulletin_paie', 'Bulletin de paie'),
        ('facture', 'Facture'),
        ('bon_entree', "Bon d'entrée"),
        ('bon_sortie', 'Bon de sortie'),
        ('recu_paiement', 'Reçu de paiement'),
        ('ordre_virement', "Ordre de virement"),
        ('autre', 'Autre'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file_url = models.URLField()
    file_name = models.CharField(max_length=255)
    related_entity_type = models.CharField(max_length=100, blank=True, null=True)
    related_entity_id = models.UUIDField(blank=True, null=True)
    uploaded_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document_type} - {self.file_name}"


class Expense(models.Model):
    EXPENSE_TYPES = [
        ('achat_stock', 'Achat Stock'),
        ('salaire', 'Salaire'),
        ('prime', 'Prime'),
        ('indemnite', 'Indemnité'),
        ('loyer', 'Loyer'),
        ('carburant', 'Carburant'),
        ('transport', 'Transport'),
        ('fourniture', 'Fourniture'),
        ('maintenance', 'Maintenance'),
        ('autre', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('paid', 'Payé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    description = models.TextField()
    related_request_id = models.UUIDField(blank=True, null=True)
    decashment_request = models.ForeignKey(
        DecashmentRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    requested_by = models.UUIDField()
    approved_by = models.UUIDField(blank=True, null=True)
    executed_by = models.UUIDField(blank=True, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_paid = models.DateTimeField(blank=True, null=True)
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'expenses'
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date_requested']

    def __str__(self):
        return f"{self.expense_type} - {self.amount} - {self.status}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('check', 'Chèque'),
        ('mobile_money', 'Mobile Money'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_name = models.CharField(max_length=255)
    recipient_account = models.CharField(max_length=255, blank=True, null=True)
    reference_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    executed_by = models.UUIDField()
    executed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-executed_at']

    def __str__(self):
        return f"Paiement {self.amount} - {self.payment_method} - {self.status}"


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.CharField(max_length=100, choices=[
        ('rh', 'RH'),
        ('stock', 'Stock'),
        ('finance', 'Finance'),
        ('general', 'Général'),
    ])
    category = models.CharField(max_length=100)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fiscal_year = models.IntegerField()
    month = models.IntegerField(blank=True, null=True)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-fiscal_year', '-month']
        unique_together = ['department', 'category', 'fiscal_year', 'month']

    def __str__(self):
        return f"Budget {self.department} - {self.category} ({self.fiscal_year})"

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount

    @property
    def utilization_percentage(self):
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return 0


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_id = models.UUIDField()
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    related_entity_type = models.CharField(max_length=100, blank=True, null=True)
    related_entity_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.recipient_id} - {self.notification_type}"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    action_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, blank=True, null=True)
    entity_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'finance_audit_logs'
        verbose_name = "Journal d'audit Finance"
        verbose_name_plural = "Journaux d'audit Finance"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.user_id} - {self.timestamp}"
