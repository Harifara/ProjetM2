from django.db import models
import uuid

class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'districts'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=255)
    location = models.TextField()

    class Meta:
        db_table = 'warehouses'
        verbose_name = 'Magasin'
        verbose_name_plural = 'Magasins'

    def __str__(self):
        return f"{self.name} - {self.district.name}"


class StockCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'stock_categories'
        verbose_name = 'Catégorie de Stock'
        verbose_name_plural = 'Catégories de Stock'

    def __str__(self):
        return self.name


class StockItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_items')
    category = models.ForeignKey(StockCategory, on_delete=models.SET_NULL, null=True, related_name='stock_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)
    is_expired = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    min_threshold = models.IntegerField(default=0)
    max_threshold = models.IntegerField(default=1000)

    class Meta:
        db_table = 'stock_items'
        verbose_name = 'Article de Stock'
        verbose_name_plural = 'Articles de Stock'

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def needs_replenishment(self):
        return self.quantity < self.min_threshold


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('entrée', 'Entrée'),
        ('sortie', 'Sortie'),
        ('transfert', 'Transfert'),
    ]

    STATUS_CHOICES = [
        ('en_attente', 'En Attente'),
        ('validé', 'Validé'),
        ('rejeté', 'Rejeté'),
        ('complété', 'Complété'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_movements')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_movements')
    requested_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    document_id = models.UUIDField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'stock_movements'
        verbose_name = 'Mouvement de Stock'
        verbose_name_plural = 'Mouvements de Stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} - {self.stock_item.name} - {self.quantity}"


class InventoryCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_checks')
    checked_by = models.UUIDField()
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'inventory_checks'
        verbose_name = 'Vérification d\'Inventaire'
        verbose_name_plural = 'Vérifications d\'Inventaire'
        ordering = ['-date']

    def __str__(self):
        return f"Inventaire {self.warehouse.name} - {self.date}"


class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En Attente'),
        ('approuvé', 'Approuvé'),
        ('rejeté', 'Rejeté'),
        ('complété', 'Complété'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='transfer_requests')
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_transfer_requests')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_transfer_requests')
    quantity = models.IntegerField()
    requested_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'transfer_requests'
        verbose_name = 'Demande de Transfert'
        verbose_name_plural = 'Demandes de Transfert'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfert: {self.stock_item.name} de {self.from_warehouse.name} à {self.to_warehouse.name}"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En Attente'),
        ('validé', 'Validé'),
        ('rejeté', 'Rejeté'),
        ('traité', 'Traité'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.UUIDField()
    department = models.CharField(max_length=100, default='stock')
    item_description = models.TextField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    validated_by = models.UUIDField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'purchase_requests'
        verbose_name = 'Demande d\'Achat'
        verbose_name_plural = 'Demandes d\'Achat'
        ordering = ['-created_at']

    def __str__(self):
        return f"Achat: {self.item_description[:50]} - {self.status}"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    action_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, null=True, blank=True)
    entity_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.user_id} - {self.timestamp}"
