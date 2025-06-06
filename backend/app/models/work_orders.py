from enum import Enum

from pydantic import BaseModel


class WorkOrderStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"


class WorkOrderPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Location(BaseModel):
    id: str  # UUID as string
    name: str
    address: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class WorkOrder(BaseModel):
    id: str  # UUID as string
    title: str
    description: str | None = None
    status: WorkOrderStatus
    priority: WorkOrderPriority
    location: Location | None = None
    location_id: str | None = None  # UUID as string for location reference
    assigned_to_user_id: str | None = None
    created_by_user_id: str
    created_at: str
    updated_at: str


class WorkOrderCreate(BaseModel):
    title: str
    description: str | None = None
    status: WorkOrderStatus = WorkOrderStatus.OPEN
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    location_id: str | None = None  # UUID as string
    assigned_to_user_id: str | None = None


class WorkOrderUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: WorkOrderStatus | None = None
    priority: WorkOrderPriority | None = None
    location_id: str | None = None  # UUID as string
    assigned_to_user_id: str | None = None


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int


class WorkOrdersResponse(BaseModel):
    data: list[WorkOrder]
    count: int
    pagination: PaginationInfo | None = None
