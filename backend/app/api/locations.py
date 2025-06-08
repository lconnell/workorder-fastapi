from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.models.work_orders import Location
from app.services.auth import get_current_user_from_token
from app.services.supabase import get_supabase_client

security = HTTPBearer()

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationCreate(BaseModel):
    name: str
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
        return None, None

    # Build search query from available parts
    query_parts = [v for v in address_parts.values() if v]
    query = ", ".join(query_parts)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1, "addressdetails": 1},
                headers={"User-Agent": "WorkOrderApp/1.0"},
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding failed for '{query}': {e}")

    return None, None


@router.post("", response_model=Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    location: LocationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Location:
    """Create a new location with automatic geocoding and duplicate prevention."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        # Check for existing location with same address
        address_parts = {
            "address": location.address,
            "city": location.city,
            "state_province": location.state_province,
            "postal_code": location.postal_code,
        }

        # Build query for existing location
        existing_query = supabase.table("locations").select("*")
        for field, value in address_parts.items():
            if value:
                existing_query = existing_query.eq(field, value)
            else:
                existing_query = existing_query.is_(field, None)

        existing_response = existing_query.maybe_single().execute()

        if existing_response and existing_response.data:
            # Return existing location instead of creating duplicate
            return Location(**existing_response.data)

        location_data = location.model_dump()

        # Always construct complete formatted address from components
        # This ensures location.address always contains the full address
        address_components = [
            location.address,
            location.city,
            location.state_province,
            location.postal_code,
        ]
        formatted_address = ", ".join([comp for comp in address_components if comp])

        if formatted_address:
            location_data["address"] = formatted_address
        elif location.name:
            # Fallback to name if no address components provided
            location_data["address"] = location.name
        else:
            # Ensure we always have something in the address field
            location_data["address"] = "Location Address Not Specified"

        # Auto-geocode if coordinates not provided
        if not location.latitude or not location.longitude:
            lat, lon = await geocode_address(address_parts)
            location_data["latitude"] = lat
            location_data["longitude"] = lon

        insert_response = supabase.table("locations").insert(location_data).execute()

        if not insert_response.data or len(insert_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create location",
            )

        created_location = insert_response.data[0]
        return Location(**created_location)
    except HTTPException:
        raise
    except Exception as e:
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
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        response = supabase.table("locations").select("*").execute()
        return [Location(**location) for location in response.data or []]
    except Exception as e:
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
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        response = (
            supabase.table("locations")
            .select("*")
            .eq("id", location_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        return Location(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch location: {str(e)}",
        ) from e
