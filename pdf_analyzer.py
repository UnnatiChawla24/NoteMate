from PyPDF2 import PdfReader


def pdf_contains_text(filepath):
    """
    Check if the PDF file contains selectable (extractable) text on its first page.

    Args:
        filepath (str): Path to the PDF file.

    Returns:
        bool: True if selectable text is found on the first page, False otherwise.
    """
    with open(filepath, "rb") as f:
        reader = PdfReader(f)
        # Check if the PDF has any pages
        if reader.pages:
            # Extract text from the first page
            text = reader.pages[0].extract_text()
            # Return True if any text found, else False
            if text:
                return True
    # Return False if no pages or no text found
    return False