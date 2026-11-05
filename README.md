# Invoice Intelligence

An automated invoice processing and purchase order (PO) matching application built with Python and Streamlit.

## Overview

Invoice Intelligence simplifies invoice verification by extracting structured information from PDF invoices and comparing it against available purchase orders.

The application identifies invoice details, validates vendor and order information, checks invoice amounts, and highlights discrepancies that may require manual review.

## Features

- **Multiple PDF Upload:** Upload and process multiple invoice PDFs.
- **PDF Text Extraction:** Extract text from PDF documents using PyMuPDF.
- **Document Classification:** Identify Tax Invoices, Bills of Supply, and Purchase Orders.
- **Invoice Data Extraction:** Extract invoice numbers, dates, vendors, order IDs, and financial information.
- **Purchase Order Extraction:** Load and extract structured details from available PO documents.
- **Automated PO Matching:** Match invoices against purchase orders using order ID, vendor name, and grand total.
- **Discrepancy Detection:** Identify amount mismatches, vendor mismatches, missing information, and cases requiring manual review.
- **Dashboard:** View processing statistics and purchase order information.
- **Invoice History:** Review documents processed during the current application session.
- **CSV Export:** Download extracted invoice information.

## Processing Architecture

```text
Invoice PDF Upload
        |
        v
PDF Text Extraction (PyMuPDF)
        |
        v
Document Classification
        |
        v
Invoice Parsing
        |
        v
Structured Invoice Data
        |
        v
Purchase Order Extraction
        |
        v
PO Matching and Validation
        |
        v
Matched / Amount Mismatch /
Vendor Mismatch / Manual Review
        |
        v
Dashboard and CSV Export
```

## Project Structure

```text
Invoice_Intelligence/
│
├── app.py
├── config.py
├── requirements.txt
├── generate_test_invoices.py
├── README.md
│
├── data/
│   ├── invoices/
│   ├── purchase_orders/
│   └── test_invoices/
│
├── modules/
│   ├── document_classifier.py
│   ├── invoice_parser.py
│   ├── invoice_pipeline.py
│   ├── pdf_extractor.py
│   ├── po_extractor.py
│   └── po_matcher.py
│
└── tests/
    ├── test_classifier.py
    ├── test_invoice_parser.py
    ├── test_invoice_pipeline.py
    ├── test_po_extractor.py
    └── test_po_matcher.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/dks2003-hub/invoice-intelligence.git
cd invoice-intelligence
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Running Tests

Run the following commands from the project root:

```bash
python -m tests.test_classifier
python -m tests.test_invoice_parser
python -m tests.test_invoice_pipeline
python -m tests.test_po_extractor
python -m tests.test_po_matcher
```

## Validation Scenarios

The project includes sample purchase orders and test invoices to demonstrate:

- Successful invoice-to-PO matching.
- Invoice amount mismatch detection.
- Vendor mismatch detection.
- Manual review when required information is unavailable.

## Current Limitations

- PDF extraction currently relies on text-based PDF content; scanned documents may require OCR.
- Invoice history is maintained in the current Streamlit session and is not persistent across sessions.
- PO matching uses rule-based validation.
- The application does not currently include a production database or user authentication system.

## Technology Stack

- Python
- Streamlit
- Pandas
- PyMuPDF
- PyTesseract
- Pillow

## Repository

[GitHub - Invoice Intelligence](https://github.com/dks2003-hub/invoice-intelligence)