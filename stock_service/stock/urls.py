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
    ajouter_stock, retirer_stock  # endpoint personnalisé
)
from .dashboard_views import dashboard_stock

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'magasins', MagasinViewSet, basename='magasin')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'mouvements-stock', MouvementStockViewSet, basename='mouvement-stock')
router.register(r'demandes-reapprovisionnement', DemandeReapprovisionnementViewSet, basename='demande-reappro')
router.register(r'demandes-achat', DemandeAchatViewSet, basename='demande-achat')
router.register(r'transferts-stock', TransfertStockViewSet, basename='transfert-stock')



urlpatterns = [
    path('', include(router.urls)),
    # Endpoints personnalisés pour gérer les quantités
    path('stocks/<uuid:stock_id>/ajouter/', ajouter_stock, name='ajouter-stock'),
    path('stocks/<uuid:stock_id>/retirer/', retirer_stock, name='retirer-stock'),
    path('dashboard-stock/', dashboard_stock, name='dashboard-stock'),
]


