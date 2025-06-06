export interface Location {
	id: number;
	name: string;
	address?: string;
	city?: string;
	state_province?: string;
	postal_code?: string;
	country?: string;
}

export interface WorkOrder {
	id: number;
	title: string;
	description?: string;
	status: "Open" | "In Progress" | "Completed" | "Cancelled" | "On Hold";
	priority: "Low" | "Medium" | "High";
	location?: Location;
	location_id?: number;
	assigned_to_user_id?: string;
	created_by_user_id: string;
	created_at: string;
	updated_at: string;
}

export interface WorkOrdersResponse {
	data: WorkOrder[];
	count: number;
	pagination?: {
		page: number;
		limit: number;
		total: number;
		totalPages: number;
	};
}

export interface WorkOrderCreate {
	title: string;
	description?: string;
	status: "Open" | "In Progress" | "On Hold";
	priority: "Low" | "Medium" | "High";
	location_id?: number;
	assigned_to_user_id?: string;
}

export interface WorkOrderUpdate {
	title?: string;
	description?: string;
	status?: "Open" | "In Progress" | "Completed" | "Cancelled" | "On Hold";
	priority?: "Low" | "Medium" | "High";
	location_id?: number;
	assigned_to_user_id?: string;
}

export interface GeocodedLocation {
	lat: number;
	lon: number;
	address: string;
	workOrderCount: number;
	workOrders: WorkOrder[];
}

export interface GeocodingResult {
	lat: number;
	lon: number;
}
