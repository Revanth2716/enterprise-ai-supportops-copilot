import re
from typing import Tuple, List

# Secret patterns
SECRET_PATTERNS = [
    ("OPENAI_KEY", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
    ("BEARER_TOKEN", re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{25,}")),
    ("AWS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GENERIC_API_KEY", re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?")),
]


def scan_and_redact_secrets(text: str) -> Tuple[str, List[str]]:
    """
    Detects API credentials, Bearer tokens, and secrets, redacting them.
    """
    redacted = text
    found = []

    for name, pattern in SECRET_PATTERNS:
        if pattern.search(redacted):
            found.append(name)
            redacted = pattern.sub("[REDACTED_SECRET]", redacted)

    return redacted, found
