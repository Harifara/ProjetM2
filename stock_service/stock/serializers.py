from rest_framework import serializers
from .models import (
    Categorie, Article, Magasin, Stock, MouvementStock,
    DemandeReapprovisionnement, TransfertStock, DemandeAchat
)

# =========================
# Catégorie
# =========================
class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = "__all__"

# =========================
# Article
# =========================
class ArticleSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id", "code", "nom", "description", "unite_mesure",
            "prix_unitaire_estime", "is_active", "categorie", "categorie_id",
            "created_at", "updated_at"
        ]

# =========================
# Magasin
# =========================
class MagasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magasin
        fields = "__all__"

# =========================
# Stock
# =========================
class StockSerializer(serializers.ModelSerializer):
    # Nested serializers pour lecture seule
    article = ArticleSerializer(read_only=True)  # ⚠️ lecture seule pour GET
    magasin = MagasinSerializer(read_only=True)

    # Champs pour POST/PATCH
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), write_only=True, source='article'
    )
    magasin_id = serializers.PrimaryKeyRelatedField(
        queryset=Magasin.objects.all(), write_only=True, source='magasin'
    )

    class Meta:
        model = Stock
        fields = [
            'id',
            'article',
            'magasin',
            'quantite',
            'seuil_alerte',
            'date_peremption',
            'article_id',
            'magasin_id'
        ]
# =========================
# MouvementStock
# =========================
class MouvementStockSerializer(serializers.ModelSerializer):
    # Sérialisation read-only
    article = ArticleSerializer(read_only=True)
    magasin_source = MagasinSerializer(read_only=True)
    magasin_dest = MagasinSerializer(read_only=True)

    # Champs write_only
    article_id = serializers.UUIDField(write_only=True, required=True)
    magasin_source_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    magasin_dest_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MouvementStock
        fields = "__all__"
        read_only_fields = ("magasinier_id", "created_by")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        # Associer automatiquement
        validated_data["magasinier_id"] = user.id
        validated_data["created_by"] = user.id

        # Extraire IDs
        article_id = validated_data.pop('article_id')
        magasin_source_id = validated_data.pop('magasin_source_id', None)
        magasin_dest_id = validated_data.pop('magasin_dest_id', None)

        # ARTICLE
        try:
            validated_data['article'] = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise serializers.ValidationError({"article_id": "Article introuvable."})

        # MAGASIN SOURCE
        if magasin_source_id:
            try:
                validated_data['magasin_source'] = Magasin.objects.get(id=magasin_source_id)
            except Magasin.DoesNotExist:
                raise serializers.ValidationError({"magasin_source_id": "Magasin source introuvable."})
        else:
            validated_data['magasin_source'] = None

        # MAGASIN DEST
        if magasin_dest_id:
            try:
                validated_data['magasin_dest'] = Magasin.objects.get(id=magasin_dest_id)
            except Magasin.DoesNotExist:
                raise serializers.ValidationError({"magasin_dest_id": "Magasin destination introuvable."})
        else:
            validated_data['magasin_dest'] = None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        article_id = validated_data.pop("article_id", None)
        magasin_source_id = validated_data.pop("magasin_source_id", None)
        magasin_dest_id = validated_data.pop("magasin_dest_id", None)

        # UPDATE ARTICLE
        if article_id:
            try:
                instance.article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                raise serializers.ValidationError({"article_id": "Article introuvable."})

        # UPDATE MAGASIN SOURCE
        if magasin_source_id is not None:
            if magasin_source_id == "":
                instance.magasin_source = None
            else:
                try:
                    instance.magasin_source = Magasin.objects.get(id=magasin_source_id)
                except Magasin.DoesNotExist:
                    raise serializers.ValidationError({"magasin_source_id": "Magasin source introuvable."})

        # UPDATE MAGASIN DEST
        if magasin_dest_id is not None:
            if magasin_dest_id == "":
                instance.magasin_dest = None
            else:
                try:
                    instance.magasin_dest = Magasin.objects.get(id=magasin_dest_id)
                except Magasin.DoesNotExist:
                    raise serializers.ValidationError({"magasin_dest_id": "Magasin destination introuvable."})

        return super().update(instance, validated_data)

# =========================
# DemandeReapprovisionnement
# =========================

class DemandeReapprovisionnementSerializer(serializers.ModelSerializer):
    magasin = MagasinSerializer(read_only=True, allow_null=True)
    article = ArticleSerializer(read_only=True, allow_null=True)

    # Pour créer une demande via POST
    magasin_id = serializers.PrimaryKeyRelatedField(
        queryset=Magasin.objects.all(),
        source="magasin",
        write_only=True
    )
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        source="article",
        write_only=True
    )

    # Champ optionnel pour déclencher le traitement automatique
    traiter = serializers.BooleanField(write_only=True, default=False)

    demandeur_id = serializers.UUIDField(read_only=True)
    validateur_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = DemandeReapprovisionnement
        fields = [
            "id", "numero", "magasin", "article",
            "magasin_id", "article_id",
            "quantite_demandee", "quantite_approuvee",
            "motif", "statut", "priorite",
            "demandeur_id", "validateur_id",
            "date_validation", "commentaire_validation",
            "created_at", "updated_at",
            "traiter"
        ]
        read_only_fields = [
            "id", "numero", "quantite_approuvee",
            "statut", "date_validation",
            "created_at", "updated_at",
            "validateur_id"
        ]

    def create(self, validated_data):
        traiter = validated_data.pop("traiter", False)
        # On assigne automatiquement le demandeur connecté
        validated_data["demandeur_id"] = self.context["request"].user.id
        demande = super().create(validated_data)

        if traiter:
            # Appel du workflow automatique côté responsable stock
            responsable_stock_id = self.context["request"].user.id
            demande.traiter_demande(responsable_stock_id)

        return demande

# =========================
# TransfertStock
# =========================
class TransfertStockSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    magasin_source = MagasinSerializer(read_only=True)
    magasin_dest = MagasinSerializer(read_only=True)

    class Meta:
        model = TransfertStock
        fields = "__all__"

# =========================
# DemandeAchat
# =========================
class DemandeAchatSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    article_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = DemandeAchat
        fields = [
            'id', 'numero', 'article', 'article_id', 'quantite', 'montant_estime',
            'statut', 'demandeur_id', 'finance_valideur_id', 'justification',
            'date_validation_finance', 'commentaire_finance',
            'statut_reception', 'date_reception', 'magasin_reception_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'numero', 'statut', 'demandeur_id', 'finance_valideur_id',
            'date_validation_finance', 'commentaire_finance',
            'statut_reception', 'date_reception', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        article_id = validated_data.pop('article_id')
        article = Article.objects.get(id=article_id)
        validated_data['article'] = article
        # Assurer que le numéro est unique si pas fourni
        if 'numero' not in validated_data:
            validated_data['numero'] = f"DA-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)
