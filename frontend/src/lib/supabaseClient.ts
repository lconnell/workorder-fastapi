import { browser } from "$app/environment";
import type { Database } from "$lib/types/supabase";
import { type SupabaseClient, createClient } from "@supabase/supabase-js";

let supabaseInstance: SupabaseClient<Database> | null = null;

function createSupabaseClient(): SupabaseClient<Database> {
	if (supabaseInstance) {
		return supabaseInstance;
	}

	// Only initialize on the client side
	if (!browser) {
		throw new Error("Supabase client can only be initialized in the browser");
	}

	// Attempt to get environment variables
	const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
	const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

	if (!supabaseUrl || !supabaseAnonKey) {
		throw new Error(
			`Supabase URL and Anon Key must be provided in .env (PUBLIC_SUPABASE_URL: ${supabaseUrl}, PUBLIC_SUPABASE_ANON_KEY: ${supabaseAnonKey ? "present" : "missing"})`,
		);
	}

	supabaseInstance = createClient<Database>(supabaseUrl, supabaseAnonKey, {
		auth: {
			flowType: "pkce",
		},
	});

	return supabaseInstance;
}

// Create a lazy supabase client that only initializes when actually used
export const supabase = new Proxy({} as SupabaseClient<Database>, {
	get(target, prop, receiver) {
		// Only try to create client if we're in the browser
		if (!browser) {
			throw new Error("Supabase client can only be used in the browser");
		}

		// Delay initialization until actually needed
		const client = createSupabaseClient();
		const value = client[prop as keyof SupabaseClient<Database>];

		// If it's a function, bind it to the client
		if (typeof value === "function") {
			return value.bind(client);
		}

		return value;
	},
});
