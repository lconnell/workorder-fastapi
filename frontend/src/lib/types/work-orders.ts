export interface Location {
	id: string;
	address?: string;
	city?: string;
	state_province?: string;
	postal_code?: string;
	country?: string;
	latitude?: number;
	longitude?: number;
}

export interface WorkOrder {
	id: string;
	title: string;
	description?: string;
	status: "Open" | "In Progress" | "Completed" | "Cancelled" | "On Hold";
	priority: "Low" | "Medium" | "High";
	location?: Location;
	location_id?: string;
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
	location_id?: string;
	assigned_to_user_id?: string;
}

export interface WorkOrderUpdate {
	title?: string;
	description?: string;
	status?: "Open" | "In Progress" | "Completed" | "Cancelled" | "On Hold";
	priority?: "Low" | "Medium" | "High";
	location_id?: string;
	assigned_to_user_id?: string;
}
