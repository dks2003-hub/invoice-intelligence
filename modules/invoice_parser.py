
import re


def find_labeled_value(text, labels):
    """Extract a value following one of the supplied labels."""

    if isinstance(labels, str):
        labels = [labels]

    for label in labels:

        pattern = (
            rf"^\s*{re.escape(label)}\s*[:#\-]?\s*(.+?)\s*$"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE
        )

        if match:
            return match.group(1).strip(" ,:\t")

    return None


def extract_invoice_number(text, document_type):
    """Extract invoice or Bill of Supply number."""

    if document_type == "Bill of Supply":

        patterns = [
            r"Bill of Supply Details\s*:?\s*\n\s*:?\s*"
            r"([A-Z]{2,}[A-Z0-9]{6,})",

            r"Bill of Supply Number\s*[:\-]?\s*"
            r"([A-Z]{2,}[A-Z0-9]{6,})"
        ]

    else:

        patterns = [
            r"Invoice Number\s*#?\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9\-]{2,})"
        ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return None


def extract_invoice_date(text, document_type):
    """Extract invoice date in either text ordering."""

    if document_type == "Bill of Supply":

        patterns = [
            r"Bill of Supply Date\s*[:\-]?\s*"
            r"(\d{2}[-/]\d{2}[-/]\d{4})",

            r"(\d{2}[-/]\d{2}[-/]\d{4})"
            r"\s*\n\s*Bill of Supply Date"
        ]

    else:

        patterns = [
            r"Invoice Date\s*[:\-]?\s*"
            r"(\d{2}[-/]\d{2}[-/]\d{4})",

            r"(\d{2}[-/]\d{2}[-/]\d{4})"
            r"\s*\n\s*Invoice Date"
        ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


def extract_order_id(text):
    """Extract both standard and hyphenated order IDs."""

    # First try an explicitly labelled Order ID.
    match = re.search(
        r"\bOrder\s+ID\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\-]*)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Fallback for Flipkart-style order IDs.
    match = re.search(
        r"\bOD\d{10,}\b",
        text,
        re.IGNORECASE
    )

    return match.group(0) if match else None


def extract_vendor(text, document_type):
    """Extract vendor from different invoice formats."""

    if document_type == "Bill of Supply":

        vendor = find_labeled_value(
            text,
            ["Billed From", "Vendor"]
        )

    else:

        vendor = find_labeled_value(
            text,
            ["Sold By", "Vendor"]
        )

    if vendor:
        return vendor.rstrip(" ,:")

    return None


def extract_numbers(block):
    """Extract numeric values from a table section."""

    matches = re.findall(
        r"(?<![A-Za-z])[-+]?\d[\d,]*\.\d{1,2}",
        block
    )

    return [
        float(value.replace(",", ""))
        for value in matches
    ]


def extract_amounts(text, document_type):
    """
    Extract financial amounts.

    Supports:
    1. Flipkart table-based invoice text.
    2. Simple label-based invoice text.
    """

    amounts = {
        "taxable_value": None,
        "cgst": None,
        "sgst": None,
        "igst": None,
        "grand_total": None
    }

    # CASE 1: BILL OF SUPPLY

    if document_type == "Bill of Supply":

        match = re.search(
            r"GT Charges(.*?)\n\s*Total\s*\n",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            values = extract_numbers(match.group(1))

            if len(values) >= 5:

                values = values[-5:]

                amounts["taxable_value"] = values[-4]
                amounts["sgst"] = values[-3]
                amounts["cgst"] = values[-2]
                amounts["grand_total"] = values[-1]

    # CASE 2: TAX INVOICE

    else:

        match = re.search(
            r"\n\s*Total\s*\n(.*?)\n\s*Grand Total",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            values = extract_numbers(match.group(1))

            if len(values) >= 5:

                values = values[-5:]

                amounts["taxable_value"] = values[-3]
                amounts["igst"] = values[-2]
                amounts["grand_total"] = values[-1]

    # FALLBACK: LABEL-BASED EXTRACTION

    fallback_labels = {
        "taxable_value": r"^\s*Taxable\s+Value\s*[:\-]?\s*",
        "cgst": r"^\s*CGST\s*[:\-]?\s*",
        "sgst": r"^\s*SGST\s*[:\-]?\s*",
        "igst": r"^\s*IGST\s*[:\-]?\s*",
        "grand_total": r"^\s*Grand\s+Total\s*[:\-]?\s*"
    }

    for field, pattern in fallback_labels.items():

        if amounts[field] is not None:
            continue

        match = re.search(
            pattern + r"(?:₹\s*)?([\d,]+(?:\.\d{1,2})?)",
            text,
            re.IGNORECASE | re.MULTILINE
        )

        if match:

            amounts[field] = float(
                match.group(1).replace(",", "")
            )

    return amounts


def parse_invoice(text, document_type="Tax Invoice"):
    """Convert invoice text into structured information."""

    return {
        "document_type": document_type,

        "invoice_number": extract_invoice_number(
            text,
            document_type
        ),

        "invoice_date": extract_invoice_date(
            text,
            document_type
        ),

        "order_id": extract_order_id(text),

        "vendor": extract_vendor(
            text,
            document_type
        ),

        "amounts": extract_amounts(
            text,
            document_type
        )
    }
