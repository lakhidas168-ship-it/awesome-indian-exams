import re

def extract_entities(text: str) -> set[str]:
    # Matches URLs, dates (YYYY-MM-DD), and numbers
    urls = set(re.findall(r'https?://[^\s]+', text))
    dates = set(re.findall(r'\d{4}-\d{2}-\d{2}', text))
    numbers = set(re.findall(r'\d+', text))
    return urls | dates | numbers

def verify_integrity(original: str, translated: str) -> bool:
    """
    Verifies that numbers, dates, and URLs are identical.
    """
    orig_entities = extract_entities(original)
    trans_entities = extract_entities(translated)
    return orig_entities == trans_entities
