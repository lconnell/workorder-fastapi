# Code Cleanup Recommendations

## 1. Frontend: `/frontend/src/routes/workorders/+page.svelte`

### Issues:
- **Duplicate color mapping functions** - Similar badge coloring functions exist in both this file and WorkOrderModal.svelte
- **Inconsistent color schemes** - Different badge styles for table vs modal view
- **Unused imports** - STATUS_COLORS and PRIORITY_COLORS imported but not used (line 4)
- **Complex filtering logic** - Could be simplified

### Specific Changes:

1. **Remove unused imports** (line 4):
```typescript
// REMOVE THIS LINE:
import { API_ENDPOINTS } from "$lib/constants"; // STATUS_COLORS and PRIORITY_COLORS are now defined locally in this component

// CHANGE TO:
import { API_ENDPOINTS } from "$lib/constants";
```

2. **Extract badge styling to shared utility** - Create `/frontend/src/lib/utils/badges.ts`:
```typescript
// Create new file: /frontend/src/lib/utils/badges.ts
export const getStatusBadgeClasses = (status: string): { bg: string; text: string } => {
  const s = status?.toLowerCase() || "default";
  switch (s) {
    case "open":
      return { bg: "bg-sky-600", text: "text-sky-50" };
    case "in progress":
    case "pending":
      return { bg: "bg-amber-500", text: "text-amber-950" };
    case "on hold":
      return { bg: "bg-indigo-600", text: "text-indigo-50" };
    case "closed":
    case "completed":
    case "resolved":
      return { bg: "bg-emerald-600", text: "text-emerald-50" };
    case "cancelled":
    case "failed":
      return { bg: "bg-rose-600", text: "text-rose-50" };
    default:
      return { bg: "bg-slate-500", text: "text-slate-50" };
  }
};

export const getPriorityBadgeClasses = (priority: string): { bg: string; text: string; border: string } => {
  const p = priority?.toLowerCase() || "default";
  switch (p) {
    case "low":
      return { bg: "bg-green-100", text: "text-green-800", border: "border-green-500" };
    case "medium":
      return { bg: "bg-yellow-100", text: "text-yellow-800", border: "border-yellow-500" };
    case "high":
      return { bg: "bg-red-100", text: "text-red-800", border: "border-red-500" };
    case "urgent":
    case "critical":
      return { bg: "bg-purple-100", text: "text-purple-800", border: "border-purple-500" };
    default:
      return { bg: "bg-gray-100", text: "text-gray-800", border: "border-gray-500" };
  }
};

// For table view - simplified colors
export const getTableStatusColor = (status: string): string => {
  const s = status?.toLowerCase() || "";
  switch (s) {
    case "open": return "bg-blue-50 text-blue-700 border-blue-200";
    case "in progress": return "bg-amber-50 text-amber-700 border-amber-200";
    case "on hold": return "bg-purple-50 text-purple-700 border-purple-200";
    case "completed": return "bg-green-50 text-green-700 border-green-200";
    case "cancelled": return "bg-red-50 text-red-700 border-red-200";
    default: return "bg-gray-50 text-gray-700 border-gray-200";
  }
};

export const getTablePriorityColor = (priority: string): string => {
  const p = priority?.toLowerCase() || "";
  switch (p) {
    case "low": return "bg-slate-50 text-slate-600 border-slate-200";
    case "medium": return "bg-blue-50 text-blue-600 border-blue-200";
    case "high": return "bg-orange-50 text-orange-700 border-orange-200";
    default: return "bg-gray-50 text-gray-600 border-gray-200";
  }
};
```

3. **Remove duplicate functions** (lines 103-164, 225-246) and import from shared utility:
```typescript
import { getTableStatusColor, getTablePriorityColor } from "$lib/utils/badges";
```

4. **Simplify filter/sort logic** - Extract to computed functions:
```typescript
// Replace the complex $effect (lines 42-82) with:
const filteredAndSortedWorkOrders = $derived(() => {
  if (!$workOrdersQuery.data?.data) return [];

  let filtered = [...$workOrdersQuery.data.data];

  // Apply filters
  if (statusFilter !== "all") {
    filtered = filtered.filter(wo => wo.status === statusFilter);
  }
  if (priorityFilter !== "all") {
    filtered = filtered.filter(wo => wo.priority === priorityFilter);
  }

  // Apply sorting
  return filtered.sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];

    if (sortBy === "id") {
      aVal = String(aVal);
      bVal = String(bVal);
    } else if (sortBy === "created_at") {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    }

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });
});
```

## 2. Frontend: `/frontend/src/lib/components/WorkOrderModal.svelte`

### Issues:
- **Duplicate badge styling functions** - Same as workorders page
- **Unused constant imports** - PRIORITY_COLORS, STATUS_COLORS imported but not used
- **Duplicate interface definitions** - LocationCreate and Location interfaces already exist in types
- **Complex form handling** - Could be simplified
- **Empty console.log statements** - Should be removed (lines 44-54)

### Specific Changes:

1. **Remove duplicate interfaces** (lines 11-30) and import from shared types:
```typescript
import type { Location } from "$lib/types/work-orders";
```

2. **Remove unused imports** (line 3):
```typescript
// REMOVE:
import { API_ENDPOINTS, PRIORITY_COLORS, STATUS_COLORS } from "$lib/constants";

// CHANGE TO:
import { API_ENDPOINTS } from "$lib/constants";
```

3. **Remove empty console.log effect** (lines 44-54):
```typescript
// DELETE this entire $effect block
$effect(() => {
  // This $effect block previously contained console.log statements for debugging modal rendering conditions.
  // Logs have been removed, retaining the structure for clarity.
  if (isOpen && (workOrder || mode === "create")) {
    // Condition met: Modal would have rendered (log removed)
  } else if (isOpen && !workOrder && mode !== "create") {
    // Condition NOT met: workOrder is null and not in create mode (log removed)
  } else if (!isOpen) {
    // Condition NOT met: isOpen is false (log removed)
  }
});
```

4. **Remove duplicate badge functions** (lines 214-277) and import shared utilities:
```typescript
import { getStatusBadgeClasses, getPriorityBadgeClasses } from "$lib/utils/badges";
```

5. **Extract form validation logic**:
```typescript
// Create computed validation
const isFormValid = $derived(() => {
  return editForm.title.trim().length > 0;
});

const hasLocationData = $derived(() => {
  return editForm.location_address.trim() ||
         editForm.location_city.trim() ||
         editForm.location_state.trim() ||
         editForm.location_zip.trim();
});
```

## 3. Frontend: `/frontend/src/routes/+page.svelte`

### Issues:
- **Hardcoded API endpoint** - Should use constants
- **Duplicate work order status mapping** - Similar to other components
- **Complex statistics calculation** - Could be simplified

### Specific Changes:

1. **Use API_ENDPOINTS constant** (line 14):
```typescript
// CHANGE:
url: "/api/v1/work-orders",

// TO:
url: API_ENDPOINTS.WORK_ORDERS,

// Add import:
import { API_ENDPOINTS } from "$lib/constants";
```

2. **Extract statistics calculation**:
```typescript
// Create /frontend/src/lib/utils/statistics.ts
export const calculateWorkOrderStats = (workOrders: WorkOrder[]) => {
  return {
    open: workOrders.filter(wo => wo.status === "Open").length,
    inProgress: workOrders.filter(wo => wo.status === "In Progress").length,
    completed: workOrders.filter(wo => wo.status === "Completed").length,
    onHold: workOrders.filter(wo => wo.status === "On Hold").length,
    total: workOrders.length,
  };
};
```

3. **Simplify reactive stats** (lines 29-43):
```typescript
import { calculateWorkOrderStats } from "$lib/utils/statistics";

const stats = $derived(() => {
  if (!$workOrdersQuery.data?.data) {
    return { open: 0, inProgress: 0, completed: 0, onHold: 0, total: 0 };
  }
  return calculateWorkOrderStats($workOrdersQuery.data.data);
});
```

## 4. Backend: `/backend/app/api/locations.py`

### Issues:
- **Duplicate error handling patterns** - Similar try/catch blocks
- **Hardcoded geocoding service** - Could be made configurable
- **Complex duplicate checking logic** - Could be simplified

### Specific Changes:

1. **Extract common error handling**:
```python
# Create /backend/app/utils/error_handling.py
def handle_supabase_error(e: Exception, operation: str) -> HTTPException:
    """Standardized error handling for Supabase operations."""
    if isinstance(e, HTTPException):
        raise e
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to {operation}: {str(e)}"
    )
```

2. **Extract geocoding to separate service**:
```python
# Create /backend/app/services/geocoding.py
class GeocodingService:
    @staticmethod
    async def geocode_address(address_parts: dict) -> tuple[float | None, float | None]:
        """Geocode an address using OpenStreetMap Nominatim API."""
        # Move existing geocode_address function here
```

3. **Simplify duplicate checking** (lines 71-91):
```python
async def find_existing_location(supabase, location: LocationCreate) -> Location | None:
    """Check if location already exists."""
    query = supabase.table("locations").select("*")

    address_fields = ["address", "city", "state_province", "postal_code"]
    for field in address_fields:
        value = getattr(location, field)
        if value:
            query = query.eq(field, value)
        else:
            query = query.is_(field, None)

    response = query.maybe_single().execute()
    return Location(**response.data) if response.data else None
```

## 5. Backend: `/backend/app/api/work_orders.py`

### Issues:
- **Repetitive error handling** - Same pattern in every endpoint
- **Duplicate validation logic** - WorkOrder validation repeated
- **Complex query building** - Could be simplified
- **Inconsistent parameter naming** - status_filter vs status

### Specific Changes:

1. **Standardize parameter names** (line 32):
```python
# CHANGE:
status_filter: str | None = Query(None, alias="status"),  # Modified
priority: str | None = None,  # Modified
assigned_to: str | None = None,  # Modified

# TO:
status: str | None = None,
priority: str | None = None,
assigned_to: str | None = None,
```

2. **Extract query building logic**:
```python
# Create /backend/app/services/work_order_filters.py
class WorkOrderFilters:
    @staticmethod
    def apply_filters(query, status: str = None, priority: str = None, assigned_to: str = None):
        """Apply filters to work order query."""
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
        if assigned_to:
            query = query.eq("assigned_to_user_id", assigned_to)
        return query
```

3. **Extract WorkOrder validation**:
```python
# Create /backend/app/utils/validation.py
def validate_work_order_data(data: dict, operation: str) -> WorkOrder:
    """Validate and convert work order data."""
    try:
        return WorkOrder(**data)
    except Exception as validation_error:
        print(f"Error validating {operation} work order: {validation_error}")
        print(f"Raw data: {data}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data validation error: {str(validation_error)}"
        )
```

4. **Remove debug print statements** (lines 86-87, 133-134, 196-197, 271-272):
```python
# DELETE these debug print statements:
print(f"Error validating work order {item.get('id', 'unknown')}: {validation_error}")
print(f"Raw data: {item}")
```

## Summary of Benefits:

1. **DRY Principle**: Eliminates duplicate badge styling, error handling, and validation logic
2. **Maintainability**: Centralized utilities make changes easier
3. **Consistency**: Shared functions ensure consistent behavior across components
4. **Readability**: Simplified components focus on their core responsibilities
5. **Type Safety**: Shared interfaces prevent type mismatches
6. **Performance**: Computed values replace complex reactive effects
7. **Debugging**: Removes debug code and console logs

## Files to Create:
- `/frontend/src/lib/utils/badges.ts`
- `/frontend/src/lib/utils/statistics.ts`
- `/backend/app/utils/error_handling.py`
- `/backend/app/services/geocoding.py`
- `/backend/app/services/work_order_filters.py`
- `/backend/app/utils/validation.py`

## Files to Modify:
- `/frontend/src/routes/workorders/+page.svelte`
- `/frontend/src/lib/components/WorkOrderModal.svelte`
- `/frontend/src/routes/+page.svelte`
- `/backend/app/api/locations.py`
- `/backend/app/api/work_orders.py`
