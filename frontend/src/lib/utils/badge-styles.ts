/**
 * Unified badge styling utilities for work order status and priority
 * Uses DaisyUI semantic badge classes with consistent DRY approach
 */

/**
 * Get status badge classes with optional variant and size
 */
export function getStatusBadgeClasses(
	status: string,
	variant: "default" | "soft" | "outline" = "default",
	size: "xs" | "sm" | "md" | "lg" = "md",
): string {
	const s = status?.toLowerCase() || "default";

	// Base semantic class
	let baseClass: string;
	switch (s) {
		case "open":
			baseClass = "badge-info";
			break;
		case "in progress":
		case "pending":
			baseClass = "badge-warning";
			break;
		case "on hold":
			baseClass = "badge-neutral";
			break;
		case "closed":
		case "completed":
		case "resolved":
			baseClass = "badge-success";
			break;
		case "cancelled":
		case "failed":
			baseClass = "badge-error";
			break;
		default:
			baseClass = "badge-neutral";
	}

	// Add variant modifier
	const variantClass =
		variant === "soft"
			? "badge-soft"
			: variant === "outline"
				? "badge-outline"
				: "";

	// Add size modifier
	const sizeClass = size !== "md" ? `badge-${size}` : "";

	return [baseClass, variantClass, sizeClass].filter(Boolean).join(" ");
}

/**
 * Get priority badge classes with optional variant and size
 */
export function getPriorityBadgeClasses(
	priority: string,
	variant: "default" | "soft" | "outline" = "outline",
	size: "xs" | "sm" | "md" | "lg" = "md",
): string {
	const p = priority?.toLowerCase() || "default";

	// Base semantic class and variant override for critical priorities
	let baseClass: string;
	let finalVariant = variant;
	switch (p) {
		case "low":
			baseClass = "badge-success";
			break;
		case "medium":
			baseClass = "badge-warning";
			break;
		case "high":
			baseClass = "badge-error";
			break;
		case "urgent":
		case "critical":
			baseClass = "badge-error";
			// Critical/urgent gets solid styling regardless of variant
			finalVariant = "default";
			break;
		default:
			baseClass = "badge-neutral";
	}

	// Add variant modifier
	const variantClass =
		finalVariant === "soft"
			? "badge-soft"
			: finalVariant === "outline"
				? "badge-outline"
				: "";

	// Add size modifier
	const sizeClass = size !== "md" ? `badge-${size}` : "";

	return [baseClass, variantClass, sizeClass].filter(Boolean).join(" ");
}

// Legacy functions for backward compatibility - use unified functions above instead
export const getModalStatusBadgeClasses = (status: string) =>
	getStatusBadgeClasses(status, "soft", "sm");
export const getModalPriorityBadgeClasses = (priority: string) =>
	getPriorityBadgeClasses(priority, "soft", "sm");
export const getTableStatusBadgeClasses = (status: string) =>
	getStatusBadgeClasses(status, "soft", "sm");
export const getTablePriorityBadgeClasses = (priority: string) =>
	getPriorityBadgeClasses(priority, "soft", "sm");
