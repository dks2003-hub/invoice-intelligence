
from modules.document_classifier import (
    classify_page,
    group_documents
)


# Test 1: Tax Invoice
page1 = {
    "page": 1,
    "text": """
    Tax Invoice
    Invoice Number # FAT5ES2600303310
    Grand Total Rs 9.00
    """
}


# Test 2: Bill of Supply
page2 = {
    "page": 2,
    "text": """
    Bill of Supply
    Bill of Supply Number : FAACR26003524254
    GT Charges 132.00
    """
}


# Test 3: Continuation page
page3 = {
    "page": 3,
    "text": """
    I/we have taken registration under CGST Act.
    Is the supply subject to reverse charge: No
    Person Liable to pay tax: GTA
    """
}


# Test 4: Another Tax Invoice
page4 = {
    "page": 4,
    "text": """
    Tax Invoice
    Invoice Number # FAJ2YV2600336628
    Grand Total Rs 240.00
    """
}


# Individual classification tests
print("\nINDIVIDUAL CLASSIFICATION RESULTS")

for page in [page1, page2, page3, page4]:

    result = classify_page(page["text"])

    print(f"Page {page['page']}: {result}")


# Document grouping test
print("\nDOCUMENT GROUPING RESULTS")

documents = group_documents(
    [page1, page2, page3, page4]
)

for document in documents:

    print(document)


# Verify expected output
assert len(documents) == 3

assert documents[0]["document_type"] == "Tax Invoice"
assert documents[0]["pages"] == [1]

assert documents[1]["document_type"] == "Bill of Supply"
assert documents[1]["pages"] == [2, 3]

assert documents[2]["document_type"] == "Tax Invoice"
assert documents[2]["pages"] == [4]

print("\nALL TESTS PASSED!")
