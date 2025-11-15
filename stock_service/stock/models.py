import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import requests


# =========================
# Catégories d'articles
# =========================
class Categorie(models.Model):
    TYPE_CATEGORIE_CHOICES = [
        ('matiere_premiere', 'Matière première'),
        ('produit_fini', 'Produit fini'),
        ('consommable', 'Consommable'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=255, unique=True)
    type_categorie = models.CharField(max_length=50, choices=TYPE_CATEGORIE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"

# =========================
# Articles
# =========================
class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unite_mesure = models.CharField(max_length=50, default='unité')
    prix_unitaire_estime = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='articles')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.nom}"

# =========================
# Magasins
# =========================
class Magasin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    adresse = models.TextField()
    district_id = models.UUIDField(help_text="ID du district (depuis service RH)")
    capacite_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "magasins"
        verbose_name = "Magasin"
        verbose_name_plural = "Magasins"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} - District: {self.district_id}"

  

    def get_district_details(self):
        """
        Récupère les infos du district depuis le RH service.
        """
        import requests
        from django.conf import settings

        if not self.district_id:
            return None

        try:
            response = requests.get(f"{settings.RH_SERVICE_URL}/api/districts/{self.district_id}/")
            if response.status_code == 200:
                return response.json()
            return {"error": "District introuvable dans rh_service"}
        except requests.exceptions.RequestException:
            return {"error": "Impossible de contacter rh_service"}

# =========================
# Stock
# =========================
class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey("Article", on_delete=models.CASCADE, related_name='stocks')
    magasin = models.ForeignKey("Magasin", on_delete=models.CASCADE, related_name='stocks')
    quantite = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=10)
    date_peremption = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stocks'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ('article', 'magasin')
        ordering = ['article', 'magasin']

    def clean(self):
        if self.article.categorie.type_categorie == 'consommable' and not self.date_peremption:
            raise ValidationError("Les consommables doivent avoir une date de péremption.")

    def __str__(self):
        return f"{self.article.nom} - {self.quantite} unités ({self.magasin.nom})"

    def ajouter_quantite(self, qte):
        if qte <= 0:
            raise ValidationError("La quantité à ajouter doit être positive.")
        self.quantite += qte
        self.save()  # Sauvegarde automatique après modification

    def retirer_quantite(self, qte):
        if qte <= 0:
            raise ValidationError("La quantité à retirer doit être positive.")
        if self.quantite < qte:
            raise ValidationError("Stock insuffisant pour retirer cette quantité.")
        self.quantite -= qte
        self.save() 


# =========================
# MouvementStock
# =========================
class MouvementStock(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('retour', 'Retour'),
        ('transfert', 'Transfert'),
        ('inventaire', 'Inventaire'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey("Article", on_delete=models.PROTECT, related_name="mouvements")
    magasin_source = models.ForeignKey(
        "Magasin", null=True, blank=True, on_delete=models.PROTECT, related_name="mouvements_sortie"
    )
    magasin_dest = models.ForeignKey(
        "Magasin", null=True, blank=True, on_delete=models.PROTECT, related_name="mouvements_entree"
    )
    quantite = models.IntegerField()
    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT_CHOICES)

    # 🔗 magasinier = utilisateur dans AUTH_SERVICE (UUID)
    magasinier_id = models.UUIDField(help_text="ID du magasinier (depuis auth_service)")

    # 🔗 recepteur (peut être un employé ou un autre magasin)
    recepteur_id = models.UUIDField(null=True, blank=True, help_text="ID du recepteur (employé ou magasin)")
    recepteur_type = models.CharField(
        max_length=50,
        choices=[
            ('employe', 'Employé (depuis RH)'),
            ('magasin', 'Magasin'),
            ('autre', 'Autre'),
        ],
        default='magasin'
    )

    transporteur = models.CharField(max_length=255, blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    date_mouvement = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "mouvements_stock"
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-date_mouvement"]

    # ============================================================
    # 💾 LOGIQUE DE SAUVEGARDE (gestion stock automatique)
    # ============================================================
    def save(self, *args, **kwargs):
        from stock.models import Stock

        if self.quantite <= 0:
            raise ValidationError("La quantité doit être positive.")

        # Vérification droits magasinier
        if self.type_mouvement == 'sortie' and self.magasin_source:
            if not self._verifier_autorisation_magasinier():
                raise ValidationError("Le magasinier n'est pas autorisé à effectuer ce mouvement dans ce magasin.")

        # Gestion du stock uniquement pour entrée, sortie et retour
        if self.type_mouvement in ['entree', 'sortie', 'retour']:
            if self.type_mouvement in ['entree', 'retour']:
                if not self.magasin_dest:
                    raise ValidationError("Entrée/Retour doit avoir un magasin destinataire.")
                stock, _ = Stock.objects.get_or_create(article=self.article, magasin=self.magasin_dest)
                stock.ajouter_quantite(self.quantite)

            elif self.type_mouvement == 'sortie':
                if not self.magasin_source:
                    raise ValidationError("Sortie doit avoir un magasin source.")
                stock = Stock.objects.filter(article=self.article, magasin=self.magasin_source).first()
                if not stock or stock.quantite < self.quantite:
                    raise ValidationError(f"Stock insuffisant dans le magasin {self.magasin_source.nom}")
                stock.retirer_quantite(self.quantite)

        # Les transferts créés par le responsable ne modifient pas le stock
        # Inventaire n'affecte pas le stock directement

        super().save(*args, **kwargs)


    # ============================================================
    # 🔍 MÉTHODES UTILITAIRES (API externes)
    # ============================================================

    def _verifier_autorisation_magasinier(self):
        """
        Vérifie via AUTH_SERVICE si le magasinier appartient au magasin_source.
        """
        try:
            response = requests.get(f"{settings.AUTH_SERVICE_URL}/api/users/{self.magasinier_id}/")
            if response.status_code != 200:
                return False
            user_data = response.json()
            return str(user_data.get("magasin_id")) == str(self.magasin_source.id)
        except requests.exceptions.RequestException:
            return False

    def get_magasinier_details(self):
        """Retourne les détails du magasinier depuis AUTH_SERVICE."""
        try:
            response = requests.get(f"{settings.AUTH_SERVICE_URL}/api/users/{self.magasinier_id}/")
            if response.status_code == 200:
                return response.json()
            return {"error": "Utilisateur introuvable"}
        except requests.exceptions.RequestException:
            return {"error": "Impossible de contacter auth_service"}

    def get_recepteur_details(self):
        """Retourne les détails du recepteur (employé ou magasin)."""
        try:
            if self.recepteur_type == 'employe':
                url = f"{settings.RH_SERVICE_URL}/api/employes/{self.recepteur_id}/"
            elif self.recepteur_type == 'magasin':
                url = f"{settings.STOCK_SERVICE_URL}/api/magasins/{self.recepteur_id}/"
            else:
                return None

            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Recepteur ({self.recepteur_type}) introuvable"}
        except requests.exceptions.RequestException:
            return {"error": "Impossible de contacter le service distant"}

    def __str__(self):
        return f"{self.type_mouvement.capitalize()} - {self.quantite} x {self.article.nom}"

# =========================
# DemandeReapprovisionnement
# =========================
class DemandeReapprovisionnement(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]
    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='demandes_reappro')
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name='demandes_reappro')
    quantite_demandee = models.IntegerField()
    quantite_approuvee = models.IntegerField(null=True, blank=True)
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')

    # 🔹 UUID du magasinier qui fait la demande
    demandeur_id = models.UUIDField(help_text="UUID du magasinier qui fait la demande")

    # 🔹 UUID du responsable stock qui valide
    validateur_id = models.UUIDField(null=True, blank=True, help_text="UUID du responsable stock qui valide la demande")

    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_validation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'demandes_reapprovisionnement'
        verbose_name = 'Demande de réapprovisionnement'
        verbose_name_plural = 'Demandes de réapprovisionnement'
        ordering = ['-created_at']

    def valider(self, responsable_stock_id: uuid.UUID):
        self.statut = 'approuve'
        self.validateur_id = responsable_stock_id
        self.date_validation = timezone.now()
        self.quantite_approuvee = self.quantite_demandee
        self.save()

    def rejeter(self, responsable_stock_id: uuid.UUID, commentaire: str = ''):
        self.statut = 'rejete'
        self.validateur_id = responsable_stock_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()

    def __str__(self):
        return f"{self.numero} - {self.article.nom} ({self.statut})"

# TransfertStock
# =========================
class TransfertStock(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('recu', 'Reçu'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name='transferts')
    magasin_source = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='transferts_sortie')
    magasin_dest = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='transferts_entree')
    quantite = models.IntegerField()
    responsable_id = models.UUIDField(help_text="UUID du responsable stock qui crée le transfert")
    date_transfert = models.DateTimeField(default=timezone.now)
    commentaire = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    class Meta:
        db_table = 'transferts_stock'
        verbose_name = 'Transfert de stock'
        verbose_name_plural = 'Transferts de stock'
        ordering = ['-date_transfert']

    def valider_reception(self, magasinier_id):
        """
        Valide l'arrivée du transfert dans le magasin destinataire.
        Met à jour le stock réel du magasin destinataire.
        """
        from stock.models import Stock

        stock_dest, _ = Stock.objects.get_or_create(article=self.article, magasin=self.magasin_dest)
        stock_dest.ajouter_quantite(self.quantite)

        self.statut = 'recu'
        self.save()

    def __str__(self):
        return f"{self.quantite} {self.article.nom}: {self.magasin_source.nom} → {self.magasin_dest.nom} ({self.statut})"


class DemandeAchat(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    RECEPTION_CHOICES = [
        ('en_attente', 'En attente'),
        ('recu', 'Reçu'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True)
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name='demandes_achat')
    quantite = models.IntegerField()
    montant_estime = models.DecimalField(max_digits=15, decimal_places=2)

    # Statut finance
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    demandeur_id = models.UUIDField(help_text="UUID du magasinier connecté")
    finance_valideur_id = models.UUIDField(null=True, blank=True, help_text="UUID du responsable finance")
    justification = models.TextField()
    date_validation_finance = models.DateTimeField(null=True, blank=True)
    commentaire_finance = models.TextField(blank=True)

    # Suivi de la réception réelle du stock
    statut_reception = models.CharField(
        max_length=20, choices=RECEPTION_CHOICES, default='en_attente'
    )
    date_reception = models.DateTimeField(null=True, blank=True)
    magasin_reception_id = models.UUIDField(null=True, blank=True, help_text="Magasin qui reçoit l'achat")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'demandes_achat'
        verbose_name = "Demande d'achat"
        verbose_name_plural = "Demandes d'achat"
        ordering = ['-created_at']

    # ------------------------
    # Méthodes Finance
    # ------------------------
    def valider_finance(self, finance_user_id: uuid.UUID):
        """Valide la demande côté finance."""
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée par la finance.")
        self.statut = 'approuve'
        self.finance_valideur_id = finance_user_id
        self.date_validation_finance = timezone.now()
        self.save()

    def rejeter_finance(self, finance_user_id: uuid.UUID, commentaire: str = ''):
        """Rejette la demande côté finance."""
        if self.statut != 'en_attente':
            raise ValidationError("Cette demande a déjà été traitée par la finance.")
        self.statut = 'rejete'
        self.finance_valideur_id = finance_user_id
        self.commentaire_finance = commentaire
        self.date_validation_finance = timezone.now()
        self.save()

    # ------------------------
    # Méthodes Magasinier
    # ------------------------
    def enregistrer_reception(self, magasin_id: uuid.UUID):
        """Enregistre la réception réelle des articles par le magasin."""
        if self.statut != 'approuve':
            raise ValidationError("La demande doit être approuvée par la finance avant réception.")
        if self.statut_reception == 'recu':
            raise ValidationError("Le stock a déjà été réceptionné.")
        # Ajouter la quantité dans le stock du magasin
        stock, _ = Stock.objects.get_or_create(article=self.article, magasin_id=magasin_id)
        stock.quantite += self.quantite
        stock.save()

        # Mettre à jour la demande
        self.statut_reception = 'recu'
        self.date_reception = timezone.now()
        self.magasin_reception_id = magasin_id
        self.save()

    def __str__(self):
        return f"{self.numero} - {self.article.nom} | Statut finance: {self.statut}, Réception: {self.statut_reception}"


class DemandeReapprovisionnement(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]
    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='demandes_reappro')
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name='demandes_reappro')
    quantite_demandee = models.IntegerField()
    quantite_approuvee = models.IntegerField(null=True, blank=True)
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')

    # 🔹 UUID des utilisateurs (auth_service)
    demandeur_id = models.UUIDField(help_text="UUID du magasinier connecté")
    validateur_id = models.UUIDField(null=True, blank=True, help_text="UUID du responsable stock")

    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_validation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'demandes_reapprovisionnement'
        verbose_name = 'Demande de réapprovisionnement'
        verbose_name_plural = 'Demandes de réapprovisionnement'
        ordering = ['-created_at']

    # 🔹 Méthodes
    def valider(self, responsable_stock_id: uuid.UUID):
        self.statut = 'approuve'
        self.validateur_id = responsable_stock_id
        self.date_validation = timezone.now()
        self.quantite_approuvee = self.quantite_demandee
        self.save()

    def rejeter(self, responsable_stock_id: uuid.UUID, commentaire: str = ''):
        self.statut = 'rejete'
        self.validateur_id = responsable_stock_id
        self.date_validation = timezone.now()
        self.commentaire_validation = commentaire
        self.save()

    def __str__(self):
        return f"{self.numero} - {self.article.nom} ({self.statut})"


# =========================
# Inventaire
# =========================
class Inventaire(models.Model):
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='inventaires')
    date_inventaire = models.DateTimeField(default=timezone.now)

    # 🔹 UUID du responsable de l’inventaire (magasinier)
    responsable_id = models.UUIDField(help_text="UUID du magasinier qui réalise l'inventaire")

    commentaire = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_cours')
    date_validation = models.DateTimeField(blank=True, null=True)

    # 🔹 UUID du valideur (responsable stock)
    valideur_id = models.UUIDField(null=True, blank=True, help_text="UUID du responsable stock qui valide l'inventaire")

    class Meta:
        db_table = 'inventaires'
        verbose_name = 'Inventaire'
        verbose_name_plural = 'Inventaires'
        ordering = ['-date_inventaire']

    # ------------------------
    # Méthode pour valider l'inventaire
    # ------------------------
    def valider(self, responsable_stock_id: uuid.UUID):
        if self.status != 'en_cours':
            raise ValidationError("Inventaire déjà validé ou rejeté.")

        # Mettre à jour le stock réel uniquement lors de la validation
        for ligne in self.lignes.all():
            stock, _ = Stock.objects.get_or_create(article=ligne.article, magasin=self.magasin)
            stock.quantite = ligne.quantite_comptée
            stock.save()
            ligne.quantite_stock = stock.quantite
            ligne.ecart = ligne.quantite_comptée - stock.quantite
            ligne.save()

        self.status = 'valide'
        self.valideur_id = responsable_stock_id
        self.date_validation = timezone.now()
        self.save()

    def rejeter(self, responsable_stock_id: uuid.UUID, commentaire: str = ''):
        if self.status != 'en_cours':
            raise ValidationError("Inventaire déjà validé ou rejeté.")
        self.status = 'rejete'
        self.valideur_id = responsable_stock_id
        self.commentaire = commentaire
        self.date_validation = timezone.now()
        self.save()

    def __str__(self):
        return f"Inventaire {self.id} - {self.magasin.nom} ({self.date_inventaire.date()})"


# =========================
# LigneInventaire
# =========================
class LigneInventaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(Article, on_delete=models.PROTECT)
    quantite_comptée = models.IntegerField()
    quantite_stock = models.IntegerField(default=0)
    ecart = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculer l'écart mais ne pas toucher au stock réel avant validation
        self.ecart = self.quantite_comptée - self.quantite_stock
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.article.nom}: compté {self.quantite_comptée}, stock {self.quantite_stock}, écart {self.ecart}"