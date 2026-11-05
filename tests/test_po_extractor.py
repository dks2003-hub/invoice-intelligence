
from pathlib import Path

from modules.po_extractor import extract_po_data


PO_FOLDER = Path("data/purchase_orders")


print("\nPURCHASE ORDER EXTRACTION RESULTS")
print("=" * 45)

for pdf_file in sorted(PO_FOLDER.glob("*.pdf")):

    with open(pdf_file, "rb") as file:
        pdf_bytes = file.read()

    result = extract_po_data(pdf_bytes)

    print(f"\nFile: {pdf_file.name}")

    if result["success"]:
        print("PO Number:", result["po_number"])
        print("Order ID:", result["order_id"])
        print("Vendor:", result["vendor"])
        print("PO Date:", result["po_date"])
        print("Amounts:", result["amounts"])
    else:
        print("Extraction failed:", result["error"])

print("\nPO EXTRACTION TEST COMPLETED!")
