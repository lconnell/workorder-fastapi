import { browser } from "$app/environment";
import type { Database } from "$lib/types/supabase";
import { type SupabaseClient, createClient } from "@supabase/supabase-js";

// Define an interface for the SvelteKit dev environment structure
interface SvelteKitDevEnv {
	__sveltekit_dev?: {
		env?: {
			PUBLIC_SUPABASE_URL?: string;
			PUBLIC_SUPABASE_ANON_KEY?: string;
			[key: string]: string | undefined;
		};
	};
}

let supabaseInstance: SupabaseClient<Database> | null = null;

function createSupabaseClient(): SupabaseClient<Database> {
	if (supabaseInstance) {
		return supabaseInstance;
	}

	// Only initialize on the client side
	if (!browser) {
		throw new Error("Supabase client can only be initialized in the browser");
	}

	// Try to get from import.meta.env first, fallback to global
	let supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
	let supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

	// Fallback to global sveltekit env if import.meta.env is empty
	if (!supabaseUrl || !supabaseAnonKey) {
		const globalEnv = (globalThis as SvelteKitDevEnv).__sveltekit_dev?.env;
		if (globalEnv) {
			supabaseUrl = supabaseUrl || globalEnv.PUBLIC_SUPABASE_URL;
			supabaseAnonKey = supabaseAnonKey || globalEnv.PUBLIC_SUPABASE_ANON_KEY;
		}
	}

	// Debug logging removed - environment variables are working

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
