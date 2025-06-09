export type Json =
	| string
	| number
	| boolean
	| null
	| { [key: string]: Json | undefined }
	| Json[];

export type Database = {
	graphql_public: {
		Tables: {
			[_ in never]: never;
		};
		Views: {
			[_ in never]: never;
		};
		Functions: {
			graphql: {
				Args: {
					operationName?: string;
					query?: string;
					variables?: Json;
					extensions?: Json;
				};
				Returns: Json;
			};
		};
		Enums: {
			[_ in never]: never;
		};
		CompositeTypes: {
			[_ in never]: never;
		};
	};
	public: {
		Tables: {
			locations: {
				Row: {
					address: string | null;
					city: string | null;
					country: string | null;
					created_at: string | null;
					id: string;
					latitude: number | null;
					longitude: number | null;
					postal_code: string | null;
					state_province: string | null;
					updated_at: string | null;
				};
				Insert: {
					address?: string | null;
					city?: string | null;
					country?: string | null;
					created_at?: string | null;
					id?: string;
					latitude?: number | null;
					longitude?: number | null;
					postal_code?: string | null;
					state_province?: string | null;
					updated_at?: string | null;
				};
				Update: {
					address?: string | null;
					city?: string | null;
					country?: string | null;
					created_at?: string | null;
					id?: string;
					latitude?: number | null;
					longitude?: number | null;
					postal_code?: string | null;
					state_province?: string | null;
					updated_at?: string | null;
				};
				Relationships: [];
			};
			parts: {
				Row: {
					created_at: string | null;
					description: string | null;
					id: number;
					name: string;
					quantity_on_hand: number;
					sku: string | null;
					updated_at: string | null;
				};
				Insert: {
					created_at?: string | null;
					description?: string | null;
					id?: number;
					name: string;
					quantity_on_hand?: number;
					sku?: string | null;
					updated_at?: string | null;
				};
				Update: {
					created_at?: string | null;
					description?: string | null;
					id?: number;
					name?: string;
					quantity_on_hand?: number;
					sku?: string | null;
					updated_at?: string | null;
				};
				Relationships: [];
			};
			profiles: {
				Row: {
					avatar_url: string | null;
					full_name: string | null;
					id: string;
					updated_at: string | null;
				};
				Insert: {
					avatar_url?: string | null;
					full_name?: string | null;
					id: string;
					updated_at?: string | null;
				};
				Update: {
					avatar_url?: string | null;
					full_name?: string | null;
					id?: string;
					updated_at?: string | null;
				};
				Relationships: [];
			};
			work_order_notes: {
				Row: {
					content: string;
					created_at: string | null;
					id: number;
					updated_at: string | null;
					user_id: string;
					work_order_id: string | null;
				};
				Insert: {
					content: string;
					created_at?: string | null;
					id?: number;
					updated_at?: string | null;
					user_id: string;
					work_order_id?: string | null;
				};
				Update: {
					content?: string;
					created_at?: string | null;
					id?: number;
					updated_at?: string | null;
					user_id?: string;
					work_order_id?: string | null;
				};
				Relationships: [
					{
						foreignKeyName: "work_order_notes_work_order_id_fkey";
						columns: ["work_order_id"];
						isOneToOne: false;
						referencedRelation: "work_orders";
						referencedColumns: ["id"];
					},
				];
			};
			work_order_parts: {
				Row: {
					added_at: string | null;
					id: number;
					notes: string | null;
					part_id: number;
					quantity_used: number;
					work_order_id: string | null;
				};
				Insert: {
					added_at?: string | null;
					id?: number;
					notes?: string | null;
					part_id: number;
					quantity_used?: number;
					work_order_id?: string | null;
				};
				Update: {
					added_at?: string | null;
					id?: number;
					notes?: string | null;
					part_id?: number;
					quantity_used?: number;
					work_order_id?: string | null;
				};
				Relationships: [
					{
						foreignKeyName: "work_order_parts_part_id_fkey";
						columns: ["part_id"];
						isOneToOne: false;
						referencedRelation: "parts";
						referencedColumns: ["id"];
					},
					{
						foreignKeyName: "work_order_parts_work_order_id_fkey";
						columns: ["work_order_id"];
						isOneToOne: false;
						referencedRelation: "work_orders";
						referencedColumns: ["id"];
					},
				];
			};
			work_orders: {
				Row: {
					assigned_to_user_id: string | null;
					created_at: string | null;
					created_by_user_id: string;
					description: string | null;
					due_date: string | null;
					id: string;
					location_id: string | null;
					priority: Database["public"]["Enums"]["work_order_priority"];
					status: Database["public"]["Enums"]["work_order_status"];
					title: string;
					updated_at: string | null;
				};
				Insert: {
					assigned_to_user_id?: string | null;
					created_at?: string | null;
					created_by_user_id: string;
					description?: string | null;
					due_date?: string | null;
					id?: string;
					location_id?: string | null;
					priority?: Database["public"]["Enums"]["work_order_priority"];
					status?: Database["public"]["Enums"]["work_order_status"];
					title: string;
					updated_at?: string | null;
				};
				Update: {
					assigned_to_user_id?: string | null;
					created_at?: string | null;
					created_by_user_id?: string;
					description?: string | null;
					due_date?: string | null;
					id?: string;
					location_id?: string | null;
					priority?: Database["public"]["Enums"]["work_order_priority"];
					status?: Database["public"]["Enums"]["work_order_status"];
					title?: string;
					updated_at?: string | null;
				};
				Relationships: [
					{
						foreignKeyName: "work_orders_assigned_to_user_id_fkey";
						columns: ["assigned_to_user_id"];
						isOneToOne: false;
						referencedRelation: "profiles";
						referencedColumns: ["id"];
					},
					{
						foreignKeyName: "work_orders_location_id_fkey";
						columns: ["location_id"];
						isOneToOne: false;
						referencedRelation: "locations";
						referencedColumns: ["id"];
					},
				];
			};
		};
		Views: {
			[_ in never]: never;
		};
		Functions: {
			[_ in never]: never;
		};
		Enums: {
			work_order_priority: "Low" | "Medium" | "High";
			work_order_status:
				| "Open"
				| "In Progress"
				| "On Hold"
				| "Completed"
				| "Cancelled";
		};
		CompositeTypes: {
			[_ in never]: never;
		};
	};
};

type DefaultSchema = Database[Extract<keyof Database, "public">];

export type Tables<
	DefaultSchemaTableNameOrOptions extends
		| keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
		| { schema: keyof Database },
	TableName extends DefaultSchemaTableNameOrOptions extends {
		schema: keyof Database;
	}
		? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
				Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
		: never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
	? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
			Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
			Row: infer R;
		}
		? R
		: never
	: DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
				DefaultSchema["Views"])
		? (DefaultSchema["Tables"] &
				DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
				Row: infer R;
			}
			? R
			: never
		: never;

export type TablesInsert<
	DefaultSchemaTableNameOrOptions extends
		| keyof DefaultSchema["Tables"]
		| { schema: keyof Database },
	TableName extends DefaultSchemaTableNameOrOptions extends {
		schema: keyof Database;
	}
		? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
		: never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
	? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
			Insert: infer I;
		}
		? I
		: never
	: DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
		? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
				Insert: infer I;
			}
			? I
			: never
		: never;

export type TablesUpdate<
	DefaultSchemaTableNameOrOptions extends
		| keyof DefaultSchema["Tables"]
		| { schema: keyof Database },
	TableName extends DefaultSchemaTableNameOrOptions extends {
		schema: keyof Database;
	}
		? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
		: never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
	? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
			Update: infer U;
		}
		? U
		: never
	: DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
		? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
				Update: infer U;
			}
			? U
			: never
		: never;

export type Enums<
	DefaultSchemaEnumNameOrOptions extends
		| keyof DefaultSchema["Enums"]
		| { schema: keyof Database },
	EnumName extends DefaultSchemaEnumNameOrOptions extends {
		schema: keyof Database;
	}
		? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
		: never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
	? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
	: DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
		? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
		: never;

export type CompositeTypes<
	PublicCompositeTypeNameOrOptions extends
		| keyof DefaultSchema["CompositeTypes"]
		| { schema: keyof Database },
	CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
		schema: keyof Database;
	}
		? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
		: never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
	? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
	: PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
		? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
		: never;

export const Constants = {
	graphql_public: {
		Enums: {},
	},
	public: {
		Enums: {
			work_order_priority: ["Low", "Medium", "High"],
			work_order_status: [
				"Open",
				"In Progress",
				"On Hold",
				"Completed",
				"Cancelled",
			],
		},
	},
} as const;
