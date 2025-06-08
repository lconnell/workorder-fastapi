/**
 * Toast notification system using DaisyUI alert components
 */

interface Toast {
	id: string;
	type: "success" | "error" | "warning" | "info";
	message: string;
	duration?: number;
}

class ToastStore {
	toasts = $state<Toast[]>([]);

	private generateId(): string {
		return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}

	add(type: Toast["type"], message: string, duration = 5000) {
		const id = this.generateId();
		const toast: Toast = { id, type, message, duration };

		this.toasts.push(toast);

		// Auto-remove after duration
		if (duration > 0) {
			setTimeout(() => {
				this.remove(id);
			}, duration);
		}

		return id;
	}

	remove(id: string) {
		const index = this.toasts.findIndex((t) => t.id === id);
		if (index > -1) {
			this.toasts.splice(index, 1);
		}
	}

	// Convenience methods
	success(message: string, duration?: number) {
		return this.add("success", message, duration);
	}

	error(message: string, duration?: number) {
		return this.add("error", message, duration);
	}

	warning(message: string, duration?: number) {
		return this.add("warning", message, duration);
	}

	info(message: string, duration?: number) {
		return this.add("info", message, duration);
	}

	clear() {
		this.toasts = [];
	}
}

export const toastStore = new ToastStore();
