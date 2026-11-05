
import pymupdf
from pathlib import Path

output_dir = Path("data/test_invoices")
output_dir.mkdir(parents=True, exist_ok=True)


def create_invoice(
    filename,
    invoice_number,
    vendor,
    order_id,
    taxable,
    cgst,
    sgst,
    total,
    purpose
):
    doc = pymupdf.open()
    page = doc.new_page()

    lines = [
        ("TAX INVOICE", 20, 50, 18, True),
        (f"Invoice Number: {invoice_number}", 20, 100, 11, False),
        ("Invoice Date: 05-11-2026", 20, 125, 11, False),
        (f"Vendor: {vendor}", 20, 150, 11, False),
        (f"Order ID: {order_id}", 20, 175, 11, False),
        ("Description: Goods and Services", 20, 220, 11, False),
        (f"Taxable Value: {taxable:.2f}", 20, 260, 11, False),
        (f"CGST: {cgst:.2f}", 20, 285, 11, False),
        (f"SGST: {sgst:.2f}", 20, 310, 11, False),
        ("IGST: 0.00", 20, 335, 11, False),
        (f"Grand Total: {total:.2f}", 20, 375, 12, True),
        (f"Test Purpose: {purpose}", 20, 430, 10, False),
        ("Synthetic test document - not a genuine tax invoice.", 20, 460, 9, False),
    ]

    for text, x, y, size, bold in lines:
        font = "hebo" if bold else "helv"
        page.insert_text(
            (x, y),
            text,
            fontsize=size,
            fontname=font
        )

    output_path = output_dir / filename
    doc.save(output_path)
    doc.close()

    print(f"Created: {output_path}")


# TEST 1: Same vendor and order ID, different amount
# PO-2025-004 expected amount = INR 5900
create_invoice(
    filename="TEST-INVOICE-004-AMOUNT-MISMATCH.pdf",
    invoice_number="TEST-INV-004",
    vendor="Northstar Office Supplies Pvt Ltd",
    order_id="OD-TEST-004",
    taxable=5100,
    cgst=450,
    sgst=450,
    total=6000,
    purpose="Amount mismatch test. Expected PO amount: INR 5900."
)


# TEST 2: Same order ID and amount, different vendor
# PO-2025-005 expected vendor = Aster Technologies Pvt Ltd
create_invoice(
    filename="TEST-INVOICE-005-VENDOR-MISMATCH.pdf",
    invoice_number="TEST-INV-005",
    vendor="Different Vendor Services Pvt Ltd",
    order_id="OD-TEST-005",
    taxable=10000,
    cgst=900,
    sgst=900,
    total=11800,
    purpose="Vendor mismatch test. Expected PO vendor: Aster Technologies Pvt Ltd."
)

print("\nBoth test invoices generated successfully!")
