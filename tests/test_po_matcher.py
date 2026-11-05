
from modules.po_matcher import (
    load_purchase_orders,
    match_invoice_to_po
)


# Load all five Purchase Orders
purchase_orders = load_purchase_orders()

print("\nPURCHASE ORDER MATCHING TEST")
print("=" * 45)

print("Total POs loaded:", len(purchase_orders))


# Three invoices extracted from our actual sample PDF
invoices = [
    {
        "invoice_number": "FAT5ES2600303310",
        "order_id": "OD335011688375083100",
        "vendor": "Buzz Retail India Private Limited",
        "amounts": {"grand_total": 9.00}
    },
    {
        "invoice_number": "FAACR26003524254",
        "order_id": "OD335011688375083100",
        "vendor": "Flipkart India Private Limited",
        "amounts": {"grand_total": 132.00}
    },
    {
        "invoice_number": "FAJ2YV2600336628",
        "order_id": "OD335011688375083100",
        "vendor": "Buzz Retail India Private Limited",
        "amounts": {"grand_total": 240.00}
    }
]


for invoice in invoices:

    result = match_invoice_to_po(
        invoice,
        purchase_orders
    )

    print("\nInvoice:", invoice["invoice_number"])
    print("Status:", result["status"])
    print("Reason:", result["reason"])

    if result.get("matched_po"):
        print(
            "Matched PO:",
            result["matched_po"]["po_number"]
        )


# Test 4: Amount mismatch
amount_mismatch_invoice = {
    "invoice_number": "TEST-004",
    "order_id": "OD-TEST-004",
    "vendor": "Northstar Office Supplies Private Limited",
    "amounts": {"grand_total": 6000.00}
}

result = match_invoice_to_po(
    amount_mismatch_invoice,
    purchase_orders
)

print("\nAMOUNT MISMATCH TEST")
print("Status:", result["status"])
print("Difference:", result.get("difference"))


# Test 5: Vendor mismatch
vendor_mismatch_invoice = {
    "invoice_number": "TEST-005",
    "order_id": "OD-TEST-005",
    "vendor": "Different Technologies Private Limited",
    "amounts": {"grand_total": 11800.00}
}

result = match_invoice_to_po(
    vendor_mismatch_invoice,
    purchase_orders
)

print("\nVENDOR MISMATCH TEST")
print("Status:", result["status"])
print("Reason:", result["reason"])


# Verify expected outcomes
assert len(purchase_orders) == 5

assert match_invoice_to_po(
    invoices[0], purchase_orders
)["status"] == "matched"

assert match_invoice_to_po(
    invoices[1], purchase_orders
)["status"] == "matched"

assert match_invoice_to_po(
    invoices[2], purchase_orders
)["status"] == "matched"

assert match_invoice_to_po(
    amount_mismatch_invoice, purchase_orders
)["status"] == "amount_mismatch"

assert match_invoice_to_po(
    vendor_mismatch_invoice, purchase_orders
)["status"] == "vendor_mismatch"

print("\nALL PO MATCHING TESTS PASSED!")
