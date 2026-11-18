"""Core matching/reconciliation engine."""

from rapidfuzz import fuzz


def reconcile_sources(source_data: dict) -> dict:
    """Core reconciliation engine. Compares system inventory against source data.

    source_data format:
    {
        "system": [{"sku": "A", "name": "Widget", "qty": 100, "cost": 10.00}, ...],
        "source": [{"sku": "A", "name": "Widget", "qty": 95, "cost": 10.00}, ...]
    }
    """
    system = source_data.get("system", [])
    sources = source_data.get("source", [])

    system_map = {item.get("sku"): item for item in system}
    source_map = {item.get("sku"): item for item in sources}

    total_items = len(set(system_map.keys()) | set(source_map.keys()))
    matched_items = 0
    discrepancies = []

    # Check source items against system
    for sku, item in source_map.items():
        if sku not in system_map:
            qty = item.get("qty", 0)
            discrepancies.append({
                "item_name": item.get("name", sku),
                "item_sku": sku,
                "system_quantity": 0,
                "source_quantity": qty,
                "quantity_difference": qty,
                "discrepancy_type": "extra_item",
                "severity": "high" if qty > 0 else "low",
                "explanation": f"Item '{item.get('name', sku)}' (SKU: {sku}) exists in source but not in your system. Source shows {qty} units.",
            })
        else:
            sys_item = system_map[sku]
            sys_qty = sys_item.get("qty", 0)
            src_qty = item.get("qty", 0)
            diff = sys_qty - src_qty

            if abs(diff) > 0:
                severity = "critical" if abs(diff) > 50 else "high" if abs(diff) > 10 else "medium"
                discrepancies.append({
                    "item_name": sys_item.get("name", sku),
                    "item_sku": sku,
                    "system_quantity": sys_qty,
                    "source_quantity": src_qty,
                    "quantity_difference": diff,
                    "discrepancy_type": "quantity_mismatch",
                    "severity": severity,
                    "explanation": f"'{sys_item.get('name', sku)}' (SKU: {sku}): system says {sys_qty}, source says {src_qty}. You're {abs(diff)} units {'short' if diff > 0 else 'over'}.",
                })
            else:
                matched_items += 1

    # Check for items in system but not in source (missing items)
    for sku, item in system_map.items():
        if sku not in source_map:
            qty = item.get("qty", 0)
            discrepancies.append({
                "item_name": item.get("name", sku),
                "item_sku": sku,
                "system_quantity": qty,
                "source_quantity": 0,
                "quantity_difference": qty,
                "discrepancy_type": "missing_item",
                "severity": "high" if qty > 0 else "low",
                "explanation": f"Item '{item.get('name', sku)}' (SKU: {sku}) is in your system but not in the source file. System shows {qty} units.",
            })

    return {
        "total_items": total_items,
        "matched_items": matched_items,
        "discrepancies_found": len(discrepancies),
        "discrepancies": discrepancies,
    }
