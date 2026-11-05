
from modules.invoice_parser import parse_invoice


sample_invoice = """
Tax Invoice

Sold By: Buzz Retail India Private Limited

Invoice Number # FAJ2YV2600336628

Invoice Date: 23-07-2025

Order ID: OD335011688375083100

Taxable Value: 203.39
IGST: 36.61
Grand Total: 240.00
"""
print("\nDEBUG: RAW TEXT PASSED TO PARSER")
print(repr(sample_invoice))

result = parse_invoice(sample_invoice)

print("\nINVOICE PARSING RESULT")
print("----------------------")

for key, value in result.items():
    print(f"{key}: {value}")

# Basic verification
assert result["invoice_number"] == "FAJ2YV2600336628"

assert result["invoice_date"] == "23-07-2025"

assert result["order_id"] == "OD335011688375083100"

assert result["amounts"]["grand_total"] == 240.00

print("\nALL PARSER TESTS PASSED!")
