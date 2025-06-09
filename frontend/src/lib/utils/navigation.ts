/**
 * Navigation utilities for consistent link styling and behavior
 */

/**
 * Get CSS classes for navigation links based on current path
 * @param currentPath - The current page path
 * @param linkPath - The path of the navigation link
 * @returns CSS classes for active/inactive state
 */
export function getNavLinkClasses(
	currentPath: string,
	linkPath: string,
): string {
	if (linkPath === "/" && currentPath === "/") {
		return "bg-primary text-primary-content";
	}

	if (linkPath !== "/" && currentPath.startsWith(linkPath)) {
		return "bg-primary text-primary-content";
	}

	return "";
}

/**
 * Check if a navigation link is active
 * @param currentPath - The current page path
 * @param linkPath - The path of the navigation link
 * @returns Whether the link is active
 */
export function isNavLinkActive(
	currentPath: string,
	linkPath: string,
): boolean {
	if (linkPath === "/") {
		return currentPath === "/";
	}

	return currentPath.startsWith(linkPath);
}
