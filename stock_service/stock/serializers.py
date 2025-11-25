from rest_framework import serializers
from .models import (
    Categorie, Article, Magasin, Stock, MouvementStock,
    DemandeReapprovisionnement, TransfertStock, DemandeAchat,
    Inventaire, LigneInventaire
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
    # Sérialisation read-only des relations
    article = ArticleSerializer(read_only=True)
    magasin_source = MagasinSerializer(read_only=True)
    magasin_dest = MagasinSerializer(read_only=True)

    # Champs write pour accepter les IDs lors de la création ou update
    article_id = serializers.UUIDField(write_only=True, required=True)
    magasin_source_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    magasin_dest_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MouvementStock
        fields = "__all__"

    def create(self, validated_data):
        # Pop les champs write-only
        article_id = validated_data.pop('article_id')
        magasin_source_id = validated_data.pop('magasin_source_id', None)
        magasin_dest_id = validated_data.pop('magasin_dest_id', None)

        # Associer les objets ForeignKey
        from stock.models import Article, Magasin
        validated_data['article'] = Article.objects.get(id=article_id)
        validated_data['magasin_source'] = Magasin.objects.get(id=magasin_source_id) if magasin_source_id else None
        validated_data['magasin_dest'] = Magasin.objects.get(id=magasin_dest_id) if magasin_dest_id else None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Même logique que create pour update
        article_id = validated_data.pop('article_id', None)
        magasin_source_id = validated_data.pop('magasin_source_id', None)
        magasin_dest_id = validated_data.pop('magasin_dest_id', None)

        from stock.models import Article, Magasin
        if article_id:
            instance.article = Article.objects.get(id=article_id)
        if magasin_source_id is not None:
            instance.magasin_source = Magasin.objects.get(id=magasin_source_id)
        if magasin_dest_id is not None:
            instance.magasin_dest = Magasin.objects.get(id=magasin_dest_id)

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

# =========================
# LigneInventaire
# =========================
class LigneInventaireSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = LigneInventaire
        fields = "__all__"

# =========================
# Inventaire
# =========================
class InventaireSerializer(serializers.ModelSerializer):
    magasin = MagasinSerializer(read_only=True)
    lignes = LigneInventaireSerializer(many=True, read_only=True)

    class Meta:
        model = Inventaire
        fields = "__all__"
