
import re

from modules.pdf_extractor import extract_pdf_text


def extract_po_data(pdf_bytes):
    """
    Extract structured Purchase Order information
    from a PDF document.
    """

    extraction = extract_pdf_text(pdf_bytes)

    if not extraction["success"]:
        return {
            "success": False,
            "error": extraction["error"]
        }

    text = extraction["text"]

    def find_value(pattern):
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE
        )
        return match.group(1).strip() if match else None

    # Extract PO information
    po_number = find_value(
        r"PO Number\s*[:#]?\s*([A-Z0-9-]+)"
    )

    order_id = find_value(
        r"Order\s*/\s*Reference ID\s*[:#]?\s*([A-Z0-9-]+)"
    )

    vendor = find_value(
        r"Vendor\s*:\s*(.+)"
    )

    po_date = find_value(
        r"PO Date\s*[:#]?\s*(\d{2}-\d{2}-\d{4})"
    )

    currency = find_value(
        r"Currency\s*[:#]?\s*([A-Z]{3})"
    )

    # Extract financial values

    def find_amount(label):
        """
        Extract monetary values even when the
        label and amount appear on separate lines.
        """

        pattern = (
            rf"{re.escape(label)}\s*[:：]?\s*"
            r"(?:INR\s*)?(?:₹\s*)?"
            r"([\d,]+(?:\.\d{1,2})?)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return float(
                match.group(1).replace(",", "")
            )

        return None

    amounts = {
        "taxable_value": find_amount("Taxable Value"),
        "cgst": find_amount("CGST"),
        "sgst": find_amount("SGST"),
        "igst": find_amount("IGST"),
        "grand_total": find_amount("Grand Total")
    }

    # Return structured PO information
    return {
        "success": True,
        "po_number": po_number,
        "order_id": order_id,
        "vendor": vendor,
        "po_date": po_date,
        "currency": currency,
        "amounts": amounts,
        "raw_text": text,
        "error": None
    }
