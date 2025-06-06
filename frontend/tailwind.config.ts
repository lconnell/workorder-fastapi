type Config = import("tailwindcss").Config;

const config: Config = {
	content: ["./src/**/*.{html,js,svelte,ts}"],
	plugins: [require("daisyui")],
	daisyui: {
		themes: ["light", "dark"],
	},
};

export default config;
