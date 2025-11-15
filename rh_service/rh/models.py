from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError



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


class Fonction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_fonction = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom_fonction']
        verbose_name = 'Fonction'
        verbose_name_plural = 'Fonctions'

    def __str__(self):
        return self.nom_fonction






class Employer(models.Model):
    STATUS_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('conge', 'En congé'),
        ('suspendu', 'Suspendu'),
    ]

    DIPLOME_CHOICES = [
        ('bacc', 'BACC'),
        ('bacc+2', 'BACC + 2'),
        ('licence', 'Licence'),
        ('master', 'Master'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_employer = models.CharField(max_length=100)
    prenom_employer = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)

    status_employer = models.CharField(max_length=20, choices=STATUS_CHOICES, default='actif')
    date_entree = models.DateField()

    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    # Nouveaux champs
    photo_profil = models.ImageField(upload_to="photos_profil/", null=True, blank=True)
    cv = models.FileField(upload_to="cv_employes/", null=True, blank=True)

    diplome = models.CharField(max_length=20, choices=DIPLOME_CHOICES, blank=True, null=True)
    domaine_etude = models.CharField(max_length=150, blank=True, null=True)

    # Relations existantes
    district = models.ForeignKey(
        'District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employes'
    )
    fonction = models.ForeignKey(
        'Fonction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employes'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom_employer', 'prenom_employer']
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'

    def __str__(self):
        return f"{self.nom_employer} {self.prenom_employer}"




import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Affectation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspendue', 'Suspendue'),
        ('terminee', 'Terminée'),
    ]

    TYPE_CHOICES = [
        ('permanente', 'Permanente'),
        ('temporaire', 'Temporaire'),
        ('mission', 'Mission'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey('Employer', on_delete=models.CASCADE, related_name='affectations')

    # Ancienne situation (avant affectation)
    ancien_district = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='anciennes_affectations'
    )
    ancienne_fonction = models.ForeignKey(
        'Fonction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='anciennes_affectations'
    )

    # Nouvelle situation (après affectation)
    nouveau_district = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='nouvelles_affectations'
    )
    nouveau_fonction = models.ForeignKey(
        'Fonction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='nouvelles_affectations'
    )

    type_affectation = models.CharField(max_length=20, choices=TYPE_CHOICES, default='permanente')
    status_affectation = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    date_creation_affectation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_creation_affectation']
        verbose_name = 'Affectation'
        verbose_name_plural = 'Affectations'

    def __str__(self):
        parts = []
        if self.nouveau_fonction:
            parts.append(self.nouveau_fonction.nom_fonction)
        if self.nouveau_district:
            parts.append(self.nouveau_district.name)
        return f"{self.employer} → {' / '.join(parts) or 'Aucune modification'}"

    def clean(self):
        if not self.employer:
            raise ValidationError("Un employé doit être sélectionné pour cette affectation.")

    def save(self, *args, **kwargs):
        # Nouvelle affectation
        if not self.pk:
            # Sauvegarde des anciennes données de l’employé
            self.ancien_district = self.employer.district if self.employer.district else None
            self.ancienne_fonction = self.employer.fonction if self.employer.fonction else None

            # Désactivation des affectations actives précédentes
            Affectation.objects.filter(
                employer=self.employer,
                status_affectation='active'
            ).update(status_affectation='inactive')

        super().save(*args, **kwargs)

        # Mise à jour des infos employé si l'affectation est active
        if self.status_affectation == 'active':
            if self.nouveau_district:
                self.employer.district = self.nouveau_district
            if self.nouveau_fonction:
                self.employer.fonction = self.nouveau_fonction
            self.employer.save()

    def verifier_fin_affectation(self):
        """Vérifie si une affectation temporaire est arrivée à échéance."""
        if (
            self.type_affectation == 'temporaire' and
            self.date_fin and
            timezone.now().date() >= self.date_fin and
            self.status_affectation == 'active'
        ):
            # Restauration de l’ancien poste
            self.employer.district = self.ancien_district
            self.employer.fonction = self.ancienne_fonction
            self.employer.save()

            # Clôture de l’affectation
            self.status_affectation = 'terminee'
            self.save(update_fields=['status_affectation'])

    @classmethod
    def verifier_toutes_les_affectations(cls):
        for affectation in cls.objects.filter(type_affectation='temporaire', status_affectation='active'):
            affectation.verifier_fin_affectation()

class TypeConge(models.Model):
    """
    Types de congés pour mieux structurer les demandes
    (ex: Congé annuel, maladie, maternité, paternité, sans solde...)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    nombre_jours_max = models.IntegerField(
        help_text="Nombre maximum de jours autorisés pour ce type de congé"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom']
        verbose_name = "Type de Congé"
        verbose_name_plural = "Types de Congés"

    def __str__(self):
        return self.nom


class Conge(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),  # Nouveau statut ajouté
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        'Employer', on_delete=models.CASCADE, related_name='conges'
    )
    type_conge = models.ForeignKey(
        'TypeConge', on_delete=models.SET_NULL, null=True, related_name='conges'
    )
    status_conge = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    nombre_jours = models.PositiveIntegerField(blank=True, null=True)
    motif = models.TextField()
    justificatif = models.FileField(
        upload_to='justificatifs_conge/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Congé'
        verbose_name_plural = 'Congés'

    def __str__(self):
        return f"Congé {self.employer} - {self.status_conge} ({self.type_conge})"

    def clean(self):
        # Vérification cohérence des dates
        if self.date_debut > self.date_fin:
            raise ValidationError("La date de début ne peut pas être après la date de fin.")
        if self.date_debut < timezone.now().date() and self.status_conge == 'en_attente':
            raise ValidationError("La date de début ne peut pas être dans le passé.")

        # Calcul automatique de la date_fin si nombre_jours fourni
        if self.date_debut and self.nombre_jours:
            self.date_fin = self.date_debut + timedelta(days=self.nombre_jours - 1)

        # Calcul automatique du nombre de jours si non renseigné
        self.nombre_jours = (self.date_fin - self.date_debut).days + 1
        if self.type_conge and self.nombre_jours > self.type_conge.nombre_jours_max:
            raise ValidationError(
                f"Le nombre de jours pour ce type de congé ne peut pas dépasser {self.type_conge.nombre_jours_max}."
            )

        # Vérification chevauchement avec d'autres congés approuvés
        chevauchements = Conge.objects.filter(
            employer=self.employer,
            status_conge='approuve',
            date_debut__lte=self.date_fin,
            date_fin__gte=self.date_debut
        )
        if self.pk:
            chevauchements = chevauchements.exclude(pk=self.pk)
        if chevauchements.exists():
            raise ValidationError("Ce congé chevauche un autre congé déjà approuvé pour cet employé.")

    def save(self, *args, **kwargs):
        self.clean()  # assure que les validations sont appliquées
        super().save(*args, **kwargs)

        # Gestion du status employé
        if self.status_conge == 'approuve':
            self.employer.status_employer = 'conge'
            self.employer.save(update_fields=['status_employer'])

        # Vérifie si le congé est terminé
        today = timezone.now().date()
        if self.status_conge == 'approuve' and self.date_fin < today:
            self.status_conge = 'termine'
            self.save(update_fields=['status_conge'])
            self.employer.status_employer = 'actif'
            self.employer.save(update_fields=['status_employer'])

class TypeContrat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom_type']
        verbose_name = 'Type de Contrat'
        verbose_name_plural = 'Types de Contrats'

    def __str__(self):
        return self.nom_type


class Contrat(models.Model):
    STATUS_CHOICES = [
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('resilie', 'Résilié'),
        ('suspendu', 'Suspendu'),
        ('termine', 'Terminé'),
    ]

    NATURE_CHOICES = [
        ('emploi', 'Contrat de travail'),
        ('prestation', 'Contrat de prestation'),
        ('mission', 'Contrat de mission'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        'Employer', on_delete=models.CASCADE, related_name='contrats'
    )
    type_contrat = models.ForeignKey(
        TypeContrat, on_delete=models.SET_NULL, null=True, related_name='contrats'
    )
    nature_contrat = models.CharField(
        max_length=20, choices=NATURE_CHOICES, default='emploi',
        help_text="Définit si c’est un contrat de travail, de mission ou de prestation"
    )
    status_contrat = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='actif'
    )
    date_debut_contrat = models.DateField()
    date_fin_contrat = models.DateField(blank=True, null=True)
    duree_jours = models.PositiveIntegerField(
        blank=True, null=True, help_text="Durée effective du contrat en jours"
    )
    salaire = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    montant_total = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text="Montant total à payer (utile pour une mission ou prestation)"
    )
    description_mission = models.TextField(
        blank=True, null=True, help_text="Détails de la mission ou de la prestation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_debut_contrat']
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'

    def __str__(self):
        type_nom = self.type_contrat.nom_type if self.type_contrat else "Type inconnu"
        return f"{self.nature_contrat.capitalize()} - {self.employer} ({type_nom})"

    def clean(self):
        # Vérifier cohérence des dates
        if self.date_fin_contrat and self.date_debut_contrat > self.date_fin_contrat:
            raise ValueError("La date de début ne peut pas être après la date de fin du contrat.")

        # Calcul automatique de la durée
        if self.date_fin_contrat:
            self.duree_jours = (self.date_fin_contrat - self.date_debut_contrat).days

        # Si mission ou prestation : vérifier la durée max du type
        if self.nature_contrat in ['mission', 'prestation'] and self.type_contrat:
            if self.type_contrat.duree_max_jours and self.duree_jours:
                if self.duree_jours > self.type_contrat.duree_max_jours:
                    raise ValueError(
                        f"La durée du contrat ({self.duree_jours} jours) dépasse la limite autorisée "
                        f"pour ce type ({self.type_contrat.duree_max_jours} jours)."
                    )

        # Vérifier chevauchement des contrats actifs uniquement pour les contrats d’emploi
        if self.nature_contrat == 'emploi':
            chevauchements = Contrat.objects.filter(
                employer=self.employer,
                status_contrat='actif',
                nature_contrat='emploi',
                date_debut_contrat__lte=self.date_fin_contrat or date.max,
                date_fin_contrat__gte=self.date_debut_contrat
            )
            if self.pk:
                chevauchements = chevauchements.exclude(pk=self.pk)
            if chevauchements.exists():
                raise ValueError("Cet employé a déjà un contrat de travail actif pendant cette période.")

    def save(self, *args, **kwargs):
        self.clean()

        # Mise à jour automatique du statut
        if self.date_fin_contrat and self.date_fin_contrat < timezone.now().date():
            self.status_contrat = 'expire'

        super().save(*args, **kwargs)
        


# -------------------- Location --------------------
class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, default='Nom par défaut') # ex: "Voiture X", "Salle de réunion"
    type_location = models.CharField(max_length=50, default='inconnu')  # voiture, matériel, bureau...
    description = models.TextField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    date_echeance = models.DateField(null=True, blank=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.type_location})"


# -------------------- Electricité --------------------
class Electricite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_compteur = models.CharField(max_length=50, unique=True)
    fournisseur = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='electricites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Compteur {self.numero_compteur}"


# -------------------- Mode de paiement --------------------
class ModePayement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mode_payement = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mode_payement


# -------------------- Paiement --------------------
class Payement(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complété'),
        ('echoue', 'Échoué'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    montant = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    date_payement = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    reference = models.CharField(max_length=100, unique=True, blank=True)
    mode_payement = models.ForeignKey(ModePayement, on_delete=models.SET_NULL, null=True, related_name='payements')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='payements')
    electricite = models.ForeignKey(Electricite, on_delete=models.SET_NULL, null=True, blank=True, related_name='payements')
    contrat = models.ForeignKey('Contrat', on_delete=models.SET_NULL, null=True, blank=True, related_name='payements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_payement']

    def __str__(self):
        return f"Paiement {self.reference} - {self.montant}"

    def clean(self):
        # Vérifier qu'au moins un élément est lié
        if not (self.location or self.electricite or self.contrat):
            raise ValidationError("Un paiement doit être lié à au moins une chose à payer (Location, Electricité ou Contrat).")

    def save(self, *args, **kwargs):
        # Calcul automatique du montant si non précisé
        if not self.montant:
            total = Decimal('0.00')
            if self.location:
                total += self.location.montant
            if self.electricite:
                total += self.electricite.montant
            if self.contrat:
                total += self.contrat.salaire  # ou autre champ correspondant
            self.montant = total

        # Référence automatique
        if not self.reference:
            self.reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)


# -------------------- TypeAchat --------------------
class TypeAchat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_achat = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom']
        verbose_name = "Type d'Achat"
        verbose_name_plural = "Types d'Achats"

    def __str__(self):
        return self.nom


# -------------------- Achat --------------------
class Achat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande = models.ForeignKey('Demande', on_delete=models.CASCADE, null=True, related_name="achats")  # Correction
    article = models.CharField(max_length=200)
    code_achat = models.CharField(max_length=50, unique=True)
    nombre = models.IntegerField(default=1)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    type_achat = models.ForeignKey(TypeAchat, on_delete=models.SET_NULL, null=True, related_name='achats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['article']  # correction: date_achat n'existe pas
        verbose_name = 'Achat'
        verbose_name_plural = 'Achats'

    def __str__(self):
        return f"{self.article} - {self.code_achat}"


# -------------------- Demande --------------------
class Demande(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('en_cours', 'En cours'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    payements = models.ManyToManyField(Payement, related_name='demandes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_demande']

    def __str__(self):
        return f"Demande {self.id} - {self.montant_total()}"

    # Calcul automatique du montant total des achats liés
    def montant_total(self):
        return sum([achat.montant * achat.nombre for achat in self.achats.all()])

    # Vérifie si tous les paiements sont complétés et met à jour le statut
    def update_status(self):
        payements = getattr(self, 'payements', [])
        if payements.exists() and all(p.status == 'complete' for p in payements.all()):
            self.status = 'approuve'
        elif payements.exists() and any(p.status == 'echoue' for p in payements.all()):
            self.status = 'refuse'
        else:
            self.status = 'en_cours'
        self.save()
