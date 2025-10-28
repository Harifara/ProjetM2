from django.db import models
import uuid

class ValidationStatus(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    VALIDE = 'validé', 'Validé'
    REJETE = 'rejeté', 'Rejeté'

class RequestType(models.TextChoices):
    PURCHASE = 'purchase', 'Achat'
    PAYMENT = 'payment', 'Paiement'
    DECASHMENT = 'decashment', 'Décaissement'
    STOCK_TRANSFER = 'stock_transfer', 'Transfert de stock'

class DecashmentValidation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=50, choices=RequestType.choices)
    request_id = models.UUIDField()
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.EN_ATTENTE
    )
    validated_by = models.UUIDField(null=True, blank=True)
    validation_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    requested_by = models.UUIDField()
    department = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'decashment_validations'
        verbose_name = 'Validation de décaissement'
        verbose_name_plural = 'Validations de décaissement'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.validation_status} - {self.created_at}"

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    action_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, null=True, blank=True)
    entity_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'coordinateur_audit_logs'
        verbose_name = 'Journal d\'audit coordinateur'
        verbose_name_plural = 'Journaux d\'audit coordinateur'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.user_id} - {self.timestamp}"

class OperationView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viewed_by = models.UUIDField()
    operation_type = models.CharField(max_length=100)
    operation_id = models.UUIDField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operation_views'
        verbose_name = 'Consultation d\'opération'
        verbose_name_plural = 'Consultations d\'opérations'
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.operation_type} - {self.viewed_by} - {self.viewed_at}"
