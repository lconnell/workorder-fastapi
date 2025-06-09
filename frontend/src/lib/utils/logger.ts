/**
 * Comprehensive logging system for the Work Order frontend application.
 * Provides structured logging with proper log levels and formatting.
 */

export enum LogLevel {
	DEBUG = "DEBUG",
	INFO = "INFO",
	WARNING = "WARNING",
	ERROR = "ERROR",
	CRITICAL = "CRITICAL",
}

export interface LogEntry {
	timestamp: string;
	level: LogLevel;
	message: string;
	component?: string;
	data?: unknown;
	userId?: string;
	sessionId?: string;
	userAgent?: string;
	url?: string;
}

export interface LoggerConfig {
	enableConsole: boolean;
	enableLocalStorage: boolean;
	maxLocalStorageEntries: number;
	logLevel: LogLevel;
	includeStackTrace: boolean;
}

class WorkOrderLogger {
	private config: LoggerConfig;
	private sessionId: string;
	private readonly STORAGE_KEY = "workorder_logs";

	constructor(config?: Partial<LoggerConfig>) {
		this.config = {
			enableConsole: true,
			enableLocalStorage: this.isDebugEnabled(),
			maxLocalStorageEntries: 1000,
			logLevel: this.isDebugEnabled() ? LogLevel.DEBUG : LogLevel.INFO,
			includeStackTrace: this.isDebugEnabled(),
			...config,
		};

		this.sessionId = this.generateSessionId();
	}

	private isDebugEnabled(): boolean {
		if (typeof window !== "undefined") {
			return (
				window.location.search.includes("debug=true") ||
				localStorage.getItem("DEBUG") === "true" ||
				// @ts-ignore - Vite environment variables
				import.meta.env.VITE_DEBUG === "true"
			);
		}
		// @ts-ignore - Vite environment variables
		return import.meta.env.VITE_DEBUG === "true";
	}

	private generateSessionId(): string {
		return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
	}

	private shouldLog(level: LogLevel): boolean {
		const levels = [
			LogLevel.DEBUG,
			LogLevel.INFO,
			LogLevel.WARNING,
			LogLevel.ERROR,
			LogLevel.CRITICAL,
		];
		const currentLevelIndex = levels.indexOf(this.config.logLevel);
		const messageLevelIndex = levels.indexOf(level);
		return messageLevelIndex >= currentLevelIndex;
	}

	private createLogEntry(
		level: LogLevel,
		message: string,
		component?: string,
		data?: unknown,
	): LogEntry {
		const entry: LogEntry = {
			timestamp: new Date().toISOString(),
			level,
			message,
			sessionId: this.sessionId,
		};

		if (component) entry.component = component;
		if (data !== undefined) entry.data = data;

		if (typeof window !== "undefined") {
			entry.url = window.location.href;
			entry.userAgent = navigator.userAgent;
		}

		return entry;
	}

	private writeToConsole(entry: LogEntry): void {
		if (!this.config.enableConsole) return;

		const timestamp = new Date(entry.timestamp).toLocaleTimeString();
		const prefix = `[${timestamp}] ${entry.level}`;
		const component = entry.component ? ` [${entry.component}]` : "";
		const message = `${prefix}${component}: ${entry.message}`;

		switch (entry.level) {
			case LogLevel.DEBUG:
				console.debug(message, entry.data || "");
				break;
			case LogLevel.INFO:
				console.info(message, entry.data || "");
				break;
			case LogLevel.WARNING:
				console.warn(message, entry.data || "");
				break;
			case LogLevel.ERROR:
			case LogLevel.CRITICAL:
				console.error(message, entry.data || "");
				if (this.config.includeStackTrace) {
					console.trace();
				}
				break;
		}
	}

	private writeToLocalStorage(entry: LogEntry): void {
		if (!this.config.enableLocalStorage) return;

		try {
			const existingLogs = this.getStoredLogs();
			existingLogs.push(entry);

			// Keep only the most recent entries
			const trimmedLogs = existingLogs.slice(
				-this.config.maxLocalStorageEntries,
			);

			localStorage.setItem(this.STORAGE_KEY, JSON.stringify(trimmedLogs));
		} catch (error) {
			console.warn("Failed to write log to localStorage:", error);
		}
	}

	private getStoredLogs(): LogEntry[] {
		try {
			const stored = localStorage.getItem(this.STORAGE_KEY);
			return stored ? JSON.parse(stored) : [];
		} catch (error) {
			console.warn("Failed to read logs from localStorage:", error);
			return [];
		}
	}

	private log(
		level: LogLevel,
		message: string,
		component?: string,
		data?: unknown,
	): void {
		if (!this.shouldLog(level)) return;

		const entry = this.createLogEntry(level, message, component, data);

		this.writeToConsole(entry);
		this.writeToLocalStorage(entry);
	}

	// Public logging methods
	debug(message: string, component?: string, data?: unknown): void {
		this.log(LogLevel.DEBUG, message, component, data);
	}

	info(message: string, component?: string, data?: unknown): void {
		this.log(LogLevel.INFO, message, component, data);
	}

	warning(message: string, component?: string, data?: unknown): void {
		this.log(LogLevel.WARNING, message, component, data);
	}

	error(message: string, component?: string, data?: unknown): void {
		this.log(LogLevel.ERROR, message, component, data);
	}

	critical(message: string, component?: string, data?: unknown): void {
		this.log(LogLevel.CRITICAL, message, component, data);
	}

	// Specialized logging methods
	logApiRequest(
		method: string,
		url: string,
		duration?: number,
		status?: number,
		data?: unknown,
	): void {
		const logData = {
			type: "api_request",
			method,
			url,
			duration_ms: duration,
			status,
			data,
		};

		if (status && status >= 400) {
			this.error(
				`API ${method} ${url} failed with status ${status}`,
				"ApiClient",
				logData,
			);
		} else {
			this.debug(
				`API ${method} ${url}${duration ? ` (${duration}ms)` : ""}`,
				"ApiClient",
				logData,
			);
		}
	}

	logComponentMount(componentName: string, props?: unknown): void {
		this.debug(`Component mounted: ${componentName}`, componentName, { props });
	}

	logComponentUnmount(componentName: string): void {
		this.debug(`Component unmounted: ${componentName}`, componentName);
	}

	logUserAction(
		action: string,
		component: string,
		data?: Record<string, unknown>,
	): void {
		this.info(`User action: ${action}`, component, {
			type: "user_action",
			action,
			...(data || {}),
		});
	}

	logNavigation(from: string, to: string): void {
		this.info(`Navigation: ${from} → ${to}`, "Router", {
			type: "navigation",
			from,
			to,
		});
	}

	logFormSubmission(
		formName: string,
		success: boolean,
		data?: Record<string, unknown>,
	): void {
		const level = success ? LogLevel.INFO : LogLevel.WARNING;
		this.log(
			level,
			`Form ${formName} ${success ? "submitted" : "failed"}`,
			"Forms",
			{
				type: "form_submission",
				form: formName,
				success,
				...(data || {}),
			},
		);
	}

	// Utility methods
	getLogs(level?: LogLevel, component?: string, limit?: number): LogEntry[] {
		let logs = this.getStoredLogs();

		if (level) {
			logs = logs.filter((log) => log.level === level);
		}

		if (component) {
			logs = logs.filter((log) => log.component === component);
		}

		if (limit) {
			logs = logs.slice(-limit);
		}

		return logs;
	}

	clearLogs(): void {
		try {
			localStorage.removeItem(this.STORAGE_KEY);
			this.info("Logs cleared", "Logger");
		} catch (error) {
			console.warn("Failed to clear logs:", error);
		}
	}

	exportLogs(): string {
		const logs = this.getStoredLogs();
		return JSON.stringify(logs, null, 2);
	}

	getConfig(): LoggerConfig {
		return { ...this.config };
	}

	updateConfig(newConfig: Partial<LoggerConfig>): void {
		this.config = { ...this.config, ...newConfig };
		this.info("Logger configuration updated", "Logger", newConfig);
	}
}

// Global logger instance
export const logger = new WorkOrderLogger();

// Backward compatibility functions
export const debugLog = (message: string, component?: string): void => {
	logger.debug(message, component);
};

export const debugLogObject = (
	label: string,
	obj: unknown,
	component?: string,
): void => {
	logger.debug(label, component, obj);
};

export const debugLogError = (
	label: string,
	error: unknown,
	component?: string,
): void => {
	logger.error(label, component, error);
};

export const isDebug = (): boolean => {
	return logger.getConfig().logLevel === LogLevel.DEBUG;
};
