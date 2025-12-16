from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models

from .models import (
    Article, Stock, MouvementStock, DemandeReapprovisionnement,
    TransfertStock, DemandeAchat, Categorie, Magasin
)
from .serializers import (
    ArticleSerializer, StockSerializer, DemandeReapprovisionnementSerializer,
    DemandeAchatSerializer, MouvementStockSerializer,
    CategorieSerializer, MagasinSerializer
)

@api_view(['GET'])
def dashboard_stock(request):
    """
    API pour le dashboard de gestion de stock
    - KPI : total articles, articles en rupture, demandes en attente
    - Listes : stocks, mouvements récents, demandes réappro, transferts, entrées/sorties
    """

    # ------------------
    # KPI globaux
    # ------------------
    total_articles = Article.objects.count()
    articles_rupture = Stock.objects.filter(quantite__lte=models.F('seuil_alerte')).count()
    demandes_reappro_en_attente = DemandeReapprovisionnement.objects.filter(statut='en_attente').count()
    transferts_en_attente = TransfertStock.objects.filter(statut='en_attente').count()
    demandes_achat_en_attente = DemandeAchat.objects.filter(statut='en_attente').count()

    # ------------------
    # Données pour tableaux
    # ------------------
    stocks = Stock.objects.select_related('article', 'magasin').all()[:50]
    demandes_reappro = DemandeReapprovisionnement.objects.select_related('article','magasin').all()[:50]
    demandes_achat = DemandeAchat.objects.select_related('article').all()[:50]

    # ------------------
    # Mouvements de stock
    # ------------------
    entrees_stock = MouvementStock.objects.filter(type_mouvement='entree').select_related(
        'article', 'magasin_source', 'magasin_dest'
    ).order_by('-date_mouvement')[:50]

    sorties_stock = MouvementStock.objects.filter(type_mouvement='sortie').select_related(
        'article', 'magasin_source', 'magasin_dest'
    ).order_by('-date_mouvement')[:50]

    total_entrees = MouvementStock.objects.filter(type_mouvement='entree').count()
    total_sorties = MouvementStock.objects.filter(type_mouvement='sortie').count()

    entrees_chart = [
        {"article": m.article.nom, "quantite": m.quantite, "magasin": m.magasin_dest.nom if m.magasin_dest else None}
        for m in entrees_stock
    ]

    sorties_chart = [
        {"article": m.article.nom, "quantite": m.quantite, "magasin": m.magasin_source.nom if m.magasin_source else None}
        for m in sorties_stock
    ]

    # ------------------
    # Données catégories et magasins
    # ------------------
    categories = Categorie.objects.all()
    magasins = Magasin.objects.all()

    return Response({
        "kpi": {
            "total_articles": total_articles,
            "articles_rupture": articles_rupture,
            "demandes_reappro_en_attente": demandes_reappro_en_attente,
            "transferts_en_attente": transferts_en_attente,
            "demandes_achat_en_attente": demandes_achat_en_attente,
            "total_entrees": total_entrees,
            "total_sorties": total_sorties,
        },
        "stocks": StockSerializer(stocks, many=True).data,
        "demandes_reappro": DemandeReapprovisionnementSerializer(demandes_reappro, many=True).data,
        "demandes_achat": DemandeAchatSerializer(demandes_achat, many=True).data,
        "mouvements": {
            "entrees": MouvementStockSerializer(entrees_stock, many=True).data,
            "sorties": MouvementStockSerializer(sorties_stock, many=True).data,
            "chart_entrees": entrees_chart,
            "chart_sorties": sorties_chart,
        },
        "categories": CategorieSerializer(categories, many=True).data,
        "magasins": MagasinSerializer(magasins, many=True).data,
    })
