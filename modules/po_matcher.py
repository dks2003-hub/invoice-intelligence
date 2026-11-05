
from pathlib import Path
import re

from modules.po_extractor import extract_po_data


PO_FOLDER = Path("data/purchase_orders")


def load_purchase_orders():
    """
    Extract and load all available PO PDFs.
    """

    purchase_orders = []

    for pdf_file in sorted(PO_FOLDER.glob("*.pdf")):

        with open(pdf_file, "rb") as file:
            pdf_bytes = file.read()

        result = extract_po_data(pdf_bytes)

        if result["success"]:
            result["source_file"] = pdf_file.name
            purchase_orders.append(result)

    return purchase_orders


def normalize_vendor(vendor):
    """
    Normalize vendor names for comparison.
    """

    if not vendor:
        return ""

    vendor = vendor.lower().strip()

    # Standardize common company suffixes
    vendor = re.sub(r"\b(private limited|pvt ltd|pvt limited)\b", "", vendor)

    return "".join(
        char.lower()
        for char in vendor
        if char.isalnum()
    )


def match_invoice_to_po(invoice, purchase_orders):
    """
    Match invoice against available Purchase Orders.

    Matching priority:
    1. Order ID
    2. Vendor
    3. Grand total
    """

    invoice_order_id = str(
        invoice.get("order_id") or ""
    ).strip().upper()

    invoice_vendor = normalize_vendor(
        invoice.get("vendor")
    )

    invoice_amounts = invoice.get("amounts") or {}
    invoice_total = invoice_amounts.get("grand_total")

    # Step 1: Validate required invoice fields

    if not invoice_order_id:
        return {
            "status": "manual_review",
            "reason": "Invoice order ID is missing.",
            "matched_po": None
        }

    if not invoice_vendor:
        return {
            "status": "manual_review",
            "reason": "Invoice vendor name is missing.",
            "matched_po": None
        }

    if invoice_total is None:
        return {
            "status": "manual_review",
            "reason": "Invoice grand total is missing.",
            "matched_po": None
        }

    # Step 2: Find POs with matching Order ID

    order_matches = [
        po for po in purchase_orders
        if str(po.get("order_id") or "").strip().upper()
        == invoice_order_id
    ]

    if not order_matches:
        return {
            "status": "no_po_found",
            "reason": "No PO found for this order ID.",
            "matched_po": None
        }

    # Step 3: Find matching vendor

    vendor_matches = [
        po for po in order_matches
        if normalize_vendor(po.get("vendor")) == invoice_vendor
    ]

    # Step 4: Check vendor mismatch

    if not vendor_matches:
        return {
            "status": "vendor_mismatch",
            "reason": "Order ID exists, but vendor does not match.",
            "matched_po": None,
            "candidate_pos": [
                po.get("po_number") for po in order_matches
            ]
        }

    # Step 5: Compare invoice amount with matching vendor POs

    amount_results = []

    for po in vendor_matches:

        po_amounts = po.get("amounts") or {}
        po_total = po_amounts.get("grand_total")

        if po_total is None:
            continue

        difference = round(
            float(invoice_total) - float(po_total), 2
        )

        amount_results.append({
            "po": po,
            "po_total": float(po_total),
            "difference": difference
        })

    if not amount_results:
        return {
            "status": "manual_review",
            "reason": "PO grand total is missing.",
            "matched_po": None
        }

    # Step 6: Find exact amount matches

    exact_matches = [
        item for item in amount_results
        if abs(item["difference"]) <= 0.01
    ]

    if len(exact_matches) == 1:

        item = exact_matches[0]

        return {
            "status": "matched",
            "reason": "Order ID, vendor and grand total match.",
            "matched_po": item["po"],
            "invoice_amount": float(invoice_total),
            "po_amount": item["po_total"],
            "difference": 0.0
        }

    if len(exact_matches) > 1:

        return {
            "status": "manual_review",
            "reason": "Multiple POs match all invoice details.",
            "matched_po": None,
            "candidate_pos": [
                item["po"].get("po_number")
                for item in exact_matches
            ]
        }

    # Step 7: Amount mismatch

    if len(amount_results) == 1:

        item = amount_results[0]

        return {
            "status": "amount_mismatch",
            "reason": "Invoice and PO grand totals differ.",
            "matched_po": item["po"],
            "invoice_amount": float(invoice_total),
            "po_amount": item["po_total"],
            "difference": item["difference"]
        }

    # Multiple POs with the same vendor and order ID
    return {
        "status": "manual_review",
        "reason": "Multiple vendor POs found, but none matches the invoice amount.",
        "matched_po": None,
        "candidate_pos": [
            item["po"].get("po_number")
            for item in amount_results
        ]
    }
