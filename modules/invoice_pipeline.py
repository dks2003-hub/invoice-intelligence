
from modules.pdf_extractor import extract_pdf_text

from modules.document_classifier import group_documents

from modules.invoice_parser import parse_invoice


def process_invoice_pdf(pdf_bytes):
    """
    Complete invoice processing pipeline.

    Steps:
    1. Extract PDF text.
    2. Classify and group document pages.
    3. Parse each individual document.
    4. Return structured results.
    """

    # STEP 1: Extract PDF text
    extraction = extract_pdf_text(pdf_bytes)

    if not extraction["success"]:
        return {
            "success": False,
            "error": extraction["error"],
            "documents": []
        }

    # STEP 2: Classify and group pages
    pages = extraction["pages"]

    grouped_documents = group_documents(pages)

    # Create page lookup
    page_lookup = {
        page["page"]: page["text"]
        for page in pages
    }

    processed_documents = []

    # STEP 3: Parse each document separately
    for document in grouped_documents:

        # Combine text from all pages of this document
        document_text = "\n\n".join(
            page_lookup[page_number]
            for page_number in document["pages"]
        )

        parsed_data = parse_invoice(
            document_text,
            document_type=document["document_type"]
        )

        # Add page information
        parsed_data["pages"] = document["pages"]

        # Preserve classifier's document number
        parsed_data["document_number"] = (
            document["document_number"]
        )

        processed_documents.append(parsed_data)

    # STEP 4: Return complete result
    return {
        "success": True,
        "total_pages": extraction["page_count"],
        "total_documents": len(processed_documents),
        "documents": processed_documents,
        "error": None
    }
