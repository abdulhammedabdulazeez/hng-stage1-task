"""
Business logic for string analysis and natural language processing.
"""

import hashlib
import logging
import re
from datetime import datetime, UTC
from typing import Dict, List, Optional
from .storage import strings_storage
from .schemas import StringProperties, StringResponse

logger = logging.getLogger(__name__)


def compute_sha256(text: str) -> str:
    """Generate SHA-256 hash of the input text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_palindrome(text: str) -> bool:
    """Check if text is a palindrome (case-insensitive)."""
    # Convert to lowercase and keep only alphanumeric characters
    cleaned = "".join(char.lower() for char in text if char.isalnum())
    return cleaned == cleaned[::-1]


def count_unique_characters(text: str) -> int:
    """Count distinct characters in the text."""
    return len(set(text))


def count_words(text: str) -> int:
    """Count words separated by whitespace."""
    return len(text.split())


def character_frequency(text: str) -> Dict[str, int]:
    """Build frequency map of characters in the text."""
    frequency_map = {}
    for char in text:
        frequency_map[char] = frequency_map.get(char, 0) + 1
    return frequency_map


def analyze_string(value: str) -> Dict:
    """Compute all properties and return full string object."""
    sha256_hash = compute_sha256(value)

    properties = StringProperties(
        length=len(value),
        is_palindrome=is_palindrome(value),
        unique_characters=count_unique_characters(value),
        word_count=count_words(value),
        sha256_hash=sha256_hash,
        character_frequency_map=character_frequency(value),
    )

    return {
        "id": sha256_hash,
        "value": value,
        "properties": properties.dict(),
        "created_at": datetime.now(UTC).isoformat(),
    }


def save_string(string_data: Dict) -> None:
    """Add string data to storage."""
    strings_storage.append(string_data)
    logger.info(f"String saved with ID: {string_data['id']}")


def find_string_by_value(value: str) -> Optional[Dict]:
    """Search storage by exact value match."""
    for string_data in strings_storage:
        if string_data["value"] == value:
            return string_data
    return None


def find_string_by_hash(hash_value: str) -> Optional[Dict]:
    """Search storage by SHA-256 hash."""
    for string_data in strings_storage:
        if string_data["id"] == hash_value:
            return string_data
    return None


def filter_strings(filters: Dict) -> List[Dict]:
    """Apply query parameter filters to stored strings."""
    filtered_strings = []

    for string_data in strings_storage:
        properties = string_data["properties"]
        include = True

        # Apply filters
        if "is_palindrome" in filters and filters["is_palindrome"] is not None:
            if properties["is_palindrome"] != filters["is_palindrome"]:
                include = False

        if "min_length" in filters and filters["min_length"] is not None:
            if properties["length"] < filters["min_length"]:
                include = False

        if "max_length" in filters and filters["max_length"] is not None:
            if properties["length"] > filters["max_length"]:
                include = False

        if "word_count" in filters and filters["word_count"] is not None:
            if properties["word_count"] != filters["word_count"]:
                include = False

        if (
            "contains_character" in filters
            and filters["contains_character"] is not None
        ):
            if filters["contains_character"] not in string_data["value"]:
                include = False

        if include:
            filtered_strings.append(string_data)

    return filtered_strings


def parse_natural_language(query: str) -> Dict:
    """Simple keyword matching for natural language queries."""
    query_lower = query.lower()
    filters = {}

    # Word count patterns
    if "single word" in query_lower or "one word" in query_lower:
        filters["word_count"] = 1

    # Palindrome patterns
    if "palindrome" in query_lower or "palindromic" in query_lower:
        filters["is_palindrome"] = True

    # Length patterns
    length_match = re.search(r"longer than (\d+)", query_lower)
    if length_match:
        filters["min_length"] = int(length_match.group(1)) + 1

    length_match = re.search(r"shorter than (\d+)", query_lower)
    if length_match:
        filters["max_length"] = int(length_match.group(1)) - 1

    # Character patterns
    char_match = re.search(
        r"contain(?:s|ing)?\s+(?:the\s+letter\s+)?([a-zA-Z])", query_lower
    )
    if char_match:
        filters["contains_character"] = char_match.group(1).lower()

    # First vowel pattern
    if "first vowel" in query_lower:
        filters["contains_character"] = "a"

    return filters


def delete_string_by_value(value: str) -> bool:
    """Delete string from storage by exact value match."""
    for i, string_data in enumerate(strings_storage):
        if string_data["value"] == value:
            del strings_storage[i]
            logger.info(f"String deleted: {value}")
            return True
    return False
