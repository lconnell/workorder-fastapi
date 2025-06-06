from typing import Any

from fastapi import (  # Added Response
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.work_orders import (  # Added PaginationInfo
    PaginationInfo,
    WorkOrder,
    WorkOrderCreate,
    WorkOrdersResponse,
    WorkOrderUpdate,
)
from app.services.auth import get_current_user_from_token
from app.services.supabase import get_supabase_client

security = HTTPBearer()

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.get("", response_model=WorkOrdersResponse)
async def get_work_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),  # Modified
    priority: str | None = None,  # Modified
    assigned_to: str | None = None,  # Modified
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> WorkOrdersResponse:
    """Get work orders with optional filtering and pagination."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        base_query = supabase.table("work_orders")

        filters = []
        if status_filter:
            filters.append(("status", "eq", status_filter))
            base_query = base_query.eq("status", status_filter)
        if priority:
            filters.append(("priority", "eq", priority))
            base_query = base_query.eq("priority", priority)
        if assigned_to:
            filters.append(("assigned_to_user_id", "eq", assigned_to))
            base_query = base_query.eq("assigned_to_user_id", assigned_to)

        offset = (page - 1) * limit

        data_response = (
            base_query.select("*, location:locations(*)")
            .range(offset, offset + limit - 1)
            .execute()
        )

        count_query_builder = supabase.table("work_orders")
        for col, op, val in filters:
            count_query_builder = getattr(count_query_builder, op)(col, val)
        count_response = count_query_builder.select("id", count="exact").execute()

        total_count = count_response.count if count_response.count is not None else 0
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 0

        pagination_info = {
            "page": page,
            "limit": limit,
            "total": total_count,
            "totalPages": total_pages,
        }

        return WorkOrdersResponse(
            data=data_response.data or [],
            count=total_count,
            pagination=PaginationInfo(**pagination_info),
        )
    except Exception as e:
        # Consider logging the error e.g.:
        # import logging
        # logging.exception("Error fetching work orders")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch work orders: {str(e)}",
        ) from e


@router.get("/{work_order_id}", response_model=WorkOrder)
async def get_work_order(
    work_order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> WorkOrder:
    """Get a specific work order by ID."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        response = (
            supabase.table("work_orders")
            .select("*, location:locations(*)")
            .eq("id", work_order_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found"
            )

        return WorkOrder(**response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch work order: {str(e)}",
        ) from e


@router.post("", response_model=WorkOrder, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    work_order: WorkOrderCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> WorkOrder:
    """Create a new work order."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        work_order_data = work_order.model_dump()
        work_order_data["created_by_user_id"] = current_user["id"]

        insert_response = (
            supabase.table("work_orders").insert(work_order_data).execute()
        )

        if not insert_response.data or len(insert_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create work order",
            )

        created_wo_id = insert_response.data[0].get("id")
        if not created_wo_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Created work order ID not found in response",
            )

        fetch_response = (
            supabase.table("work_orders")
            .select("*, location:locations(*)")
            .eq("id", created_wo_id)
            .single()
            .execute()
        )

        if not fetch_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch newly created work order with location details",
            )

        return WorkOrder(**fetch_response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create work order: {str(e)}",
        ) from e


@router.put("/{work_order_id}", response_model=WorkOrder)
async def update_work_order(
    work_order_id: str,
    work_order_update: WorkOrderUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> WorkOrder:
    """Update a work order."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        update_data = work_order_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
            )

        check_response = (
            supabase.table("work_orders")
            .select("id")
            .eq("id", work_order_id)
            .maybe_single()
            .execute()
        )
        if not check_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work order not found or not accessible",
            )

        update_response = (
            supabase.table("work_orders")
            .update(update_data)
            .eq("id", work_order_id)
            .execute()
        )

        if not update_response.data or len(update_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update work order, or no effective changes made.",
            )

        fetch_response = (
            supabase.table("work_orders")
            .select("*, location:locations(*)")
            .eq("id", work_order_id)
            .single()
            .execute()
        )
        if not fetch_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to fetch updated work order details.",
            )

        return WorkOrder(**fetch_response.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update work order: {str(e)}",
        ) from e


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_order(
    work_order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Response:
    """Delete a work order."""
    supabase = get_supabase_client()
    supabase.auth.set_session(credentials.credentials, "")

    try:
        check_response = (
            supabase.table("work_orders")
            .select("id")
            .eq("id", work_order_id)
            .maybe_single()
            .execute()
        )
        if not check_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work order not found or not accessible",
            )

        delete_response = (
            supabase.table("work_orders").delete().eq("id", work_order_id).execute()
        )

        if not delete_response.data or len(delete_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work order not found, or no rows deleted.",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete work order: {str(e)}",
        ) from e
