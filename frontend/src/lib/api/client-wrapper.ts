import type { AxiosError, AxiosRequestConfig } from "axios";
import axios from "axios";
import { supabase } from "../supabaseClient";

const API_BASE_URL =
	import.meta.env.PUBLIC_API_BASE_URL || "http://localhost:8000";

const axiosInstance = axios.create({
	baseURL: API_BASE_URL,
	timeout: 30000,
	headers: {
		"Content-Type": "application/json",
	},
});

// Request interceptor to add auth token
axiosInstance.interceptors.request.use(
	async (config) => {
		const {
			data: { session },
		} = await supabase.auth.getSession();

		if (session?.access_token) {
			config.headers.Authorization = `Bearer ${session.access_token}`;
		}

		return config;
	},
	(error) => {
		return Promise.reject(error);
	},
);

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
	(response) => response,
	async (error: AxiosError) => {
		if (error.response?.status === 401) {
			// Token might be expired, try to refresh
			const { error: refreshError } = await supabase.auth.refreshSession();

			if (!refreshError && error.config) {
				// Retry the original request with new token
				return axiosInstance(error.config);
			}

			// If refresh failed, sign out
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
