import { QueryClient } from "@tanstack/svelte-query";

// Singleton QueryClient instance for the whole app
export const queryClient = new QueryClient();
