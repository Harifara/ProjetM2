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
    # READ
    article = ArticleSerializer(read_only=True)
    magasin_source = MagasinSerializer(read_only=True)
    magasin_dest = MagasinSerializer(read_only=True)

    # WRITE
    article_id = serializers.UUIDField(write_only=True, required=True)
    magasin_source_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    magasin_dest_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MouvementStock
        fields = "__all__"

    # ---------------------------------------------------------
    # VALIDATION GLOBALE : contraintes selon type_mouvement
    # ---------------------------------------------------------
    def validate(self, attrs):
        type_mvt = attrs.get("type_mouvement")
        src = attrs.get("magasin_source_id") or attrs.get("magasin_source")
        dst = attrs.get("magasin_dest_id") or attrs.get("magasin_dest")

        # ENTREE → dest obligatoire
        if type_mvt == "entree" and not dst:
            raise serializers.ValidationError({"magasin_dest_id": "Le magasin destination est requis pour une entrée."})

        # SORTIE → source obligatoire
        if type_mvt == "sortie" and not src:
            raise serializers.ValidationError({"magasin_source_id": "Le magasin source est requis pour une sortie."})

        # RETOUR → dest obligatoire
        if type_mvt == "retour" and not dst:
            raise serializers.ValidationError({"magasin_dest_id": "Le magasin destination est requis pour un retour."})

        # TRANSFERT → source et dest obligatoires
        if type_mvt == "transfert":
            if not src:
                raise serializers.ValidationError({"magasin_source_id": "Le magasin source est requis pour un transfert."})
            if not dst:
                raise serializers.ValidationError({"magasin_dest_id": "Le magasin destination est requis pour un transfert."})

        return attrs

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------
    def create(self, validated_data):
        article_id = validated_data.pop("article_id")
        src_id = validated_data.pop("magasin_source_id", None)
        dst_id = validated_data.pop("magasin_dest_id", None)

        # ARTICLE
        try:
            validated_data["article"] = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise serializers.ValidationError({"article_id": "Article introuvable."})

        # SOURCE
        if src_id:
            try:
                validated_data["magasin_source"] = Magasin.objects.get(id=src_id)
            except Magasin.DoesNotExist:
                raise serializers.ValidationError({"magasin_source_id": "Magasin source introuvable."})
        else:
            validated_data["magasin_source"] = None

        # DEST
        if dst_id:
            try:
                validated_data["magasin_dest"] = Magasin.objects.get(id=dst_id)
            except Magasin.DoesNotExist:
                raise serializers.ValidationError({"magasin_dest_id": "Magasin destination introuvable."})
        else:
            validated_data["magasin_dest"] = None

        return super().create(validated_data)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(self, instance, validated_data):
        article_id = validated_data.pop("article_id", None)
        src_id = validated_data.pop("magasin_source_id", None)
        dst_id = validated_data.pop("magasin_dest_id", None)

        # ARTICLE
        if article_id:
            try:
                instance.article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                raise serializers.ValidationError({"article_id": "Article introuvable."})

        # SOURCE
        if src_id is not None:
            if src_id == "" or src_id is None:
                instance.magasin_source = None
            else:
                try:
                    instance.magasin_source = Magasin.objects.get(id=src_id)
                except Magasin.DoesNotExist:
                    raise serializers.ValidationError({"magasin_source_id": "Magasin source introuvable."})

        # DESTINATION
        if dst_id is not None:
            if dst_id == "" or dst_id is None:
                instance.magasin_dest = None
            else:
                try:
                    instance.magasin_dest = Magasin.objects.get(id=dst_id)
                except Magasin.DoesNotExist:
                    raise serializers.ValidationError({"magasin_dest_id": "Magasin destination introuvable."})

        return super().update(instance, validated_data)
# =========================
# DemandeReapprovisionnement
# =========================
class DemandeReapprovisionnementSerializer(serializers.ModelSerializer):
    magasin = MagasinSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = DemandeReapprovisionnement
        fields = "__all__"

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

    class Meta:
        model = DemandeAchat
        fields = "__all__"


