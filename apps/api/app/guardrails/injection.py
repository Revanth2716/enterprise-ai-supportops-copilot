import re
from typing import Tuple, List

# Adversarial prompt injection signatures
INJECTION_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("ignore_instructions", re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts)", re.IGNORECASE)),
    ("system_override", re.compile(r"(override|bypass|disable)\s+([a-z\s]+)?(rules|prompt|policy|guardrail|security)", re.IGNORECASE)),
    ("developer_mode", re.compile(r"(enter|switch\s+to|enable)\s+(developer\s+mode|dan\s+mode|god\s+mode)", re.IGNORECASE)),
    ("jailbreak_attempt", re.compile(r"you\s+are\s+now\s+an\s+unfiltered|act\s+as\s+an\s+unrestricted\s+ai", re.IGNORECASE)),
    ("malicious_execution", re.compile(r"(drop|delete|truncate)\s+table|exec\s*\(|eval\s*\(|rm\s+-rf", re.IGNORECASE)),
    ("disregard_policies", re.compile(r"disregard\s+(company|enterprise)\s+(policies|rules|guidelines)", re.IGNORECASE)),
]


def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """
    Scans incoming query text against known adversarial prompt injection patterns.
    Returns (is_injected, matched_pattern_names).
    """
    matches = []
    for pattern_name, regex in INJECTION_PATTERNS:
        if regex.search(text):
            matches.append(pattern_name)

    return len(matches) > 0, matches
