"""
core/disease_matcher.py — Fuzzy matching and disease extraction from user queries.
"""

from rapidfuzz import process, fuzz


def extract_disease_from_question(question, disease_list):
    """
    Try to find a disease name directly mentioned in the question.
    Uses exact substring matching (case-insensitive).
    """
    question_lower = question.lower()
    # Sort by length descending to match longer disease names first
    # (e.g., "Common Cold" before "Cold")
    sorted_diseases = sorted(disease_list, key=len, reverse=True)
    for disease in sorted_diseases:
        if disease.lower() in question_lower:
            return disease
    return None


def fuzzy_match_disease(question, disease_list, threshold=70):
    """
    Use fuzzy matching to find the best disease match for a query.
    Returns the best match if score >= threshold, else None.
    """
    question_lower = question.lower().strip()
    disease_lower_map = {d.lower(): d for d in disease_list}

    # Check exact match first
    if question_lower in disease_lower_map:
        return disease_lower_map[question_lower]

    # Try fuzzy matching against disease names
    best_match = process.extractOne(
        question_lower,
        list(disease_lower_map.keys()),
        scorer=fuzz.token_sort_ratio
    )

    if best_match and best_match[1] >= threshold:
        return disease_lower_map[best_match[0]]

    return None


def find_disease_in_query(question, disease_list, last_disease=None):
    """
    Main disease detection pipeline:
    1. Try exact substring match
    2. Try fuzzy matching
    3. Fall back to last_disease if user refers to "this disease" / "it"

    Returns (disease_name, method) or (None, None)
    """
    # Step 1: Exact substring match
    exact = extract_disease_from_question(question, disease_list)
    if exact:
        return exact, "exact"

    # Step 2: Fuzzy match
    fuzzy = fuzzy_match_disease(question, disease_list)
    if fuzzy:
        return fuzzy, "fuzzy"

    # Step 3: Context-based (refers to previous disease)
    context_phrases = ["this disease", "this", "that disease", "that", "the same", "it"]
    if last_disease and any(phrase in question.lower() for phrase in context_phrases):
        return last_disease, "context"

    return None, None
