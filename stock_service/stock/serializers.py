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
    article = ArticleSerializer(read_only=True)
    magasin_source = MagasinSerializer(read_only=True)
    magasin_dest = MagasinSerializer(read_only=True)

    article_id = serializers.UUIDField(write_only=True)
    magasin_source_id = serializers.UUIDField(write_only=True, allow_null=True, required=False)
    magasin_dest_id = serializers.UUIDField(write_only=True, allow_null=True, required=False)

    class Meta:
        model = MouvementStock
        fields = "__all__"

    # ---------------------------------------------------------
    # VALIDATION → Utilise les valeurs write_only
    # ---------------------------------------------------------
    def validate(self, attrs):
        request_data = self.initial_data

        type_mvt = request_data.get("type_mouvement")
        src = request_data.get("magasin_source_id")
        dst = request_data.get("magasin_dest_id")

        if type_mvt == "entree" and not dst:
            raise serializers.ValidationError({"magasin_dest_id": "Magasin destination requis pour une entrée."})

        if type_mvt == "sortie" and not src:
            raise serializers.ValidationError({"magasin_source_id": "Magasin source requis pour une sortie."})

        if type_mvt == "retour" and not dst:
            raise serializers.ValidationError({"magasin_dest_id": "Magasin destination requis pour un retour."})

        if type_mvt == "transfert":
            if not src:
                raise serializers.ValidationError({"magasin_source_id": "Magasin source requis pour un transfert."})
            if not dst:
                raise serializers.ValidationError({"magasin_dest_id": "Magasin destination requis pour un transfert."})

        return attrs

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------
    def create(self, validated_data):
        data = self.initial_data

        validated_data["article"] = Article.objects.get(id=data["article_id"])
        validated_data["magasin_source"] = (
            Magasin.objects.get(id=data["magasin_source_id"])
            if data.get("magasin_source_id") else None
        )
        validated_data["magasin_dest"] = (
            Magasin.objects.get(id=data["magasin_dest_id"])
            if data.get("magasin_dest_id") else None
        )

        return super().create(validated_data)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(self, instance, validated_data):
        data = self.initial_data

        if "article_id" in data:
            instance.article = Article.objects.get(id=data["article_id"])

        if "magasin_source_id" in data:
            instance.magasin_source = (
                Magasin.objects.get(id=data["magasin_source_id"])
                if data["magasin_source_id"] else None
            )

        if "magasin_dest_id" in data:
            instance.magasin_dest = (
                Magasin.objects.get(id=data["magasin_dest_id"])
                if data["magasin_dest_id"] else None
            )

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


