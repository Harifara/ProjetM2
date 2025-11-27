# ==========================================
# 📁 stock_service/views.py
# ==========================================
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
import uuid
import logging







from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from .models import (
    Categorie, Article, Magasin, Stock, MouvementStock,
    DemandeReapprovisionnement, TransfertStock, DemandeAchat
)

from .serializers import (
    CategorieSerializer, ArticleSerializer, MagasinSerializer, StockSerializer,
    MouvementStockSerializer, DemandeReapprovisionnementSerializer, TransfertStockSerializer,
    DemandeAchatSerializer
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

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # ✅ Magasinier : ne voit que son magasin
        if getattr(user, "role", None) == "magasinier" and user.magasin_id:
            qs = qs.filter(magasin_id=user.magasin_id)
        # Responsable stock et admin voient tout
        return qs

    
    
# =========================
# MouvementStock
# =========================
class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [IsAuthenticated, IsResponsableStockOrMagasinier]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['article__nom', 'magasin_source__nom', 'magasin_dest__nom']
    ordering_fields = ['date_mouvement', 'quantite', 'type_mouvement']
    ordering = ['-date_mouvement']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if hasattr(user, 'magasin_id'):
            queryset = queryset.filter(
                models.Q(magasin_source_id=user.magasin_id) |
                models.Q(magasin_dest_id=user.magasin_id)
            )
        return queryset

logger = logging.getLogger(__name__)

class DemandeReapprovisionnementViewSet(viewsets.ModelViewSet):
    queryset = DemandeReapprovisionnement.objects.select_related('magasin', 'article').all()
    serializer_class = DemandeReapprovisionnementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = []

    def list(self, request, *args, **kwargs):
        logger.info("[GET] Début récupération demandes")
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[GET] Nombre de demandes récupérées: {len(serializer.data)}")
            return Response(serializer.data)
        except Exception as e:
            logger.exception("[GET] Erreur récupération demandes")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        numero = f"DR-{uuid.uuid4().hex[:8].upper()}"
        demandeur_id = getattr(self.request.user, "id", None)
        logger.info(f"[POST] Création demande pour utilisateur {demandeur_id}")
        serializer.save(numero=numero, demandeur_id=demandeur_id)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """
        Workflow complet :
        1. Vérifier stock disponible dans d'autres magasins
        2. Si disponible → créer TransfertStock
        3. Sinon → créer DemandeAchat
        4. Mettre à jour statut demande
        """
        try:
            obj = self.get_object()
            responsable_id = getattr(request.user, "id", None)

            if obj.statut != 'en_attente':
                return Response({"error": "Cette demande a déjà été traitée."}, status=status.HTTP_400_BAD_REQUEST)

            # ----------------------------
            # Vérifier si l'article est disponible ailleurs
            # ----------------------------
            autres_stocks = Stock.objects.filter(
                article=obj.article,
            ).exclude(magasin=obj.magasin).filter(quantite__gte=obj.quantite_demandee)

            if autres_stocks.exists():
                # Créer un transfert depuis le premier magasin trouvé
                stock_source = autres_stocks.first()
                transfert = TransfertStock.objects.create(
                    article=obj.article,
                    magasin_source=stock_source.magasin,
                    magasin_dest=obj.magasin,
                    quantite=obj.quantite_demandee,
                    responsable_id=responsable_id,
                    commentaire=f"Transfert automatique pour demande {obj.numero}"
                )
                logger.info(f"TransfertStock créé: {transfert}")
                obj.quantite_approuvee = obj.quantite_demandee
                obj.statut = 'approuve'
                obj.validateur_id = responsable_id
                obj.date_validation = timezone.now()
                obj.save()

            else:
                # Créer une demande d'achat pour la finance
                montant_estime = obj.article.prix_unitaire_estime * obj.quantite_demandee
                demande_achat = DemandeAchat.objects.create(
                    numero=f"DA-{uuid.uuid4().hex[:8].upper()}",
                    article=obj.article,
                    quantite=obj.quantite_demandee,
                    montant_estime=montant_estime,
                    statut='en_attente',
                    demandeur_id=obj.demandeur_id,
                    justification=f"Demande automatique pour {obj.numero}"
                )
                logger.info(f"DemandeAchat créée: {demande_achat}")
                obj.statut = 'approuve'
                obj.validateur_id = responsable_id
                obj.date_validation = timezone.now()
                obj.save()

            serializer = self.get_serializer(obj)
            logger.info(f"[POST] Demande {obj.numero} validée par {responsable_id}")
            return Response(serializer.data)

        except Exception as e:
            logger.exception("[POST] Erreur validation workflow")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        """
        Rejeter la demande sans workflow automatique
        """
        try:
            obj = self.get_object()
            responsable_id = getattr(request.user, "id", None)
            commentaire = request.data.get("commentaire_validation", "")
            obj.rejeter(responsable_stock_id=responsable_id, commentaire=commentaire)
            serializer = self.get_serializer(obj)
            logger.info(f"[POST] Demande {obj.numero} rejetée par {responsable_id}")
            return Response(serializer.data)
        except Exception as e:
            logger.exception("[POST] Erreur rejet")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    """
    ViewSet pour gérer les demandes d'achat :
    - Liste (GET)
    - Création (POST)
    - Validation et rejet par la finance
    """
    queryset = DemandeAchat.objects.all()
    serializer_class = DemandeAchatSerializer
    permission_classes = [IsAuthenticated, IsResponsableStockOrMagasinier]  # exiger l'authentification
    filter_backends = []

    def list(self, request, *args, **kwargs):
        """GET /api/stock/demandes-achat/"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

    def create(self, request, *args, **kwargs):
        """Créer une nouvelle demande d'achat"""
        if not request.user or request.user.is_anonymous:
            return Response({"error": "Utilisateur non authentifié"}, status=401)

        data = request.data.copy()
        data['demandeur_id'] = str(request.user.id)
        data['numero'] = f"DA-{uuid.uuid4().hex[:8].upper()}"

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def valider_finance(self, request, pk=None):
        """Valider la demande côté finance"""
        try:
            obj = self.get_object()
            finance_id = getattr(request.user, "id", None)
            obj.valider_finance(finance_user_id=finance_id)
            obj.save()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableStock])
    def rejeter_finance(self, request, pk=None):
        """Rejeter la demande côté finance avec commentaire"""
        try:
            obj = self.get_object()
            finance_id = getattr(request.user, "id", None)
            commentaire = request.data.get("commentaire", "")
            if not commentaire:
                return Response({"error": "Le commentaire est obligatoire."}, status=400)

            obj.rejeter_finance(finance_user_id=finance_id, commentaire=commentaire)
            obj.save()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)