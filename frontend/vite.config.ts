import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	// Set the third parameter to "" to load all env regardless of the `VITE_` prefix.
	const env = loadEnv(mode, process.cwd(), "");

	return {
		plugins: [tailwindcss(), sveltekit()],
		define: {
			"import.meta.env.PUBLIC_SUPABASE_URL": JSON.stringify(
				env.PUBLIC_SUPABASE_URL,
			),
			"import.meta.env.PUBLIC_SUPABASE_ANON_KEY": JSON.stringify(
				env.PUBLIC_SUPABASE_ANON_KEY,
			),
			"import.meta.env.PUBLIC_API_BASE_URL": JSON.stringify(
				env.PUBLIC_API_BASE_URL,
			),
		},
	};
});
