
import streamlit as st
import pandas as pd

from modules.invoice_pipeline import process_invoice_pdf
from modules.po_matcher import (
    load_purchase_orders,
    match_invoice_to_po
)


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Invoice Intelligence",
    page_icon="📄",
    layout="wide"
)


# =====================================================
# 2. HELPER FUNCTIONS
# =====================================================

@st.cache_data
def get_purchase_orders():
    return load_purchase_orders()


def get_status_counts(results):
    """Count each PO matching status."""

    counts = {
        "matched": 0,
        "amount_mismatch": 0,
        "vendor_mismatch": 0,
        "no_po_found": 0,
        "manual_review": 0
    }

    for item in results:
        status = item["matching"].get("status", "manual_review")

        if status in counts:
            counts[status] += 1

    return counts


def create_results_dataframe(results):
    """Convert extracted invoice results into a DataFrame."""

    rows = []

    for item in results:
        document = item["document"]
        matching = item["matching"]
        amounts = document.get("amounts") or {}

        rows.append({
            "Source File": item["filename"],
            "Document Type": document.get("document_type"),
            "Invoice Number": document.get("invoice_number"),
            "Vendor": document.get("vendor"),
            "Invoice Date": document.get("invoice_date"),
            "Order ID": document.get("order_id"),
            "Grand Total": amounts.get("grand_total"),
            "PO Status": matching.get("status")
        })

    return pd.DataFrame(rows)


# =====================================================
# 3. LOAD PURCHASE ORDERS
# =====================================================

try:
    purchase_orders = get_purchase_orders()
    po_load_error = None

except Exception as error:
    purchase_orders = []
    po_load_error = str(error)


# =====================================================
# 4. SESSION STATE
# =====================================================

if "processing_history" not in st.session_state:
    st.session_state["processing_history"] = []

if "processing_result" not in st.session_state:
    st.session_state["processing_result"] = None


# =====================================================
# 5. APPLICATION HEADER
# =====================================================

st.title("📄 Invoice Intelligence")

st.markdown(
    "### Automated Invoice Processing & PO Validation"
)

st.caption(
    "Extract, classify, validate and match financial documents."
)

if po_load_error:
    st.error(f"Could not load Purchase Orders: {po_load_error}")

st.divider()


# =====================================================
# 6. SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Dashboard",
        "Upload Invoice",
        "Invoice History"
    ]
)

st.sidebar.divider()

st.sidebar.metric(
    "Available Purchase Orders",
    len(purchase_orders)
)

if st.session_state["processing_result"]:
    st.sidebar.metric(
        "Documents Processed",
        len(st.session_state["processing_history"])
    )

if st.sidebar.button("Clear Processing Data"):
    st.session_state["processing_result"] = None
    st.session_state["processing_history"] = []
    st.rerun()


# =====================================================
# 7. DASHBOARD
# =====================================================

if page == "Dashboard":

    st.subheader("Processing Dashboard")

    history = st.session_state["processing_history"]

    total_documents = len(history)

    status_counts = get_status_counts(history)

    matched = status_counts["matched"]

    needs_review = (
        status_counts["amount_mismatch"]
        + status_counts["vendor_mismatch"]
        + status_counts["no_po_found"]
        + status_counts["manual_review"]
    )

    total_files = len({
        item["filename"] for item in history
    })

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Available Purchase Orders",
        len(purchase_orders)
    )

    col2.metric(
        "Invoice Documents",
        total_documents
    )

    col3.metric(
        "Matched",
        matched
    )

    col4.metric(
        "Needs Review",
        needs_review
    )

    st.divider()

    st.subheader("Available Purchase Orders")

    with st.expander(
        f"View all {len(purchase_orders)} available Purchase Orders"
    ):

        if purchase_orders:

            po_rows = []

            for po in purchase_orders:

                amounts = po.get("amounts") or {}

                po_rows.append({
                    "PO Number": po.get("po_number"),
                    "Vendor": po.get("vendor"),
                    "Order ID": po.get("order_id"),
                    "PO Date": po.get("po_date"),
                    "Grand Total": amounts.get("grand_total"),
                    "Source File": po.get("source_file")
                })

            po_df = pd.DataFrame(po_rows)

            st.dataframe(
                po_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No Purchase Orders are currently available.")

    st.divider()

    if total_documents == 0:

        st.info(
            "No invoices have been processed yet. "
            "Go to Upload Invoice to get started."
        )

    else:

        st.subheader("Latest Processing Statistics")

        col1, col2 = st.columns(2)

        col1.metric("Files Processed", total_files)

        col2.metric("Documents Identified", total_documents)

        status_df = pd.DataFrame({
            "PO Matching Status": [
                "Matched",
                "Amount Mismatch",
                "Vendor Mismatch",
                "No PO Found",
                "Manual Review"
            ],
            "Count": [
                status_counts["matched"],
                status_counts["amount_mismatch"],
                status_counts["vendor_mismatch"],
                status_counts["no_po_found"],
                status_counts["manual_review"]
            ]
        })

        st.bar_chart(
            status_df.set_index("PO Matching Status")
        )

    st.divider()

    st.subheader("System Capabilities")

    st.markdown("""
    - **PDF Extraction:** Extract text from uploaded PDF documents.
    - **Document Classification:** Identify Tax Invoices and Bills of Supply.
    - **Information Extraction:** Extract invoice number, date, vendor and order ID.
    - **Financial Extraction:** Identify taxable value, taxes and grand total.
    - **Purchase Order Processing:** Extract information from Purchase Order PDFs.
    - **Automated PO Matching:** Match documents using Order ID, vendor and amount.
    - **Exception Detection:** Identify amount mismatches, vendor mismatches and missing information.
    - **Reporting:** Download extracted invoice information as a CSV report.
    """)


# =====================================================
# 8. INVOICE UPLOAD AND PROCESSING
# =====================================================

elif page == "Upload Invoice":

    st.subheader("Upload Invoice Documents")

    uploaded_files = st.file_uploader(
        "Choose invoice PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.success(
            f"{len(uploaded_files)} PDF file(s) uploaded successfully."
        )

        for uploaded_file in uploaded_files:
            st.write(f"📄 {uploaded_file.name}")

        if st.button(
            "Process All Invoices",
            type="primary",
            use_container_width=True
        ):

            all_matching_results = []
            total_pages = 0
            processing_errors = []

            with st.spinner(
                "Extracting, classifying and validating documents..."
            ):

                for uploaded_file in uploaded_files:

                    try:

                        pdf_bytes = uploaded_file.getvalue()

                        result = process_invoice_pdf(pdf_bytes)

                        if not result["success"]:

                            processing_errors.append({
                                "filename": uploaded_file.name,
                                "error": result.get("error", "Unknown error")
                            })

                            continue

                        total_pages += result["total_pages"]

                        for document in result["documents"]:

                            match_result = match_invoice_to_po(
                                document,
                                purchase_orders
                            )

                            all_matching_results.append({
                                "filename": uploaded_file.name,
                                "document": document,
                                "matching": match_result
                            })

                    except Exception as error:

                        processing_errors.append({
                            "filename": uploaded_file.name,
                            "error": str(error)
                        })

            # Save the latest processing result

            processing_result = {
                "filenames": [
                    file.name for file in uploaded_files
                ],
                "total_pages": total_pages,
                "total_documents": len(all_matching_results),
                "matching_results": all_matching_results,
                "errors": processing_errors
            }

            st.session_state["processing_result"] = processing_result

            # Add results to current session history

            st.session_state["processing_history"].extend(
                all_matching_results
            )

            if processing_errors:
                st.warning(
                    f"{len(processing_errors)} file(s) could not be processed."
                )

                for error in processing_errors:
                    st.error(
                        f"{error['filename']}: {error['error']}"
                    )

            if all_matching_results:
                st.success(
                    f"Successfully identified "
                    f"{len(all_matching_results)} document(s) "
                    f"from {len(uploaded_files)} uploaded file(s)."
                )
            else:
                st.warning("No documents were identified.")

            st.rerun()

    else:

        st.info("Please upload one or more PDF files to begin.")

    # -------------------------------------------------
    # DISPLAY LATEST PROCESSING RESULTS
    # -------------------------------------------------

    data = st.session_state["processing_result"]

    if data:

        matching_results = data["matching_results"]

        st.divider()

        st.subheader("Processing Summary")

        st.write("**Processed Files:**")

        for filename in data["filenames"]:
            st.write(f"📄 {filename}")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Pages",
            data["total_pages"]
        )

        col2.metric(
            "Documents Identified",
            data["total_documents"]
        )

        matched_count = get_status_counts(
            matching_results
        )["matched"]

        col3.metric(
            "Successfully Matched",
            matched_count
        )

        st.divider()

        st.subheader("Document Validation Results")

        for index, item in enumerate(
            matching_results,
            start=1
        ):

            document = item["document"]
            matching = item["matching"]
            status = matching["status"]

            with st.expander(
                f"Document {index}: "
                f"{document.get('invoice_number') or 'Unknown'}",
                expanded=True
            ):

                st.caption(
                    f"Source File: {item['filename']}"
                )

                st.write(
                    "**Document Type:**",
                    document.get("document_type", "Unknown")
                )

                st.write(
                    "**Vendor:**",
                    document.get("vendor") or "Not identified"
                )

                st.write(
                    "**Invoice Date:**",
                    document.get("invoice_date") or "Not identified"
                )

                st.write(
                    "**Order ID:**",
                    document.get("order_id") or "Not identified"
                )

                st.write(
                    "**Invoice Number:**",
                    document.get("invoice_number") or "Not identified"
                )

                amounts = document.get("amounts") or {}

                st.write(
                    "**Grand Total:**",
                    amounts.get("grand_total", "Not identified")
                )

                st.divider()

                st.markdown("#### PO Matching")

                if status == "matched":

                    st.success("PURCHASE ORDER MATCHED")

                    po = matching["matched_po"]

                    st.write(
                        "**Matched PO:**",
                        po.get("po_number", "Unknown")
                    )

                    st.write(
                        "**PO Vendor:**",
                        po.get("vendor", "Unknown")
                    )

                    po_amounts = po.get("amounts") or {}

                    st.write(
                        "**PO Amount:**",
                        po_amounts.get("grand_total", "Unknown")
                    )

                    st.write(
                        "**Difference:**",
                        matching.get("difference", 0)
                    )

                    st.write(matching.get("reason", ""))

                elif status == "amount_mismatch":

                    st.error("AMOUNT MISMATCH")

                    st.write(
                        "**Invoice Amount:**",
                        matching.get("invoice_amount")
                    )

                    st.write(
                        "**PO Amount:**",
                        matching.get("po_amount")
                    )

                    st.write(
                        "**Difference:**",
                        matching.get("difference")
                    )

                    st.warning(matching.get("reason", ""))

                    po = matching.get("matched_po")

                    if po:
                        st.write(
                            "**Candidate PO:**",
                            po.get("po_number", "Unknown")
                        )

                elif status == "vendor_mismatch":

                    st.error("VENDOR MISMATCH")

                    st.warning(matching.get("reason", ""))

                    st.write(
                        "**Candidate POs:**",
                        matching.get("candidate_pos", [])
                    )

                elif status == "no_po_found":

                    st.warning("NO PURCHASE ORDER FOUND")

                    st.write(matching.get("reason", ""))

                else:

                    st.warning("MANUAL REVIEW REQUIRED")

                    st.write(matching.get("reason", ""))

        st.divider()

        st.subheader("Extracted Documents")

        extracted_df = create_results_dataframe(
            matching_results
        )

        st.dataframe(
            extracted_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = extracted_df.to_csv(index=False)

        st.download_button(
            "Download Processing Report",
            data=csv_data,
            file_name="invoice_processing_report.csv",
            mime="text/csv"
        )


# =====================================================
# 9. INVOICE HISTORY
# =====================================================

elif page == "Invoice History":

    st.subheader("Invoice Processing History")

    history = st.session_state["processing_history"]

    if not history:

        st.info(
            "No invoice processing history available. "
            "Upload and process an invoice to see the results here."
        )

    else:

        status_counts = get_status_counts(history)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Documents",
            len(history)
        )

        col2.metric(
            "Matched",
            status_counts["matched"]
        )

        col3.metric(
            "Needs Review",
            len(history) - status_counts["matched"]
        )

        st.divider()

        history_df = create_results_dataframe(history)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Complete History",
            data=history_df.to_csv(index=False),
            file_name="invoice_processing_history.csv",
            mime="text/csv"
        )

        st.caption(
            "Note: This history is maintained for the current "
            "Streamlit session. Permanent database storage "
            "is not implemented."
        )
