
import re

def classify_page(text):
    """
    Identify the type of financial document
    using text extracted from a PDF page.
    """

    normalized_text = text.lower()

    # Extract invoice number
    invoice_match = re.search(
        r"invoice\s+number\s*#?\s*[:\-]?\s*([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )

    invoice_number = (
        invoice_match.group(1)
        if invoice_match
        else None
    )

    # Extract bill of supply number

    bill_match = re.search(
        r"Bill of Supply Details\s*:?\s*\n\s*:?\s*"
        r"([A-Z]{2,}[A-Z0-9]{6,})",
        text,
        re.IGNORECASE
    )

    if not bill_match:
        bill_match = re.search(
            r"Bill of Supply Number\s*[:\-]?\s*"
            r"([A-Z]{2,}[A-Z0-9]{6,})",
            text,
            re.IGNORECASE
        )

    bill_number = (
        bill_match.group(1)
        if bill_match
        else None
    )


    # Classification rules
    if "bill of supply" in normalized_text:

        document_type = "Bill of Supply"

        document_number = bill_number

    elif "tax invoice" in normalized_text:

        document_type = "Tax Invoice"

        document_number = invoice_number

    elif "purchase order" in normalized_text:

        document_type = "Purchase Order"

        document_number = None

    else:

        document_type = "Unknown"

        document_number = None

    return {
        "document_type": document_type,
        "document_number": document_number
    }



def group_documents(pages):
    """
    Group pages belonging to the same financial document.
    Also handles continuation pages.
    """

    documents = []

    for page in pages:

        text = page["text"]

        classification = classify_page(text)

        doc_type = classification["document_type"]
        doc_number = classification["document_number"]

        # Detect continuation pages
        lower_text = text.lower()

        continuation_markers = [
            "person liable to pay tax",
            "reverse charge",
            "signature / digital signature",
            "i/we have taken registration"
        ]

        is_continuation = any(
            marker in lower_text
            for marker in continuation_markers
        )

        # Attach continuation to previous Bill of Supply
        if (
            doc_type == "Unknown"
            and documents
            and documents[-1]["document_type"] == "Bill of Supply"
            and is_continuation
        ):

            documents[-1]["pages"].append(page["page"])

            continue

        current_key = (doc_type, doc_number)

        if (
            not documents
            or documents[-1]["key"] != current_key
        ):

            documents.append({
                "key": current_key,
                "document_type": doc_type,
                "document_number": doc_number,
                "pages": [page["page"]]
            })

        else:

            documents[-1]["pages"].append(page["page"])

    return documents
