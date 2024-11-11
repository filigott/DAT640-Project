import random
import re
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


def preprocess_name(name):
    """Remove unnecessary punctuation and extra whitespace."""
    return re.sub(r"[^\w\s'\-()]", "", name).strip()


def clean_and_filter_data(data_list):
    """Clean, filter out empty or non-useful entries."""
    return [
        preprocess_name(entry)
        for entry in data_list
        if entry and len(entry) > 2 and not entry.isdigit()
    ]

def random_case_variation(text, variation_probability=0.05):
    """Introduce case variation with a lower default probability."""
    if random.random() < variation_probability:
        return random.choice([text.lower(), text.upper(), text.title()])
    return text
