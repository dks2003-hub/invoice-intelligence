
import pymupdf as fitz


def extract_pdf_text(pdf_bytes):
    """
    Extract text from a PDF file.

    Parameters:
        pdf_bytes: PDF file contents in bytes.

    Returns:
        Dictionary containing extracted text and page count.
    """

    try:
        # Open PDF directly from memory
        pdf_document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        extracted_pages = []

        # Extract text from each page
        for page_number, page in enumerate(pdf_document, start=1):

            page_text = page.get_text("text")

            extracted_pages.append({
                "page": page_number,
                "text": page_text.strip()
            })

        pdf_document.close()

        full_text = "\n\n".join(
            page["text"] for page in extracted_pages
        )

        return {
            "success": True,
            "page_count": len(extracted_pages),
            "text": full_text,
            "pages": extracted_pages,
            "error": None
        }

    except Exception as error:

        return {
            "success": False,
            "page_count": 0,
            "text": "",
            "pages": [],
            "error": str(error)
        }
