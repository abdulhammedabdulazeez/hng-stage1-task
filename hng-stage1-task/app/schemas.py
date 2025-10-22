"""
Pydantic models for the String Analyzer Service.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional


class StringAnalyzeRequest(BaseModel):
    """Request model for analyzing a string."""

    value: str


class StringProperties(BaseModel):
    """Properties of an analyzed string."""

    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]


class StringResponse(BaseModel):
    """Response model for a single analyzed string."""

    id: str
    value: str
    properties: StringProperties
    created_at: str


class StringListResponse(BaseModel):
    """Response model for listing strings with filters."""

    data: List[StringResponse]
    count: int
    filters_applied: Dict[str, Optional[str]]


class InterpretedQuery(BaseModel):
    """Parsed natural language query."""

    original: str
    parsed_filters: Dict[str, str]


class NaturalLanguageResponse(BaseModel):
    """Response model for natural language filtering."""

    data: List[StringResponse]
    count: int
    interpreted_query: InterpretedQuery
