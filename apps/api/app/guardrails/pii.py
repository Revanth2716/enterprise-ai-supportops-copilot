import re
from typing import Tuple, List

# PII Patterns
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def sanitize_pii(text: str) -> Tuple[str, List[str]]:
    """
    Detects and masks sensitive PII (Social Security Numbers, Credit Cards)
    from query strings before model processing and logging.
    """
    detected = []
    sanitized = text

    if SSN_PATTERN.search(sanitized):
        detected.append("SSN")
        sanitized = SSN_PATTERN.sub("[REDACTED_SSN]", sanitized)

    if CREDIT_CARD_PATTERN.search(sanitized):
        detected.append("CREDIT_CARD")
        sanitized = CREDIT_CARD_PATTERN.sub("[REDACTED_CC]", sanitized)

    return sanitized, detected
