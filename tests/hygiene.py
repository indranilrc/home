"""The repo is public: no SLB-internal identifiers in any tracked file.

Client, location, and internal program names are listed only as SHA-256
hashes so this denylist does not itself publish them. Add a term with:
    python -c "import hashlib;print(hashlib.sha256(b'term').hexdigest())"
(lowercase; one or two words).
"""
import hashlib
import re
HASHED = {
    "05f84363a37b42906a9b2bc8de3fc38cab17c76fa7605c03eb950d49aa56f846",
    "7221705240eeb3b502e302eb59624ceb96c3c9846d202c697066c38385c2f76e",
    "cd88c378b67f11bfa479b681c9cb19ddf251b9b41b8fc2e0df8ce0a271d16dda",
    "31a03e012b7851643e14ff2fe01e13746c10171dec9e38f7ecf52cecf31af0b1",
    "1da1f5bde3c3ecf4148613cac321461fbc53ca2f9bbc51d1dd3d761c19b231e7",
}


def terms(text: str):
    words = re.findall(r"[a-z0-9-]+", text.lower())
    yield from words
    yield from (f"{a} {b}" for a, b in zip(words, words[1:]))


def denylisted(text: str) -> int:
    """Number of distinct denylisted terms in text (never returns the terms)."""
    return sum(1 for t in set(terms(text)) if hashlib.sha256(t.encode()).hexdigest() in HASHED)
