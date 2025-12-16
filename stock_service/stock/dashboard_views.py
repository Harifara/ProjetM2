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

    total_entrees = MouvementStock.objects.filter(type_mouvement='entree').count()
    total_sorties = MouvementStock.objects.filter(type_mouvement='sortie').count()

    # ------------------
    # Stocks et mouvements récents
    # ------------------
    stocks = Stock.objects.select_related('article', 'magasin').all()[:50]
    mouvements_entree = MouvementStock.objects.filter(type_mouvement='entree').select_related(
        'article', 'magasin_source', 'magasin_dest'
    ).order_by('-date_mouvement')[:50]
    mouvements_sortie = MouvementStock.objects.filter(type_mouvement='sortie').select_related(
        'article', 'magasin_source', 'magasin_dest'
    ).order_by('-date_mouvement')[:50]

    # Chart data simplifié pour frontend
    chart_entrees = [
        {"article": m.article.nom, "quantite": m.quantite, "magasin": m.magasin_dest.nom if m.magasin_dest else None}
        for m in mouvements_entree
    ]
    chart_sorties = [
        {"article": m.article.nom, "quantite": m.quantite, "magasin": m.magasin_source.nom if m.magasin_source else None}
        for m in mouvements_sortie
    ]

    # ------------------
    # Demandes de réapprovisionnement et achats
    # ------------------
    demandes_reappro = DemandeReapprovisionnement.objects.select_related('article', 'magasin').all()[:50]
    demandes_achat = DemandeAchat.objects.select_related('article').all()[:50]
    transferts = TransfertStock.objects.select_related('article', 'magasin_source', 'magasin_dest').all()[:50]

    # ------------------
    # Catégories et magasins
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
        "transferts": [
            {
                "id": t.id,
                "article": t.article.nom,
                "magasin_source": t.magasin_source.nom,
                "magasin_dest": t.magasin_dest.nom,
                "quantite": t.quantite,
                "statut": t.statut,
                "date_transfert": t.date_transfert,
                "commentaire": t.commentaire,
            } for t in transferts
        ],
        "mouvements": {
            "entrees": MouvementStockSerializer(mouvements_entree, many=True).data,
            "sorties": MouvementStockSerializer(mouvements_sortie, many=True).data,
            "chart_entrees": chart_entrees,
            "chart_sorties": chart_sorties,
        },
        "categories": CategorieSerializer(categories, many=True).data,
        "magasins": MagasinSerializer(magasins, many=True).data,
    })
