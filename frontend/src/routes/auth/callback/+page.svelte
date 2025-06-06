<script lang="ts">
import { goto } from "$app/navigation";
import { page } from "$app/stores";
import { supabase } from "$lib/supabaseClient";
import { onMount } from "svelte";

onMount(async () => {
	// Check if this is a password recovery link
	const hashParams = new URLSearchParams(window.location.hash.substring(1));
	const type = hashParams.get("type");

	console.log("Auth callback - type:", type);
	console.log("Auth callback - hash:", window.location.hash);

	if (type === "recovery") {
		// This is a password reset link, redirect to reset password page
		console.log("Redirecting to password reset page");
		goto(`/auth/reset-password${window.location.hash}`);
		return;
	}

	const { data, error } = await supabase.auth.getSession();

	if (error) {
		console.error("Auth error:", error);
		goto(`/login?error=${encodeURIComponent(error.message)}`);
		return;
	}

	if (data.session) {
		// User is authenticated, redirect to app
		goto("/");
	} else {
		// No session, redirect to login
		goto("/login");
	}
});
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="text-center">
    <span class="loading loading-spinner loading-lg"></span>
    <p class="mt-4">Completing sign in...</p>
  </div>
</div>
