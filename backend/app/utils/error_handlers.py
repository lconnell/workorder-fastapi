"""
Shared error handling utilities for API endpoints
"""

from typing import Any

from fastapi import HTTPException, status


def handle_supabase_error(
    error: Exception, operation: str, entity: str = "resource"
) -> HTTPException:
    """
    Standardized error handling for Supabase operations

    Args:
        error: The exception that occurred
        operation: Description of the operation (e.g., "create", "fetch", "update")
        entity: The entity being operated on (e.g., "work order", "location")

    Returns:
        HTTPException: Properly formatted HTTP exception
    """
    error_msg = str(error)

    # Handle common Supabase errors
    if "not found" in error_msg.lower():
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity.title()} not found"
        )
    elif "already exists" in error_msg.lower():
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity.title()} already exists",
        )
    elif "unauthorized" in error_msg.lower() or "permission" in error_msg.lower():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions to {operation} {entity}",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {operation} {entity}: {error_msg}",
        )


def validate_supabase_response(
    response: Any, operation: str, entity: str = "resource"
) -> None:
    """
    Validate Supabase response and raise appropriate errors

    Args:
        response: The Supabase response object
        operation: Description of the operation
        entity: The entity being operated on

    Raises:
        HTTPException: If response is invalid or empty
    """
    if not response or not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {operation} {entity} - no data returned",
        )

    if isinstance(response.data, list) and len(response.data) == 0:
        if operation in ["create", "update"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Failed to {operation} {entity} - operation returned no results"
                ),
            )


def create_not_found_error(entity: str, identifier: str | None = None) -> HTTPException:
    """Create a standardized 404 error"""
    detail = f"{entity.title()} not found"
    if identifier:
        detail += f" with ID: {identifier}"

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def create_validation_error(message: str) -> HTTPException:
    """Create a standardized validation error"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {message}"
    )
