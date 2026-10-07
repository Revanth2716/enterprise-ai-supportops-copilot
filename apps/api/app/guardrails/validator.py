import re
from typing import Dict, Any, List, Tuple
from app.guardrails.injection import detect_prompt_injection
from app.guardrails.pii import sanitize_pii
from app.guardrails.secret_scanner import scan_and_redact_secrets

MAX_QUERY_LENGTH = 2000
CITATION_PATTERN = re.compile(r"\[Doc:([^#\]]+)#C(\d+)\]")


class GuardrailViolationError(Exception):
    def __init__(self, message: str, reasons: List[str]):
        super().__init__(message)
        self.message = message
        self.reasons = reasons


class SecurityValidator:
    """
    Enterprise guardrail boundary covering Pre-agent input validation,
    tool authorization validation, and Post-generation output validation.
    """

    def validate_input(self, raw_query: str) -> Dict[str, Any]:
        """
        Validates user input before passing to agent workflow.
        """
        if not raw_query or not raw_query.strip():
            raise GuardrailViolationError("Empty query provided.", ["EMPTY_QUERY"])

        if len(raw_query) > MAX_QUERY_LENGTH:
            raise GuardrailViolationError(
                f"Query exceeds maximum character limit of {MAX_QUERY_LENGTH}.",
                ["EXCEEDED_LENGTH_LIMIT"]
            )

        # 1. Prompt Injection Scan
        is_injected, matched_patterns = detect_prompt_injection(raw_query)
        if is_injected:
            raise GuardrailViolationError(
                "Query blocked: Potential prompt injection or system override detected.",
                matched_patterns
            )

        # 2. Secret Redaction
        sanitized_text, detected_secrets = scan_and_redact_secrets(raw_query)

        # 3. PII Masking
        sanitized_text, detected_pii = sanitize_pii(sanitized_text)

        return {
            "is_valid": True,
            "original_query": raw_query,
            "sanitized_query": sanitized_text,
            "detected_pii": detected_pii,
            "detected_secrets": detected_secrets
        }

    def validate_citations(
        self,
        response_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates that generated citations match retrieved knowledge chunks.
        """
        valid_chunk_tokens = {
            chunk.get("citation_token"): chunk
            for chunk in retrieved_chunks
            if chunk.get("citation_token")
        }

        matches = CITATION_PATTERN.findall(response_text)
        found_tokens = [f"[Doc:{title}#C{idx}]" for title, idx in matches]

        verified_citations = []
        unverified_citations = []

        for token in set(found_tokens):
            if token in valid_chunk_tokens:
                chunk = valid_chunk_tokens[token]
                verified_citations.append({
                    "citation_token": token,
                    "document_title": chunk.get("document_title"),
                    "chunk_id": chunk.get("chunk_id"),
                    "content_excerpt": chunk.get("content", "")[:120] + "..."
                })
            else:
                unverified_citations.append(token)

        total_citations = len(found_tokens)
        verified_count = len(verified_citations)
        coverage_rate = 1.0 if total_citations == 0 else round(verified_count / total_citations, 3)

        return {
            "total_citations": total_citations,
            "verified_count": verified_count,
            "coverage_rate": coverage_rate,
            "verified_citations": verified_citations,
            "unverified_citations": unverified_citations,
            "is_grounded": len(unverified_citations) == 0
        }

    def validate_output(
        self,
        response_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Post-execution output guardrail inspecting for leaks and verifying grounding.
        """
        # Secret check on output
        cleaned_response, leaked_secrets = scan_and_redact_secrets(response_text)
        citation_check = self.validate_citations(cleaned_response, retrieved_chunks)

        return {
            "sanitized_response": cleaned_response,
            "leaked_secrets_redacted": leaked_secrets,
            "citations": citation_check
        }


# Singleton
security_validator = SecurityValidator()
