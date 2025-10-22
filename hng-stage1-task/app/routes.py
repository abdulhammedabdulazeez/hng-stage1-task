"""
API routes for the String Analyzer Service.
"""

import logging
from urllib.parse import unquote
from fastapi import APIRouter, HTTPException, Request, status, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from .schemas import (
    StringAnalyzeRequest,
    StringResponse,
    StringListResponse,
    NaturalLanguageResponse,
    InterpretedQuery,
)
from .services import (
    analyze_string,
    save_string,
    find_string_by_value,
    filter_strings,
    parse_natural_language,
    delete_string_by_value,
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Create limiter instance for the router
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/strings", response_model=StringResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
async def create_string(request: Request, string_request: StringAnalyzeRequest):
    """
    Create/Analyze a string and store its computed properties.

    Returns:
        StringResponse: Analyzed string with all properties

    Raises:
        HTTPException: 400 if invalid request, 409 if string already exists
    """
    logger.info("POST /strings endpoint accessed")

    try:
        # Check if string already exists
        existing_string = find_string_by_value(string_request.value)
        if existing_string:
            logger.warning(f"String already exists: {string_request.value}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="String already exists in the system",
            )

        # Analyze the string
        string_data = analyze_string(string_request.value)

        # Save to storage
        save_string(string_data)

        logger.info(f"String analyzed and saved: {string_data['id']}")
        return StringResponse(**string_data)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in POST /strings: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )


@router.get("/strings/{string_value}", response_model=StringResponse)
@limiter.limit("20/minute")
async def get_string(request: Request, string_value: str):
    """
    Get a specific string by its value.

    Returns:
        StringResponse: The requested string with properties

    Raises:
        HTTPException: 404 if string not found
    """
    logger.info(f"GET /strings/{string_value} endpoint accessed")

    try:
        # URL decode the path parameter
        decoded_value = unquote(string_value)

        # Find the string
        string_data = find_string_by_value(decoded_value)
        if not string_data:
            logger.warning(f"String not found: {decoded_value}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="String does not exist in the system",
            )

        logger.info(f"String found: {string_data['id']}")
        return StringResponse(**string_data)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in GET /strings/{string_value}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )


@router.get("/strings", response_model=StringListResponse)
@limiter.limit("15/minute")
async def get_strings(
    request: Request,
    is_palindrome: Optional[bool] = Query(
        None, description="Filter by palindrome status"
    ),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum string length"),
    max_length: Optional[int] = Query(None, ge=0, description="Maximum string length"),
    word_count: Optional[int] = Query(None, ge=0, description="Exact word count"),
    contains_character: Optional[str] = Query(
        None, description="Character to search for"
    ),
):
    """
    Get all strings with optional filtering.

    Returns:
        StringListResponse: Filtered list of strings with count and applied filters
    """
    logger.info("GET /strings endpoint accessed")

    try:
        # Build filters dictionary
        filters = {}
        if is_palindrome is not None:
            filters["is_palindrome"] = is_palindrome
        if min_length is not None:
            filters["min_length"] = min_length
        if max_length is not None:
            filters["max_length"] = max_length
        if word_count is not None:
            filters["word_count"] = word_count
        if contains_character is not None:
            filters["contains_character"] = contains_character

        # Apply filters
        filtered_strings = filter_strings(filters)

        # Convert to response format
        string_responses = [
            StringResponse(**string_data) for string_data in filtered_strings
        ]

        # Build filters_applied for response
        filters_applied = {
            "is_palindrome": str(is_palindrome) if is_palindrome is not None else None,
            "min_length": str(min_length) if min_length is not None else None,
            "max_length": str(max_length) if max_length is not None else None,
            "word_count": str(word_count) if word_count is not None else None,
            "contains_character": contains_character,
        }

        logger.info(f"Found {len(string_responses)} strings matching filters")
        return StringListResponse(
            data=string_responses,
            count=len(string_responses),
            filters_applied=filters_applied,
        )

    except Exception as exc:
        logger.error(f"Error in GET /strings: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )


@router.get(
    "/strings/filter-by-natural-language", response_model=NaturalLanguageResponse
)
@limiter.limit("10/minute")
async def filter_by_natural_language(
    request: Request, query: str = Query(..., description="Natural language query")
):
    """
    Filter strings using natural language queries.

    Returns:
        NaturalLanguageResponse: Filtered strings with interpreted query

    Raises:
        HTTPException: 400 if unable to parse query, 422 if conflicting filters
    """
    logger.info(
        f"GET /strings/filter-by-natural-language endpoint accessed with query: {query}"
    )

    try:
        # Parse natural language query
        parsed_filters = parse_natural_language(query)

        if not parsed_filters:
            logger.warning(f"Unable to parse natural language query: {query}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to parse natural language query",
            )

        # Check for conflicting filters
        if "min_length" in parsed_filters and "max_length" in parsed_filters:
            if parsed_filters["min_length"] > parsed_filters["max_length"]:
                logger.warning("Conflicting filters: min_length > max_length")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Query parsed but resulted in conflicting filters",
                )

        # Apply filters
        filtered_strings = filter_strings(parsed_filters)

        # Convert to response format
        string_responses = [
            StringResponse(**string_data) for string_data in filtered_strings
        ]

        # Build interpreted query
        interpreted_query = InterpretedQuery(
            original=query, parsed_filters=parsed_filters
        )

        logger.info(
            f"Found {len(string_responses)} strings matching natural language query"
        )
        return NaturalLanguageResponse(
            data=string_responses,
            count=len(string_responses),
            interpreted_query=interpreted_query,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in GET /strings/filter-by-natural-language: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )


@router.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_string(request: Request, string_value: str):
    """
    Delete a string by its value.

    Returns:
        204 No Content if successful

    Raises:
        HTTPException: 404 if string not found
    """
    logger.info(f"DELETE /strings/{string_value} endpoint accessed")

    try:
        # URL decode the path parameter
        decoded_value = unquote(string_value)

        # Delete the string
        deleted = delete_string_by_value(decoded_value)
        if not deleted:
            logger.warning(f"String not found for deletion: {decoded_value}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="String does not exist in the system",
            )

        logger.info(f"String deleted successfully: {decoded_value}")
        return None

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in DELETE /strings/{string_value}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )
