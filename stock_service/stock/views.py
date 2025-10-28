from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, F
from .models import (
    District, Warehouse, StockCategory, StockItem, StockMovement,
    InventoryCheck, TransferRequest, PurchaseRequest, AuditLog
)
from .serializers import (
    DistrictSerializer, WarehouseSerializer, StockCategorySerializer,
    StockItemSerializer, StockMovementSerializer, StockMovementCreateSerializer,
    InventoryCheckSerializer, TransferRequestSerializer, TransferRequestCreateSerializer,
    PurchaseRequestSerializer, PurchaseRequestCreateSerializer, AuditLogSerializer
)
from .permissions import IsStockPersonnel, IsResponsableStock, IsResponsableStockOrReadOnly
from .utils import log_audit

# stock/views.py
from django.http import JsonResponse

def health_view(request):
    return JsonResponse({"status": "ok"})




class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsStockPersonnel]


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsResponsableStockOrReadOnly]

    def perform_create(self, serializer):
        warehouse = serializer.save()
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_WAREHOUSE',
            entity_type='Warehouse',
            entity_id=str(warehouse.id),
            details={'name': warehouse.name},
            request=self.request
        )

    @action(detail=True, methods=['get'], url_path='stock-items')
    def stock_items(self, request, pk=None):
        warehouse = self.get_object()
        items = StockItem.objects.filter(warehouse=warehouse)
        serializer = StockItemSerializer(items, many=True)
        return Response(serializer.data)


class StockCategoryViewSet(viewsets.ModelViewSet):
    queryset = StockCategory.objects.all()
    serializer_class = StockCategorySerializer
    permission_classes = [IsAuthenticated, IsResponsableStockOrReadOnly]


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsStockPersonnel]
    filterset_fields = ['warehouse', 'category', 'is_expired']
    search_fields = ['name', 'sku', 'description']

    def perform_create(self, serializer):
        item = serializer.save()
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_STOCK_ITEM',
            entity_type='StockItem',
            entity_id=str(item.id),
            details={'name': item.name, 'sku': item.sku},
            request=self.request
        )

    def perform_update(self, serializer):
        item = serializer.save()
        log_audit(
            user_id=self.request.user_id,
            action_type='UPDATE_STOCK_ITEM',
            entity_type='StockItem',
            entity_id=str(item.id),
            details={'name': item.name},
            request=self.request
        )

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        items = StockItem.objects.filter(
            Q(quantity__lte=F('min_threshold'))
        )
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='expired')
    def expired(self, request):
        items = StockItem.objects.filter(is_expired=True)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='check-availability')
    def check_availability(self, request, pk=None):
        item = self.get_object()
        quantity_needed = request.data.get('quantity', 0)

        warehouses_with_stock = StockItem.objects.filter(
            sku=item.sku,
            quantity__gte=quantity_needed
        ).exclude(warehouse=item.warehouse)

        if warehouses_with_stock.exists():
            serializer = StockItemSerializer(warehouses_with_stock, many=True)
            return Response({
                'available': True,
                'warehouses': serializer.data
            })

        return Response({
            'available': False,
            'message': 'Stock insuffisant dans tous les magasins'
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    permission_classes = [IsAuthenticated, IsStockPersonnel]
    filterset_fields = ['movement_type', 'status', 'stock_item']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer

    def perform_create(self, serializer):
        movement = serializer.save(requested_by=self.request.user_id)

        if movement.movement_type == 'entrée':
            movement.stock_item.quantity += movement.quantity
            movement.stock_item.save()
            movement.status = 'complété'
            movement.save()

        elif movement.movement_type == 'sortie':
            if movement.stock_item.quantity >= movement.quantity:
                movement.stock_item.quantity -= movement.quantity
                movement.stock_item.save()
                movement.status = 'complété'
                movement.save()
            else:
                movement.status = 'rejeté'
                movement.notes += ' | Quantité insuffisante'
                movement.save()

        log_audit(
            user_id=self.request.user_id,
            action_type=f'CREATE_STOCK_MOVEMENT_{movement.movement_type.upper()}',
            entity_type='StockMovement',
            entity_id=str(movement.id),
            details={
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'stock_item': movement.stock_item.name
            },
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='approve', permission_classes=[IsAuthenticated, IsResponsableStock])
    def approve(self, request, pk=None):
        movement = self.get_object()

        if movement.status != 'en_attente':
            return Response(
                {'error': 'Ce mouvement a déjà été traité'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movement.approved_by = request.user_id
        movement.status = 'validé'

        if movement.movement_type == 'transfert':
            if movement.stock_item.quantity >= movement.quantity:
                movement.stock_item.quantity -= movement.quantity
                movement.stock_item.save()

                target_item = StockItem.objects.filter(
                    sku=movement.stock_item.sku,
                    warehouse=movement.to_warehouse
                ).first()

                if target_item:
                    target_item.quantity += movement.quantity
                    target_item.save()

                movement.status = 'complété'
            else:
                movement.status = 'rejeté'
                movement.notes += ' | Quantité insuffisante pour le transfert'

        movement.save()

        log_audit(
            user_id=request.user_id,
            action_type='APPROVE_STOCK_MOVEMENT',
            entity_type='StockMovement',
            entity_id=str(movement.id),
            details={'status': movement.status},
            request=request
        )

        return Response({'message': 'Mouvement approuvé', 'status': movement.status})


class InventoryCheckViewSet(viewsets.ModelViewSet):
    queryset = InventoryCheck.objects.all()
    serializer_class = InventoryCheckSerializer
    permission_classes = [IsAuthenticated, IsStockPersonnel]
    filterset_fields = ['warehouse']
    ordering = ['-date']

    def perform_create(self, serializer):
        check = serializer.save(checked_by=self.request.user_id)
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_INVENTORY_CHECK',
            entity_type='InventoryCheck',
            entity_id=str(check.id),
            details={'warehouse': check.warehouse.name},
            request=self.request
        )


class TransferRequestViewSet(viewsets.ModelViewSet):
    queryset = TransferRequest.objects.all()
    permission_classes = [IsAuthenticated, IsStockPersonnel]
    filterset_fields = ['status', 'from_warehouse', 'to_warehouse']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return TransferRequestCreateSerializer
        return TransferRequestSerializer

    def perform_create(self, serializer):
        transfer = serializer.save(requested_by=self.request.user_id)
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_TRANSFER_REQUEST',
            entity_type='TransferRequest',
            entity_id=str(transfer.id),
            details={
                'stock_item': transfer.stock_item.name,
                'quantity': transfer.quantity
            },
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='approve', permission_classes=[IsAuthenticated, IsResponsableStock])
    def approve(self, request, pk=None):
        transfer = self.get_object()

        if transfer.status != 'en_attente':
            return Response(
                {'error': 'Cette demande a déjà été traitée'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transfer.approved_by = request.user_id
        transfer.status = 'approuvé'
        transfer.validated_at = timezone.now()
        transfer.save()

        movement = StockMovement.objects.create(
            stock_item=transfer.stock_item,
            movement_type='transfert',
            quantity=transfer.quantity,
            from_warehouse=transfer.from_warehouse,
            to_warehouse=transfer.to_warehouse,
            requested_by=transfer.requested_by,
            approved_by=request.user_id,
            status='validé'
        )

        log_audit(
            user_id=request.user_id,
            action_type='APPROVE_TRANSFER_REQUEST',
            entity_type='TransferRequest',
            entity_id=str(transfer.id),
            details={'created_movement_id': str(movement.id)},
            request=request
        )

        return Response({'message': 'Demande approuvée et mouvement créé'})

    @action(detail=True, methods=['post'], url_path='reject', permission_classes=[IsAuthenticated, IsResponsableStock])
    def reject(self, request, pk=None):
        transfer = self.get_object()

        if transfer.status != 'en_attente':
            return Response(
                {'error': 'Cette demande a déjà été traitée'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transfer.approved_by = request.user_id
        transfer.status = 'rejeté'
        transfer.validated_at = timezone.now()
        transfer.notes = request.data.get('notes', transfer.notes)
        transfer.save()

        log_audit(
            user_id=request.user_id,
            action_type='REJECT_TRANSFER_REQUEST',
            entity_type='TransferRequest',
            entity_id=str(transfer.id),
            request=request
        )

        return Response({'message': 'Demande rejetée'})


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    permission_classes = [IsAuthenticated, IsStockPersonnel]
    filterset_fields = ['status', 'department']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseRequestCreateSerializer
        return PurchaseRequestSerializer

    def perform_create(self, serializer):
        purchase = serializer.save(
            requested_by=self.request.user_id,
            department='stock'
        )
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_PURCHASE_REQUEST',
            entity_type='PurchaseRequest',
            entity_id=str(purchase.id),
            details={'item_description': purchase.item_description[:100]},
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='validate', permission_classes=[IsAuthenticated, IsResponsableStock])
    def validate_request(self, request, pk=None):
        purchase = self.get_object()

        if purchase.status != 'en_attente':
            return Response(
                {'error': 'Cette demande a déjà été traitée'},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase.validated_by = request.user_id
        purchase.status = 'validé'
        purchase.validated_at = timezone.now()
        purchase.save()

        log_audit(
            user_id=request.user_id,
            action_type='VALIDATE_PURCHASE_REQUEST',
            entity_type='PurchaseRequest',
            entity_id=str(purchase.id),
            request=request
        )

        return Response({'message': 'Demande validée et envoyée au service financier'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsResponsableStock]
    filterset_fields = ['user_id', 'action_type', 'entity_type']
    search_fields = ['action_type', 'entity_type', 'entity_id']
    ordering = ['-timestamp']
