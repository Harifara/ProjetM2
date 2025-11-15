from rest_framework import serializers
from .models import (
    District, Commune, Fokontany, Fonction, Affectation,
    Employer, TypeConge, Conge, TypeContrat, Contrat, Location,
    Electricite, ModePayement, Demande, Payement,
    TypeAchat, Achat
)
from django.utils import timezone


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


class FonctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonction
        fields = '__all__'





from rest_framework import serializers
from .models import Employer, Fonction, District
from .serializers import FonctionSerializer, DistrictSerializer


class EmployerSerializer(serializers.ModelSerializer):
    fonction = FonctionSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    fonction_id = serializers.PrimaryKeyRelatedField(
        queryset=Fonction.objects.all(), source='fonction', write_only=True, allow_null=True, required=False
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), source='district', write_only=True, allow_null=True, required=False
    )
    photo_profil = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    cv = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = Employer
        fields = [
            'id', 'nom_employer', 'prenom_employer', 'date_naissance', 'status_employer',
            'date_entree', 'email', 'telephone', 'adresse',
            'photo_profil', 'cv', 'diplome', 'domaine_etude',
            'fonction', 'fonction_id', 'district', 'district_id',
            'created_at', 'updated_at'
        ]

    def validate_status_employer(self, value):
        if value not in dict(Employer.STATUS_CHOICES):
            raise serializers.ValidationError("Status invalide")
        return value



class AffectationSerializer(serializers.ModelSerializer):
    # Lecture
    employer = EmployerSerializer(read_only=True)
    ancienne_fonction = FonctionSerializer(read_only=True)
    ancien_district = DistrictSerializer(read_only=True)
    nouveau_fonction = FonctionSerializer(read_only=True)
    nouveau_district = DistrictSerializer(read_only=True)

    # Écriture
    employer_id = serializers.UUIDField(write_only=True)
    nouveau_fonction_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    nouveau_district_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Affectation
        fields = [
            'id',
            'employer', 'employer_id',
            'ancienne_fonction', 'ancien_district',
            'nouveau_fonction', 'nouveau_fonction_id',
            'nouveau_district', 'nouveau_district_id',
            'type_affectation', 'status_affectation',
            'date_creation_affectation', 'date_fin',
            'remarque', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'employer',
            'ancienne_fonction', 'ancien_district',
            'date_creation_affectation', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        employer_id = validated_data.pop('employer_id')
        validated_data['employer'] = Employer.objects.get(id=employer_id)

        nouveau_fonction_id = validated_data.pop('nouveau_fonction_id', None)
        nouveau_district_id = validated_data.pop('nouveau_district_id', None)

        if nouveau_fonction_id:
            validated_data['nouveau_fonction'] = Fonction.objects.get(id=nouveau_fonction_id)
        if nouveau_district_id:
            validated_data['nouveau_district'] = District.objects.get(id=nouveau_district_id)

        return Affectation.objects.create(**validated_data)


class TypeCongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeConge
        fields = ['id', 'nom', 'description', 'nombre_jours_max', 'created_at', 'updated_at']

class CongeSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    employer_id = serializers.UUIDField(write_only=True)
    type_conge = TypeCongeSerializer(read_only=True)
    type_conge_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Conge
        fields = [
            'id',
            'employer', 'employer_id',
            'type_conge', 'type_conge_id',
            'status_conge',
            'date_creation',
            'date_debut',
            'date_fin',
            'nombre_jours',
            'motif',
            'justificatif',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['nombre_jours', 'status_conge', 'created_at', 'updated_at', 'date_creation']

    def validate(self, data):
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')
        type_conge_id = data.get('type_conge_id')

        if date_debut and date_fin:
            if date_debut > date_fin:
                raise serializers.ValidationError("La date de début ne peut pas être après la date de fin.")
            if date_debut < timezone.now().date():
                raise serializers.ValidationError("La date de début ne peut pas être dans le passé.")

        # Vérification nombre de jours avec le type de congé
        if date_debut and date_fin and type_conge_id:
            nombre_jours = (date_fin - date_debut).days + 1
            from .models import TypeConge
            type_conge = TypeConge.objects.filter(id=type_conge_id).first()
            if type_conge and nombre_jours > type_conge.nombre_jours_max:
                raise serializers.ValidationError(
                    f"Le nombre de jours dépasse le maximum autorisé pour ce type de congé ({type_conge.nombre_jours_max})."
                )

        return data

    def create(self, validated_data):
        employer_id = validated_data.pop('employer_id')
        type_conge_id = validated_data.pop('type_conge_id')
        employer = Employer.objects.get(id=employer_id)
        type_conge = TypeConge.objects.get(id=type_conge_id)

        conge = Conge.objects.create(
            employer=employer,
            type_conge=type_conge,
            **validated_data
        )
        return conge

    def update(self, instance, validated_data):
        type_conge_id = validated_data.pop('type_conge_id', None)
        if type_conge_id:
            from .models import TypeConge
            instance.type_conge = TypeConge.objects.get(id=type_conge_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TypeContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeContrat
        fields = '__all__'


class ContratSerializer(serializers.ModelSerializer):
    type_contrat = TypeContratSerializer(read_only=True)
    type_contrat_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    employer = EmployerSerializer(read_only=True)
    employer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Contrat
        fields = [
            'id', 'status_contrat', 'date_debut_contrat', 'date_fin_contrat',
            'salaire', 'type_contrat', 'type_contrat_id', 'employer',
            'employer_id', 'created_at', 'updated_at'
        ]


class LocationSerializer(serializers.ModelSerializer):
    affectation = AffectationSerializer(read_only=True)
    affectation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'adresse', 'ville', 'code_postal',
            'affectation', 'affectation_id', 'created_at', 'updated_at'
        ]


class ElectriciteSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    location_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Electricite
        fields = [
            'id', 'numero_compteur', 'fournisseur',
            'location', 'location_id', 'created_at', 'updated_at'
        ]



class ModePayementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModePayement
        fields = '__all__'


class DemandeSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    employer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Demande
        fields = [
            'id', 'description', 'montant', 'status', 'date_demande',
            'employer', 'employer_id', 'created_at', 'updated_at'
        ]


class PayementSerializer(serializers.ModelSerializer):
    mode_payement = ModePayementSerializer(read_only=True)
    mode_payement_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    demande = DemandeSerializer(read_only=True)
    demande_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    electricite = ElectriciteSerializer(read_only=True)
    electricite_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Payement
        fields = [
            'id', 'montant', 'date_payement', 'status', 'reference',
            'mode_payement', 'mode_payement_id', 'demande', 'demande_id',
            'electricite', 'electricite_id',
            'created_at', 'updated_at'
        ]


class TypeAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeAchat
        fields = '__all__'


class AchatSerializer(serializers.ModelSerializer):
    type_achat = TypeAchatSerializer(read_only=True)
    type_achat_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Achat
        fields = [
            'id', 'article', 'code_achat', 'nombre', 'montant', 'date_achat',
            'type_achat', 'type_achat_id', 'created_at', 'updated_at'
        ]
