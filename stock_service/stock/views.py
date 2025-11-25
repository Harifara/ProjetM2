# ==========================================
# 📁 stock_service/views.py
# ==========================================
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from .models import (
    Categorie, Article, Magasin, Stock, MouvementStock,
    DemandeReapprovisionnement, TransfertStock, DemandeAchat,
    Inventaire, LigneInventaire
)

from .serializers import (
    CategorieSerializer, ArticleSerializer, MagasinSerializer, StockSerializer,
    MouvementStockSerializer, DemandeReapprovisionnementSerializer, TransfertStockSerializer,
    DemandeAchatSerializer, InventaireSerializer, LigneInventaireSerializer
)

from .permissions import (
    IsResponsableStock, IsMagasinier, IsResponsableStockOrMagasinier,
    IsResponsableStockOrReadOnly, CanAccessOwnMagasinOnly, IsAdminOrResponsableStock
)

@api_view(['POST'])
def ajouter_stock(request, stock_id):
    try:
        stock = Stock.objects.get(id=stock_id)
        qte = int(request.data.get('quantite', 0))
        stock.ajouter_quantite(qte)  # Assurez-vous que cette méthode existe dans le modèle Stock
        serializer = StockSerializer(stock)
        return Response(serializer.data)
    except Stock.DoesNotExist:
        return Response({"detail": "Stock non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def retirer_stock(request, stock_id):
    try:
        stock = Stock.objects.get(id=stock_id)
        qte = int(request.data.get('quantite', 0))
        stock.retirer_quantite(qte)  # Assurez-vous que cette méthode existe dans le modèle Stock
        serializer = StockSerializer(stock)
        return Response(serializer.data)
    except Stock.DoesNotExist:
        return Response({"detail": "Stock non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# =========================
# Catégories
# =========================
class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsResponsableStockOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["type_categorie", "is_active"]


# =========================
# Articles
# =========================
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsResponsableStockOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "nom", "categorie__nom"]


# =========================
# Magasins
# =========================
class MagasinViewSet(viewsets.ModelViewSet):
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    permission_classes = [IsResponsableStockOrReadOnly, CanAccessOwnMagasinOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['nom', 'adresse']
    



# =========================
# Stock
# =========================
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsResponsableStockOrMagasinier]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['article', 'magasin']

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [CanAccessOwnMagasinOnly()]
        return super().get_permissions()
    
    
# =========================
# MouvementStock
# =========================
class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [IsResponsableStockOrMagasinier]
    filter_backends = [SearchFilter, OrderingFilter]  # <-- liste obligatoire
    search_fields = ['article__nom', 'magasin_source__nom', 'magasin_dest__nom']
    ordering_fields = ['date_mouvement']


# =========================
# DemandeReapprovisionnement
# =========================
class DemandeReapprovisionnementViewSet(viewsets.ModelViewSet):
    queryset = DemandeReapprovisionnement.objects.all()
    serializer_class = DemandeReapprovisionnementSerializer
    permission_classes = [IsResponsableStockOrReadOnly]

    # 🔹 Actions personnalisées pour valider/rejeter
    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def valider(self, request, pk=None):
        obj = self.get_object()
        responsable_id = getattr(request.user, "id", None)
        obj.valider(responsable_stock_id=responsable_id)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def rejeter(self, request, pk=None):
        obj = self.get_object()
        responsable_id = getattr(request.user, "id", None)
        commentaire = request.data.get("commentaire", "")
        obj.rejeter(responsable_stock_id=responsable_id, commentaire=commentaire)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# TransfertStock
# =========================
class TransfertStockViewSet(viewsets.ModelViewSet):
    queryset = TransfertStock.objects.all()
    serializer_class = TransfertStockSerializer
    permission_classes = [IsResponsableStock]

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def effectuer(self, request, pk=None):
        obj = self.get_object()
        obj.effectuer()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# DemandeAchat
# =========================
class DemandeAchatViewSet(viewsets.ModelViewSet):
    queryset = DemandeAchat.objects.all()
    serializer_class = DemandeAchatSerializer
    permission_classes = [IsResponsableStockOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def valider_finance(self, request, pk=None):
        obj = self.get_object()
        finance_id = getattr(request.user, "id", None)
        obj.valider_finance(finance_user_id=finance_id)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def rejeter_finance(self, request, pk=None):
        obj = self.get_object()
        finance_id = getattr(request.user, "id", None)
        commentaire = request.data.get("commentaire", "")
        obj.rejeter_finance(finance_user_id=finance_id, commentaire=commentaire)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# Inventaire et LigneInventaire
# =========================
class LigneInventaireViewSet(viewsets.ModelViewSet):
    queryset = LigneInventaire.objects.all()
    serializer_class = LigneInventaireSerializer
    permission_classes = [IsResponsableStockOrMagasinier]


class InventaireViewSet(viewsets.ModelViewSet):
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
    permission_classes = [IsResponsableStockOrMagasinier]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)
        if role == "magasinier":
            return self.queryset.filter(magasin__magasinier_id=user.id)
        return self.queryset
