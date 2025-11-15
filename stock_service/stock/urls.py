# ==========================================
# 📁 stock_service/urls.py
# ==========================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategorieViewSet,
    ArticleViewSet,
    MagasinViewSet,
    StockViewSet,
    MouvementStockViewSet,
    DemandeReapprovisionnementViewSet,
    TransfertStockViewSet,
    DemandeAchatViewSet,
    InventaireViewSet,
    LigneInventaireViewSet,
    ajouter_stock, retirer_stock  # endpoint personnalisé
)

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'magasins', MagasinViewSet, basename='magasin')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'mouvements-stock', MouvementStockViewSet, basename='mouvement-stock')
router.register(r'demandes-reapprovisionnement', DemandeReapprovisionnementViewSet, basename='demande-reappro')
router.register(r'demandes-achat', DemandeAchatViewSet, basename='demande-achat')
router.register(r'transferts-stock', TransfertStockViewSet, basename='transfert-stock')
router.register(r'inventaires', InventaireViewSet, basename='inventaire')
router.register(r'lignes-inventaire', LigneInventaireViewSet, basename='ligne-inventaire')

urlpatterns = [
    path('', include(router.urls)),
    # Endpoints personnalisés pour gérer les quantités
    path('stocks/<uuid:stock_id>/ajouter/', ajouter_stock, name='ajouter-stock'),
    path('stocks/<uuid:stock_id>/retirer/', retirer_stock, name='retirer-stock'),
]
