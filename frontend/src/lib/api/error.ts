// Centralized API error extraction helper for type-safe, DRY error handling
// Returns the most user-friendly error message possible from API error responses

export function extractApiError(
	error: unknown,
	fallbackMessage: string,
): string {
	if (error && typeof error === "object") {
		// Handle FastAPI single string detail (most common for simple errors)
		if (
			"detail" in error &&
			typeof (error as { detail: unknown }).detail === "string"
		) {
			return (error as { detail: string }).detail;
		}

		// Handle FastAPI HTTPValidationError (array of errors, e.g., from Pydantic)
		// Example: error.detail = [{ loc: ..., msg: ..., type: ... }]
		if (
			"detail" in error &&
			Array.isArray((error as { detail: unknown }).detail) &&
			(error as { detail: unknown[] }).detail.length > 0
		) {
			const firstError = (error as { detail: { msg?: string }[] }).detail[0];
			if (
				firstError &&
				typeof firstError === "object" &&
				"msg" in firstError &&
				typeof firstError.msg === "string"
			) {
				return firstError.msg; // Or join all messages, or format them as needed
			}
		}

		// Handle a more generic "message" property if detail is not found or not in expected format
		if (
			"message" in error &&
			typeof (error as { message: unknown }).message === "string"
		) {
			return (error as { message: string }).message;
		}
	}

	// Handle network errors or other non-API errors that might be Error instances
	if (error instanceof Error) {
		return error.message;
	}

	return fallbackMessage;
}
