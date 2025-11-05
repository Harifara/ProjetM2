// types.ts
export interface StockItem {
  id: string;
  name: string;
  sku: string;
  category_name: string;
  warehouse_name: string;
  quantity: number;
  min_threshold: number;
  max_threshold: number;
  is_expired: boolean;
  expiry_date: string | null;
  needs_replenishment: boolean;
}

export interface Warehouse {
  id: string;
  name: string;
  district_name: string;
  location: string;
}

export interface StockMovement {
  id: string;
  stock_item_name: string;
  movement_type: string;
  quantity: number;
  status: string;
  created_at: string;
}

export interface TransferRequest {
  id: string;
  stock_item_name: string;
  from_warehouse_name: string;
  to_warehouse_name: string;
  quantity: number;
  status: string;
  validated_at: string | null;
}

export interface PurchaseRequest {
  id: string;
  item_description: string;
  quantity: number;
  status: string;
  validated_at: string | null;
}

export interface InventoryCheck {
  id: string;
  warehouse_name: string;
  checked_by: string;
  date: string;
  notes: string;
}

export interface AuditLog {
  id: string;
  user_id: string;
  action_type: string;
  entity_type: string;
  entity_id: string;
  timestamp: string;
  details: any;
}
