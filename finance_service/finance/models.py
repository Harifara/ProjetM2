import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# ============================================================
# 📋 Types de demande de décaissement
# ============================================================
class TypeDecaissement(models.Model):
    TYPE_CHOICES = [
        ('salaire', 'Salaire'),
        ('achat', 'Achat'),
        ('location', 'Location'),
        ('electricite', 'Électricité'),
        ('mission', 'Mission'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True)
    type_decaissement = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'types_decaissement'
        verbose_name = 'Type de Décaissement'
        verbose_name_plural = 'Types de Décaissement'
        ordering = ['nom']

    def __str__(self):
        return self.nom

# ============================================================
# 💰 Demande de Décaissement (envoyée au Coordinateur)
# ============================================================
class DemandeDecaissement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    type_decaissement = models.ForeignKey(
        TypeDecaissement, 
        on_delete=models.PROTECT, 
        related_name='demandes_decaissement'
    )
    
    # Responsable finance qui fait la demande
    demandeur_finance_id = models.UUIDField(
        help_text="UUID du responsable finance (depuis auth_service)"
    )
    
    # Coordinateur qui valide
    validateur_coordinateur_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID du coordinateur qui valide (depuis auth_service)"
    )
    
    montant_demande = models.DecimalField(max_digits=15, decimal_places=2)
    justification = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    date_demande = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_validation = models.TextField(blank=True)
    
    # Références vers entités externes (optionnel selon le type)
    demande_rh_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID de la demande RH (contrat, congé, etc.)"
    )
    demande_stock_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID de la demande d'achat (depuis stock_service)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'demandes_decaissement'
        verbose_name = 'Demande de Décaissement'
        verbose_name_plural = 'Demandes de Décaissement'
        ordering = ['-date_demande']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def approuver(self, coordinateur_id: uuid.UUID, commentaire: str = ''):
        """Approuve la demande par le coordinateur et crée une dépense."""
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée.")
        
        self.statut = 'approuve'
        self.validateur_coordinateur_id = coordinateur_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()
        
        # Création automatique de la dépense
        self._creer_depense(self.demandeur_finance_id)

    def rejeter(self, coordinateur_id: uuid.UUID, commentaire: str = ''):
        """Rejette la demande par le coordinateur."""
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée.")
        
        self.statut = 'rejete'
        self.validateur_coordinateur_id = coordinateur_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()

    def _creer_depense(self, responsable_finance_id: uuid.UUID):
        """Crée automatiquement une dépense après validation du coordinateur."""
        depense = Depense.objects.create(
            demande_decaissement=self,
            type_depense=self.type_decaissement,
            montant=self.montant_demande,
            description=self.justification,
            responsable_finance_id=responsable_finance_id,
            demande_rh_id=self.demande_rh_id,
            demande_stock_id=self.demande_stock_id,
        )
        return depense

    def __str__(self):
        return f"{self.numero} - {self.montant_demande} Ar ({self.statut})"

# ============================================================
# 💸 Dépense (créée APRÈS approbation d'une DemandeDecaissement)
# ============================================================
class Depense(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    
    # Lien vers la demande de décaissement approuvée
    demande_decaissement = models.ForeignKey(
        DemandeDecaissement,
        on_delete=models.PROTECT,
        related_name='depenses'
    )
    
    type_depense = models.ForeignKey(
        TypeDecaissement,
        on_delete=models.PROTECT,
        related_name='depenses'
    )
    
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    # Références vers entités des autres services
    employer_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID de l'employé (depuis rh_service)"
    )
    demande_rh_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID de la demande RH (depuis rh_service)"
    )
    demande_stock_id = models.UUIDField(
        null=True, 
        blank=True,
        help_text="UUID de la demande d'achat (depuis stock_service)"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    
    # Responsable finance qui gère la dépense
    responsable_finance_id = models.UUIDField(
        help_text="UUID du responsable finance (depuis auth_service)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'depenses'
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"DEP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def marquer_payee(self):
        """Marque la dépense comme payée."""
        if self.statut == 'payee':
            raise ValidationError("Cette dépense est déjà payée.")
        
        self.statut = 'payee'
        self.date_paiement = timezone.now()
        self.save()

    def annuler(self):
        """Annule la dépense."""
        if self.statut == 'payee':
            raise ValidationError("Une dépense payée ne peut pas être annulée.")
        
        self.statut = 'annulee'
        self.save()

    def __str__(self):
        return f"{self.numero} - {self.montant} Ar ({self.statut})"

# ============================================================
# 📄 Bulletin de Paie (généré à partir de dépenses salaires)
# ============================================================
class BulletinPaie(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('envoye', 'Envoyé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    
    # Référence vers l'employé (depuis rh_service)
    employer_id = models.UUIDField(help_text="UUID de l'employé (depuis rh_service)")
    
    # Référence vers la dépense associée
    depense = models.ForeignKey(
        Depense,
        on_delete=models.PROTECT,
        related_name='bulletins_paie'
    )
    
    mois = models.IntegerField(help_text="Mois du paiement (1-12)")
    annee = models.IntegerField(help_text="Année du paiement")
    
    salaire_base = models.DecimalField(max_digits=15, decimal_places=2)
    primes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    retenues = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    salaire_net = models.DecimalField(max_digits=15, decimal_places=2)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_generation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Responsable finance qui génère le bulletin
    responsable_finance_id = models.UUIDField(
        help_text="UUID du responsable finance (depuis auth_service)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bulletins_paie'
        verbose_name = 'Bulletin de Paie'
        verbose_name_plural = 'Bulletins de Paie'
        ordering = ['-annee', '-mois']
        unique_together = [['employer_id', 'mois', 'annee']]

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"BP-{self.annee}-{self.mois:02d}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calcul automatique du salaire net
        self.salaire_net = self.salaire_base + self.primes - self.retenues
        
        super().save(*args, **kwargs)

    def valider(self):
        """Valide le bulletin de paie."""
        if self.statut != 'brouillon':
            raise ValidationError("Seuls les bulletins en brouillon peuvent être validés.")
        
        self.statut = 'valide'
        self.date_validation = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.numero} - {self.mois}/{self.annee}"

# ============================================================
# 🧾 Validation des Demandes RH/Stock par Finance
# ============================================================
class ValidationDemande(models.Model):
    TYPE_DEMANDE_CHOICES = [
        ('rh', 'Demande RH'),
        ('achat_stock', 'Demande Stock'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    type_demande = models.CharField(max_length=50, choices=TYPE_DEMANDE_CHOICES)
    
    # ID de la demande dans le service d'origine
    demande_origine_id = models.UUIDField(help_text="UUID de la demande d'origine (RH ou Stock)")
    service_origine = models.CharField(max_length=50, choices=[('rh_service', 'RH'), ('stock_service', 'Stock')])
    
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    validateur_finance_id = models.UUIDField(null=True, blank=True, help_text="UUID du responsable finance")
    date_reception = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_validation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'validations_demandes'
        verbose_name = 'Validation de Demande RH/Stock'
        verbose_name_plural = 'Validations de Demandes RH/Stock'
        ordering = ['-date_reception']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"VAL-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def approuver(self, responsable_finance_id: uuid.UUID, commentaire: str = ''):
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée.")
        
        self.statut = 'approuve'
        self.validateur_finance_id = responsable_finance_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()
        
        # 🔹 Mettre à jour le service d'origine
        self._update_service_origine('approuve')

    def rejeter(self, responsable_finance_id: uuid.UUID, commentaire: str = ''):
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée.")
        
        self.statut = 'rejete'
        self.validateur_finance_id = responsable_finance_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()
        
        # 🔹 Mettre à jour le service d'origine
        self._update_service_origine('rejete')

    def _update_service_origine(self, statut_finance):
        """Synchronise le statut dans le service d'origine"""
        if self.service_origine == 'rh_service':
            from rh_service.models import Demande
            demande = Demande.objects.get(id=self.demande_origine_id)
            # Ajuster le statut selon les règles RH
            demande.status = 'approuve' if statut_finance == 'approuve' else 'refuse'
            demande.save()
        elif self.service_origine == 'stock_service':
            from stock_service.models import DemandeAchat
            demande = DemandeAchat.objects.get(id=self.demande_origine_id)
            demande.statut = 'approuve' if statut_finance == 'approuve' else 'rejete'
            demande.finance_valideur_id = self.validateur_finance_id
            demande.date_validation_finance = timezone.now()
            demande.commentaire_finance = self.commentaire_validation
            demande.save()

    def __str__(self):
        return f"{self.numero} - {self.type_demande} ({self.statut})"