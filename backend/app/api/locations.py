from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.models.work_orders import Location
from app.services.auth import get_current_user_from_token
from app.services.supabase import get_supabase_client
from app.utils.logger import logger

security = HTTPBearer()

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationCreate(BaseModel):
    address: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str = "USA"
    latitude: float | None = None
    longitude: float | None = None


async def geocode_address(address_parts: dict) -> tuple[float | None, float | None]:
    """Geocode an address using OpenStreetMap Nominatim API."""
    if not any(address_parts.values()):
        logger.warning("No address parts provided for geocoding")
        return None, None

    # Build search query from available parts
    query_parts = [v for v in address_parts.values() if v]
    query = ", ".join(query_parts)
    logger.debug(f"Starting geocoding for query: '{query}'")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1, "addressdetails": 1},
                headers={"User-Agent": "WorkOrderApp/1.0"},
            )

            logger.debug(f"Nominatim API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Nominatim API returned {len(data)} results")
                if data:
                    lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
                    logger.log_geocoding(query, True, lat, lon)
                    return lat, lon
                else:
                    logger.log_geocoding(query, False, error="Empty results from API")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.log_geocoding(query, False, error=error_msg)
    except Exception as e:
        logger.log_geocoding(query, False, error=str(e))
        logger.error(
            f"Geocoding exception for '{query}'", {"exception": str(e)}, exc_info=True
        )
    return None, None


@router.post("", response_model=Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    location: LocationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Location:
    """Create a new location with automatic geocoding and duplicate prevention."""
    user_id = current_user.get("id", "Unknown")
    user_email = current_user.get("email", "No email")

    logger.info(
        "Location creation started",
        {
            "user_id": user_id,
            "user_email": user_email,
            "location_data": location.model_dump(),
        },
    )

    try:
        supabase = get_supabase_client()
        logger.debug("Supabase client created successfully")
        supabase.auth.set_session(credentials.credentials, "")
        logger.debug("Auth session set successfully")
    except Exception as auth_error:
        logger.error("Auth setup failed", {"user_id": user_id}, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication setup failed: {str(auth_error)}",
        ) from auth_error

    try:
        # Check for existing location with same address
        address_parts = {
            "address": location.address,
            "city": location.city,
            "state_province": location.state_province,
            "postal_code": location.postal_code,
        }

        # Check for existing location with same address components
        # Use a simpler approach - only check for duplicates if we have a street address
        if location.address and location.city and location.state_province:
            logger.debug(
                "Checking for duplicate location",
                {
                    "address": location.address,
                    "city": location.city,
                    "state_province": location.state_province,
                },
            )
            existing_response = (
                supabase.table("locations")
                .select("*")
                .eq("address", location.address)
                .eq("city", location.city)
                .eq("state_province", location.state_province)
                .execute()
            )

            if existing_response.data and len(existing_response.data) > 0:
                location_id = existing_response.data[0].get("id")
                logger.info(
                    "Found existing location, returning it",
                    {
                        "user_id": user_id,
                        "location_id": location_id,
                        "duplicate_prevented": True,
                    },
                )
                return Location(**existing_response.data[0])
            else:
                logger.debug(
                    "No existing location found, proceeding with creation",
                    {
                        "user_id": user_id,
                        "search_criteria": {
                            "address": location.address,
                            "city": location.city,
                            "state_province": location.state_province,
                        },
                    },
                )

        location_data = location.model_dump()

        # Only construct formatted address if no street address is provided
        if not location.address:
            # Build address from city, state, zip if street address is missing
            address_components = [
                location.city,
                location.state_province,
                location.postal_code,
            ]
            formatted_address = ", ".join([comp for comp in address_components if comp])

            if formatted_address:
                location_data["address"] = formatted_address

        # Auto-geocode if coordinates not provided
        if not location.latitude or not location.longitude:
            logger.debug(
                "Attempting to geocode address",
                {"user_id": user_id, "address_parts": address_parts},
            )
            lat, lon = await geocode_address(address_parts)

            if lat is None or lon is None:
                logger.warning(
                    "Geocoding failed - location will be created without coordinates",
                    {
                        "user_id": user_id,
                        "address_parts": address_parts,
                        "geocoding_failed": True,
                    },
                )
                location_data["latitude"] = None
                location_data["longitude"] = None
            else:
                logger.info(
                    "Geocoding successful",
                    {
                        "user_id": user_id,
                        "latitude": lat,
                        "longitude": lon,
                        "address_parts": address_parts,
                    },
                )
                location_data["latitude"] = lat
                location_data["longitude"] = lon

        logger.debug(
            "Creating new location in database",
            {"user_id": user_id, "location_data": location_data},
        )
        try:
            insert_response = (
                supabase.table("locations").insert(location_data).execute()
            )
            logger.debug(
                "Insert response received",
                {
                    "user_id": user_id,
                    "data_count": (
                        len(insert_response.data) if insert_response.data else 0
                    ),
                },
            )
        except Exception as insert_error:
            logger.error(
                "Database insert failed",
                {
                    "user_id": user_id,
                    "operation": "location_insert",
                    "error": str(insert_error),
                },
                exc_info=True,
            )
            raise

        if not insert_response.data or len(insert_response.data) == 0:
            logger.error(
                "Insert response data is empty",
                {"user_id": user_id, "response_data": insert_response.data},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create location",
            )

        created_location = insert_response.data[0]
        location_id = created_location.get("id")
        has_coordinates = bool(
            created_location.get("latitude") and created_location.get("longitude")
        )

        logger.info(
            "Location created successfully",
            {
                "user_id": user_id,
                "location_id": location_id,
                "has_coordinates": has_coordinates,
                "latitude": created_location.get("latitude"),
                "longitude": created_location.get("longitude"),
            },
        )

        # Add a warning message if geocoding failed
        if not has_coordinates:
            logger.warning(
                "Location created without coordinates - geocoding failed",
                {
                    "user_id": user_id,
                    "location_id": location_id,
                    "geocoding_failed": True,
                },
            )

        return Location(**created_location)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Location creation failed",
            {"user_id": user_id, "operation": "create_location", "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create location: {str(e)}",
        ) from e


@router.get("", response_model=list[Location])
async def get_locations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> list[Location]:
    """Get all locations."""
    user_id = current_user.get("id", "Unknown")

    logger.info("Fetching all locations", {"user_id": user_id})

    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        logger.debug("Fetching all locations from database", {"user_id": user_id})
        response = supabase.table("locations").select("*").execute()

        location_count = len(response.data) if response.data else 0
        logger.info(
            "Successfully fetched locations",
            {"user_id": user_id, "location_count": location_count},
        )

        return [Location(**location) for location in response.data or []]
    except Exception as e:
        logger.error(
            "Failed to fetch locations",
            {"user_id": user_id, "operation": "get_locations", "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch locations: {str(e)}",
        ) from e


@router.get("/{location_id}", response_model=Location)
async def get_location(
    location_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Location:
    """Get a specific location by ID."""
    user_id = current_user.get("id", "Unknown")

    logger.info(
        "Fetching specific location", {"user_id": user_id, "location_id": location_id}
    )

    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        logger.debug(
            "Fetching location by ID from database",
            {"user_id": user_id, "location_id": location_id},
        )

        response = (
            supabase.table("locations")
            .select("*")
            .eq("id", location_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            logger.warning(
                "Location not found", {"user_id": user_id, "location_id": location_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        logger.info(
            "Successfully fetched location",
            {"user_id": user_id, "location_id": location_id},
        )

        return Location(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to fetch location",
            {
                "user_id": user_id,
                "location_id": location_id,
                "operation": "get_location",
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch location: {str(e)}",
        ) from e


@router.post("/{location_id}/geocode", response_model=Location)
async def geocode_location(
    location_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Location:
    """Manually geocode an existing location that doesn't have coordinates."""
    user_id = current_user.get("id", "Unknown")

    logger.info(
        "Manual geocoding started", {"user_id": user_id, "location_id": location_id}
    )

    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        # Get the location
        logger.debug(
            "Fetching location for geocoding",
            {"user_id": user_id, "location_id": location_id},
        )

        location_response = (
            supabase.table("locations")
            .select("*")
            .eq("id", location_id)
            .maybe_single()
            .execute()
        )

        if not location_response.data:
            logger.warning(
                "Location not found for geocoding",
                {"user_id": user_id, "location_id": location_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        location_data = location_response.data

        # Build address for geocoding
        address_parts = {
            "address": location_data.get("address"),
            "city": location_data.get("city"),
            "state_province": location_data.get("state_province"),
            "postal_code": location_data.get("postal_code"),
        }

        logger.debug(
            "Starting manual geocoding",
            {
                "user_id": user_id,
                "location_id": location_id,
                "address_parts": address_parts,
            },
        )

        # Geocode the location
        lat, lon = await geocode_address(address_parts)

        if lat is None or lon is None:
            logger.warning(
                "Manual geocoding failed - no coordinates found",
                {
                    "user_id": user_id,
                    "location_id": location_id,
                    "address_parts": address_parts,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to geocode location - could not find coordinates",
            )

        # Update with coordinates
        logger.debug(
            "Updating location with geocoded coordinates",
            {
                "user_id": user_id,
                "location_id": location_id,
                "latitude": lat,
                "longitude": lon,
            },
        )

        update_response = (
            supabase.table("locations")
            .update({"latitude": lat, "longitude": lon})
            .eq("id", location_id)
            .execute()
        )

        if not update_response.data:
            logger.error(
                "Failed to update location with coordinates",
                {
                    "user_id": user_id,
                    "location_id": location_id,
                    "latitude": lat,
                    "longitude": lon,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update location with coordinates",
            )

        logger.info(
            "Location geocoded successfully",
            {
                "user_id": current_user.get("id", "Unknown"),
                "location_id": location_id,
                "latitude": lat,
                "longitude": lon,
            },
        )
        return Location(**update_response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to geocode location",
            {
                "user_id": current_user.get("id", "Unknown"),
                "location_id": location_id,
                "operation": "geocode_location",
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to geocode location: {str(e)}",
        ) from e
