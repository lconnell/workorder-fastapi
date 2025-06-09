import type {
	AxiosError,
	AxiosRequestConfig,
	InternalAxiosRequestConfig,
} from "axios";
import axios from "axios";
import { supabase } from "../supabaseClient";
import { logger } from "../utils/logger";

// Extend the Axios config to include our metadata
interface ConfigWithMetadata extends InternalAxiosRequestConfig {
	metadata?: {
		startTime: number;
	};
}

const API_BASE_URL =
	import.meta.env.PUBLIC_API_BASE_URL || "http://localhost:8000";

const axiosInstance = axios.create({
	baseURL: API_BASE_URL,
	timeout: 30000,
	headers: {
		"Content-Type": "application/json",
	},
});

// Request interceptor to add auth token and log requests
axiosInstance.interceptors.request.use(
	async (config: ConfigWithMetadata) => {
		const startTime = Date.now();
		config.metadata = { startTime };

		const {
			data: { session },
		} = await supabase.auth.getSession();

		if (session?.access_token) {
			config.headers.Authorization = `Bearer ${session.access_token}`;
		}

		logger.debug(
			`API Request: ${config.method?.toUpperCase()} ${config.url}`,
			"ApiClient",
			{
				url: config.url,
				method: config.method,
				data: config.data,
				params: config.params,
			},
		);

		return config;
	},
	(error) => {
		logger.error("API Request failed", "ApiClient", error);
		return Promise.reject(error);
	},
);

// Response interceptor for error handling and logging
axiosInstance.interceptors.response.use(
	(response) => {
		const config = response.config as ConfigWithMetadata;
		const duration = config.metadata?.startTime
			? Date.now() - config.metadata.startTime
			: undefined;

		logger.logApiRequest(
			response.config.method?.toUpperCase() || "UNKNOWN",
			response.config.url || "unknown",
			duration,
			response.status,
			response.data,
		);

		return response;
	},
	async (error: AxiosError) => {
		const config = error.config as ConfigWithMetadata;
		const duration = config?.metadata?.startTime
			? Date.now() - config.metadata.startTime
			: undefined;

		logger.logApiRequest(
			error.config?.method?.toUpperCase() || "UNKNOWN",
			error.config?.url || "unknown",
			duration,
			error.response?.status,
			{
				error: error.message,
				response: error.response?.data,
			},
		);

		if (error.response?.status === 401) {
			logger.warning(
				"Authentication token expired, attempting refresh",
				"ApiClient",
			);

			// Token might be expired, try to refresh
			const { error: refreshError } = await supabase.auth.refreshSession();

			if (!refreshError && error.config) {
				logger.info(
					"Token refreshed successfully, retrying request",
					"ApiClient",
				);
				// Retry the original request with new token
				return axiosInstance(error.config);
			}

			// If refresh failed, sign out
			logger.error("Token refresh failed, signing out user", "ApiClient");
			await supabase.auth.signOut();
			window.location.href = "/login";
		}

		return Promise.reject(error);
	},
);

// Orval client wrapper function
export const clientWrapper = async <T>(
	config: AxiosRequestConfig,
): Promise<T> => {
	const response = await axiosInstance(config);
	return response.data;
};

export default axiosInstance;
