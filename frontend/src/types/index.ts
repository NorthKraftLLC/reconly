export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  industry?: string;
  is_active: boolean;
  created_at: string;
}

export interface InventoryItem {
  id: string;
  company_id: string;
  sku: string;
  name: string;
  description?: string;
  quantity_on_hand: number;
  unit_cost: number;
  currency: string;
  location?: string;
  category?: string;
  reorder_level: number;
  notes?: string;
  created_at: string;
}

export interface Reconciliation {
  id: string;
  company_id: string;
  name: string;
  status: string;
  source_file_name?: string;
  total_items: number;
  matched_items: number;
  discrepancies_found: number;
  created_by: string;
  created_at: string;
}

export interface Discrepancy {
  id: string;
  reconciliation_id: string;
  item_name: string;
  item_sku?: string;
  system_quantity: number;
  source_quantity: number;
  quantity_difference: number;
  discrepancy_type: string;
  severity: string;
  explanation: string;
  resolved: boolean;
  resolved_at?: string;
  reviewer_notes?: string;
  created_at: string;
}
