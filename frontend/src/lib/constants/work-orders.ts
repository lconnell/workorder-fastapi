/**
 * Work Order related constants for consistent data handling
 */

export const WORK_ORDER_STATUSES = {
	OPEN: "Open",
	IN_PROGRESS: "In Progress",
	COMPLETED: "Completed",
	CANCELLED: "Cancelled",
	ON_HOLD: "On Hold",
} as const;

export const WORK_ORDER_PRIORITIES = {
	LOW: "Low",
	MEDIUM: "Medium",
	HIGH: "High",
} as const;

// Type definitions derived from constants
export type WorkOrderStatus =
	(typeof WORK_ORDER_STATUSES)[keyof typeof WORK_ORDER_STATUSES];
export type WorkOrderPriority =
	(typeof WORK_ORDER_PRIORITIES)[keyof typeof WORK_ORDER_PRIORITIES];

// Arrays for iteration (e.g., in dropdowns, filters)
export const WORK_ORDER_STATUS_OPTIONS = Object.values(WORK_ORDER_STATUSES);
export const WORK_ORDER_PRIORITY_OPTIONS = Object.values(WORK_ORDER_PRIORITIES);

// Active statuses for map filtering
export const ACTIVE_WORK_ORDER_STATUSES = [
	WORK_ORDER_STATUSES.OPEN,
	WORK_ORDER_STATUSES.IN_PROGRESS,
] as const;
