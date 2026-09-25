import re
from typing import Optional, List, Tuple


def normalize_text(text: str) -> str:
    """Normalize whitespace and lowercases for uniform comparison."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def extract_sections(text: str) -> List[str]:
    """
    Extracts section references such as §4, §12, Section 4, sec. 18.
    """
    patterns = [
        r"§\s*(\d+)",
        r"(?:section|sec\.?)\s*(\d+)",
        r"ಸೆಕ್ಷನ್\s*(\d+)",
        r"धारा\s*(\d+)",
        r"సెక్షన్\s*(\d+)"
    ]
    sections = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            sections.append(f"§{m}")
    return list(dict.fromkeys(sections))


def extract_numbers_and_units(text: str) -> List[str]:
    """
    Extracts numeric claims with associated units (e.g., '30 calendar days', '5,000 credits', '80%').
    """
    pattern = r"(\d[\d,]*(?:\.\d+)?)\s*(calendar\s+days|business\s+days|days|hours|years|months|credits|decibels|liters|square\s+meters|%)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    results = [f"{num.replace(',', '')} {unit.lower()}" for num, unit in matches]
    return results


def check_exact_fact(expected: str, fact_type: str, actual_text: str) -> Tuple[str, str]:
    """
    Compares expected fact against actual text deterministically.
    Returns (status: PASS | FAIL | MISSING, reason: str).
    """
    norm_expected = normalize_text(expected)
    norm_actual = normalize_text(actual_text)

    if fact_type == "section":
        exp_sections = extract_sections(expected)
        act_sections = extract_sections(actual_text)
        if not exp_sections:
            if norm_expected in norm_actual:
                return "PASS", f"Section '{expected}' present."
            return "MISSING", f"Expected section '{expected}' not found."

        target_sec = exp_sections[0]
        if target_sec in act_sections:
            return "PASS", f"Section {target_sec} correctly identified."
        elif act_sections:
            return "FAIL", f"Expected {target_sec} but found {', '.join(act_sections)}."
        else:
            return "MISSING", f"Required section {target_sec} omitted from answer."

    elif fact_type in ["deadline", "number"]:
        # Extract clean digits & units
        exp_digits = re.findall(r"\d+", norm_expected)
        act_digits = re.findall(r"\d+", norm_actual)

        if not exp_digits:
            if norm_expected in norm_actual:
                return "PASS", f"Fact '{expected}' present."
            return "MISSING", f"Fact '{expected}' missing."

        target_digit = exp_digits[0]
        if target_digit in act_digits:
            # Check unit fidelity if specified (e.g. business vs calendar)
            if "business" in norm_expected and "calendar" in norm_actual:
                return "FAIL", f"Mismatch in unit specification: expected business days, got calendar days."
            if "calendar" in norm_expected and "business" in norm_actual:
                return "FAIL", f"Mismatch in unit specification: expected calendar days, got business days."
            return "PASS", f"Numeric value '{expected}' matched."
        elif act_digits:
            return "FAIL", f"Expected '{expected}' (value {target_digit}) but got alternative numbers: {act_digits}."
        else:
            return "MISSING", f"Numeric fact '{expected}' omitted."

    elif fact_type == "authority":
        # Check canonical authority terms
        if norm_expected in norm_actual:
            return "PASS", f"Authority '{expected}' verified."
        # Check core keyword match (e.g. 'urban administration', 'hazard response')
        words = [w for w in norm_expected.split() if len(w) > 4]
        matched_words = [w for w in words if w in norm_actual]
        if len(matched_words) >= max(1, len(words) // 2):
            return "PASS", f"Authority partially matched: {', '.join(matched_words)}."
        return "MISSING", f"Required authority '{expected}' not mentioned."

    # General entity / default check
    if norm_expected in norm_actual:
        return "PASS", f"Fact '{expected}' present."
    return "MISSING", f"Fact '{expected}' not found in answer."
