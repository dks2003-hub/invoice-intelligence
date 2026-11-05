
from modules.invoice_pipeline import process_invoice_pdf


# Load the actual PDF
pdf_path = "data/invoices/sample_invoice.pdf"

with open(pdf_path, "rb") as file:
    pdf_bytes = file.read()


# Run the complete pipeline
result = process_invoice_pdf(pdf_bytes)


# Display results
print("\nINVOICE INTELLIGENCE RESULTS")
print("=" * 50)

if result["success"]:

    print("Total Pages:", result["total_pages"])

    print("Total Documents:", result["total_documents"])

    for index, document in enumerate(
        result["documents"], start=1
    ):

        print("\nDOCUMENT", index)
        print("-" * 40)

        print("Type:", document["document_type"])

        print("Pages:", document["pages"])

        print(
            "Document Number:",
            document["document_number"]
        )

        print(
            "Invoice Number:",
            document["invoice_number"]
        )

        print(
            "Invoice Date:",
            document["invoice_date"]
        )

        print("Vendor:", document["vendor"])

        print("Order ID:", document["order_id"])

        print("Amounts:", document["amounts"])

    print("\nPIPELINE EXECUTION SUCCESSFUL!")

else:

    print("Processing failed:", result["error"])
