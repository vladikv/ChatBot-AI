import re


_CANCELLATION_PATTERN = re.compile(
    r"\bcancel\b.{0,60}\border\s+#?\s*(\d+)\b"
    r"|\border\s+#?\s*(\d+)\b.{0,60}\bcancel\b",
    re.IGNORECASE,
)
_NEGATED_CANCELLATION_PATTERN = re.compile(
    r"\b(?:don['’]?t|do not|never|not|can['’]?t|cannot|won['’]?t|"
    r"wouldn['’]?t|shouldn['’]?t|needn['’]?t|no need to)\b"
    r".{0,60}\bcancel\b"
    r"|\bcancel\b.{0,60}\b(?:not|never|no|don['’]?t|do not|can['’]?t|cannot)\b",
    re.IGNORECASE,
)
_UNCERTAIN_CANCELLATION_PATTERN = re.compile(
    r"\b(?:should\s+(?:i|we|they)|might\s+(?:i|we|they)|may\s+(?:i|we|they)|"
    r"could\s+i|would\s+i|can\s+i|whether|maybe|perhaps|consider(?:ing)?|"
    r"thinking about|if\s+i|is it possible to)\b.{0,60}\bcancel\b"
    r"|\bcancel\b.{0,60}\b(?:maybe|perhaps|if|unless)\b",
    re.IGNORECASE,
)


def extract_cancellation_order_id(message):
    """Return an order ID only for a clear, affirmative cancellation request."""
    if _NEGATED_CANCELLATION_PATTERN.search(message):
        return None
    if _UNCERTAIN_CANCELLATION_PATTERN.search(message):
        return None

    match = _CANCELLATION_PATTERN.search(message)
    if not match:
        return None
    return match.group(1) or match.group(2)
