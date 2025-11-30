import uuid
from django.db import models
from django.utils import timezone

# ============================================================
# 👤 Profil du Coordinateur
# ============================================================
class ProfilCoordinateur(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # UUID depuis auth_service
    user_id = models.UUIDField(unique=True, help_text="UUID de l'utilisateur (depuis auth_service)")
    
    nom_complet = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    
    # Permissions/Rôles du coordinateur
    peut_valider_decaissement = models.BooleanField(default=True)
    
    # Disponibilité du coordinateur
    est_disponible = models.BooleanField(default=True)
    
    date_embauche = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profils_coordinateurs'
        verbose_name = 'Profil Coordinateur'
        verbose_name_plural = 'Profils Coordinateurs'

    def __str__(self):
        return f"{self.nom_complet} ({self.email})"

# ============================================================
# 📋 Gestion des Dossiers de Décaissement
# ============================================================
class DossierDecaissement(models.Model):
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('partiellement_approuve', 'Partiellement approuvé'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    
    # Référence vers la demande de décaissement du service finance
    demande_decaissement_id = models.UUIDField(
        help_text="UUID de la DemandeDecaissement (depuis finance_service)"
    )
    
    # Coordinateur assigné
    coordinateur = models.ForeignKey(
        ProfilCoordinateur,
        on_delete=models.PROTECT,
        related_name='dossiers_decaissement'
    )
    
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='en_attente')
    
    date_reception = models.DateTimeField(auto_now_add=True)
    date_limite_decision = models.DateTimeField(
        help_text="Date limite pour décider (généralement 3-5 jours)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dossiers_decaissement'
        verbose_name = 'Dossier de Décaissement'
        verbose_name_plural = 'Dossiers de Décaissement'
        ordering = ['-date_reception']
        indexes = [
            models.Index(fields=['coordinateur', '-date_reception']),
            models.Index(fields=['demande_decaissement_id']),
        ]

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"DOS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} - {self.statut}"

# ============================================================
# ✅ Historique des Validations
# ============================================================
class HistoriqueValidation(models.Model):
    ACTION_CHOICES = [
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('en_attente', 'En attente'),
        ('renvoi', 'Renvoi pour modifications'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    dossier_decaissement = models.ForeignKey(
        DossierDecaissement,
        on_delete=models.CASCADE,
        related_name='historique_validations'
    )
    
    coordinateur = models.ForeignKey(
        ProfilCoordinateur,
        on_delete=models.PROTECT,
        related_name='validations_effectuees'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    commentaire = models.TextField(blank=True)
    
    # Liste des éléments approuvés (pour approbation partielle)
    elements_approves = models.JSONField(default=list, help_text="Éléments approuvés par le coordinateur")
    
    raison_rejet = models.TextField(blank=True, help_text="Raison du rejet si applicable")
    
    date_validation = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historiques_validations'
        verbose_name = 'Historique de Validation'
        verbose_name_plural = 'Historiques de Validations'
        ordering = ['-date_validation']

    def __str__(self):
        return f"{self.dossier_decaissement.numero} - {self.action} - {self.date_validation.strftime('%d/%m/%Y')}"

# ============================================================
# 🔔 Notifications et Alertes
# ============================================================
class AlerteDecaissement(models.Model):
    TYPE_ALERTE_CHOICES = [
        ('date_limite', 'Date limite approchante'),
        ('montant_eleve', 'Montant élevé'),
        ('type_suspect', 'Type de décaissement suspect'),
        ('coordinateur_indisponible', 'Coordinateur indisponible'),
    ]

    SEVERITE_CHOICES = [
        ('info', 'Information'),
        ('avertissement', 'Avertissement'),
        ('critique', 'Critique'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    dossier_decaissement = models.ForeignKey(
        DossierDecaissement,
        on_delete=models.CASCADE,
        related_name='alertes'
    )
    
    type_alerte = models.CharField(max_length=50, choices=TYPE_ALERTE_CHOICES)
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='info')
    
    message = models.TextField()
    est_lue = models.BooleanField(default=False)
    notifie_finance = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    lue_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alertes_decaissements'
        verbose_name = 'Alerte de Décaissement'
        verbose_name_plural = 'Alertes de Décaissements'
        ordering = ['-created_at']

    def marquer_comme_lue(self):
        self.est_lue = True
        self.lue_le = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.type_alerte} - {self.dossier_decaissement.numero}"

# ============================================================
# 📊 Statistiques et Rapports
# ============================================================
class StatistiquesValidation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    coordinateur = models.OneToOneField(
        ProfilCoordinateur,
        on_delete=models.CASCADE,
        related_name='statistiques'
    )
    
    mois = models.IntegerField(help_text="Mois (1-12)")
    annee = models.IntegerField(help_text="Année")
    
    total_demandes_traitees = models.IntegerField(default=0)
    demandes_approuvees = models.IntegerField(default=0)
    demandes_rejetees = models.IntegerField(default=0)
    demandes_renvoyees = models.IntegerField(default=0)
    
    montant_total_demande = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_total_approuve = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    temps_moyen_traitement = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'statistiques_validations'
        verbose_name = 'Statistiques de Validation'
        verbose_name_plural = 'Statistiques de Validations'
        unique_together = [['coordinateur', 'mois', 'annee']]
        ordering = ['-annee', '-mois']

    def __str__(self):
        return f"{self.coordinateur.nom_complet} - {self.mois}/{self.annee}"

# ============================================================
# 📝 Modèles de Décision (Templates)
# ============================================================
class ModeleDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    nom = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    
    montant_min = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    type_decaissement = models.CharField(max_length=100, blank=True)
    
    decision_defaut = models.CharField(
        max_length=20,
        choices=[('approuve', 'Approuvé'), ('rejete', 'Rejeté')],
        help_text="Décision suggérée"
    )
    
    commentaire_template = models.TextField(blank=True)
    est_actif = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'modeles_decisions'
        verbose_name = 'Modèle de Décision'
        verbose_name_plural = 'Modèles de Décisions'

    def __str__(self):
        return self.nom

# ============================================================
# 📋 Vue pour Tableau de Bord
# ============================================================
class Vue_DemandesPendantes(models.Model):
    """Vue pour les demandes en attente (utiliser pour les dashboards)."""
    
    id = models.UUIDField(primary_key=True)
    dossier_numero = models.CharField(max_length=100)
    demande_numero = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    type_decaissement = models.CharField(max_length=100)
    coordinateur_nom = models.CharField(max_length=255)
    demandeur_finance_id = models.UUIDField()
    date_reception = models.DateTimeField()
    date_limite = models.DateTimeField()
    priorite = models.CharField(max_length=20)
    jours_restants = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vue_demandes_pendantes'
        verbose_name = 'Vue Demandes Pendantes'
        verbose_name_plural = 'Vue Demandes Pendantes'
