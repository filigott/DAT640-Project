import unicodedata


def advanced_normalize_text(text: str) -> str:
    """Normalize text by converting to lowercase, removing diacritics, and handling special characters like apostrophes."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove diacritics (e.g., á -> a)
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    # Replace apostrophes with an empty string or space
    text = text.replace("'", "")  # You can also replace it with a space if needed, e.g., text.replace("'", " ")
    
    # Remove other special characters, but retain alphanumeric and spaces
    return ''.join(e for e in text if e.isalnum() or e.isspace()).strip()
