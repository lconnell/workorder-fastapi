const config = {
	api: {
		input: "./src/lib/api/openapi.json",
		output: {
			target: "./src/lib/api/client.ts",
			schemas: "./src/lib/api/schemas",
			client: "svelte-query",
			mode: "single",
			override: {
				mutator: {
					path: "./src/lib/api/client-wrapper.ts",
					name: "clientWrapper",
				},
			},
		},
	},
};

export default config;
