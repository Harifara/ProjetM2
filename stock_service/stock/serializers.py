from rest_framework import serializers
from .models import (
    District, Warehouse, StockCategory, StockItem, StockMovement,
    InventoryCheck, TransferRequest, PurchaseRequest, AuditLog
)


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class WarehouseSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'district', 'district_name', 'name', 'location']


class StockCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockCategory
        fields = ['id', 'name']


class StockItemSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    needs_replenishment = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockItem
        fields = [
            'id', 'warehouse', 'warehouse_name', 'category', 'category_name',
            'name', 'description', 'sku', 'quantity', 'is_expired', 'expiry_date',
            'min_threshold', 'max_threshold', 'needs_replenishment'
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source='stock_item.name', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True, allow_null=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True, allow_null=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'stock_item', 'stock_item_name', 'movement_type', 'quantity',
            'from_warehouse', 'from_warehouse_name', 'to_warehouse', 'to_warehouse_name',
            'requested_by', 'approved_by', 'created_at', 'status', 'document_id', 'notes'
        ]
        read_only_fields = ['id', 'created_at', 'requested_by']


class StockMovementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            'stock_item', 'movement_type', 'quantity', 'from_warehouse',
            'to_warehouse', 'notes'
        ]

    def validate(self, attrs):
        movement_type = attrs.get('movement_type')
        from_warehouse = attrs.get('from_warehouse')
        to_warehouse = attrs.get('to_warehouse')

        if movement_type == 'transfert':
            if not from_warehouse or not to_warehouse:
                raise serializers.ValidationError(
                    "Les magasins source et destination sont requis pour un transfert"
                )
            if from_warehouse == to_warehouse:
                raise serializers.ValidationError(
                    "Les magasins source et destination doivent être différents"
                )

        return attrs


class InventoryCheckSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = InventoryCheck
        fields = ['id', 'warehouse', 'warehouse_name', 'checked_by', 'date', 'notes']
        read_only_fields = ['id', 'date', 'checked_by']


class TransferRequestSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source='stock_item.name', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)

    class Meta:
        model = TransferRequest
        fields = [
            'id', 'stock_item', 'stock_item_name', 'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name', 'quantity', 'requested_by', 'approved_by',
            'status', 'created_at', 'validated_at', 'notes'
        ]
        read_only_fields = ['id', 'created_at', 'validated_at', 'requested_by']


class TransferRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRequest
        fields = ['stock_item', 'from_warehouse', 'to_warehouse', 'quantity', 'notes']

    def validate(self, attrs):
        if attrs['from_warehouse'] == attrs['to_warehouse']:
            raise serializers.ValidationError(
                "Les magasins source et destination doivent être différents"
            )

        stock_item = attrs['stock_item']
        if stock_item.warehouse != attrs['from_warehouse']:
            raise serializers.ValidationError(
                "L'article doit appartenir au magasin source"
            )

        if stock_item.quantity < attrs['quantity']:
            raise serializers.ValidationError(
                f"Quantité insuffisante. Disponible: {stock_item.quantity}"
            )

        return attrs


class PurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'requested_by', 'department', 'item_description', 'quantity',
            'status', 'created_at', 'validated_by', 'validated_at', 'notes'
        ]
        read_only_fields = ['id', 'created_at', 'validated_at', 'requested_by']


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = ['item_description', 'quantity', 'notes']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_id', 'action_type', 'entity_type', 'entity_id',
            'timestamp', 'details', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']
