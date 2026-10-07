import re
from typing import List, Dict, Any


class DocumentChunker:
    """
    Splits policy and SOP markdown documents into semantic chunks
    with clean section headers and overlap.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown(
        self,
        document_id: str,
        document_title: str,
        category: str,
        content: str
    ) -> List[Dict[str, Any]]:
        # Split by markdown headers first if present
        sections = re.split(r'\n(?=##?\s+)', content)
        chunks = []
        chunk_idx = 0

        for section in sections:
            section_clean = section.strip()
            if not section_clean:
                continue

            # Extract header if present
            header_match = re.match(r'^##?\s+(.*)', section_clean)
            section_title = header_match.group(1).strip() if header_match else "General"

            # If section is small enough, keep as single chunk
            if len(section_clean) <= self.chunk_size:
                chunks.append({
                    "chunk_id": f"{document_id}-C{chunk_idx + 1}",
                    "document_id": document_id,
                    "document_title": document_title,
                    "category": category,
                    "chunk_index": chunk_idx + 1,
                    "section_title": section_title,
                    "content": section_clean,
                    "metadata": {
                        "document_id": document_id,
                        "document_title": document_title,
                        "category": category,
                        "section_title": section_title,
                        "chunk_index": chunk_idx + 1
                    }
                })
                chunk_idx += 1
            else:
                # Sub-split into character chunks with overlap
                start = 0
                while start < len(section_clean):
                    end = start + self.chunk_size
                    piece = section_clean[start:end].strip()
                    if piece:
                        chunks.append({
                            "chunk_id": f"{document_id}-C{chunk_idx + 1}",
                            "document_id": document_id,
                            "document_title": document_title,
                            "category": category,
                            "chunk_index": chunk_idx + 1,
                            "section_title": section_title,
                            "content": piece,
                            "metadata": {
                                "document_id": document_id,
                                "document_title": document_title,
                                "category": category,
                                "section_title": section_title,
                                "chunk_index": chunk_idx + 1
                            }
                        })
                        chunk_idx += 1
                    start += self.chunk_size - self.chunk_overlap

        return chunks
