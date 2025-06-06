/**
 * Shared badge styling utilities for work order status and priority
 * Used across modals and tables for consistent styling
 */

interface BadgeClasses {
	bg: string;
	text: string;
	border?: string;
}

/**
 * Professional modal badge colors (more vibrant for emphasis)
 */
export function getModalStatusBadgeClasses(status: string): BadgeClasses {
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
}

export function getModalPriorityBadgeClasses(priority: string): BadgeClasses {
	const p = priority?.toLowerCase() || "default";
	switch (p) {
		case "low":
			return {
				bg: "bg-green-100",
				text: "text-green-800",
				border: "border-green-500",
			};
		case "medium":
			return {
				bg: "bg-yellow-100",
				text: "text-yellow-800",
				border: "border-yellow-500",
			};
		case "high":
			return {
				bg: "bg-red-100",
				text: "text-red-800",
				border: "border-red-500",
			};
		case "urgent":
		case "critical":
			return {
				bg: "bg-purple-100",
				text: "text-purple-800",
				border: "border-purple-500",
			};
		default:
			return {
				bg: "bg-gray-100",
				text: "text-gray-800",
				border: "border-gray-500",
			};
	}
}

/**
 * Subtle table badge colors (professional, low contrast)
 */
export function getTableStatusBadgeClasses(status: string): string {
	const s = status?.toLowerCase() || "";
	switch (s) {
		case "open":
			return "bg-blue-50 text-blue-700 border-blue-200";
		case "in progress":
			return "bg-amber-50 text-amber-700 border-amber-200";
		case "on hold":
			return "bg-purple-50 text-purple-700 border-purple-200";
		case "completed":
			return "bg-green-50 text-green-700 border-green-200";
		case "cancelled":
			return "bg-red-50 text-red-700 border-red-200";
		default:
			return "bg-gray-50 text-gray-700 border-gray-200";
	}
}

export function getTablePriorityBadgeClasses(priority: string): string {
	const p = priority?.toLowerCase() || "";
	switch (p) {
		case "low":
			return "bg-slate-50 text-slate-600 border-slate-200";
		case "medium":
			return "bg-blue-50 text-blue-600 border-blue-200";
		case "high":
			return "bg-orange-50 text-orange-700 border-orange-200";
		default:
			return "bg-gray-50 text-gray-600 border-gray-200";
	}
}
