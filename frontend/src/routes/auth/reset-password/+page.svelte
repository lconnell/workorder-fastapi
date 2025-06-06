<script lang="ts">
import { goto } from "$app/navigation";
import { supabase } from "$lib/supabaseClient";
import { onMount } from "svelte";

// biome-ignore lint/style/useConst: Svelte 5 binding requires let
let password = $state("");
// biome-ignore lint/style/useConst: Svelte 5 binding requires let
let confirmPassword = $state("");
let error = $state<string | null>(null);
let loading = $state(false);
let success = $state(false);

onMount(async () => {
	console.log("Reset password page loaded");
	console.log("URL hash:", window.location.hash);

	// Give Supabase time to process the URL hash and establish session
	await new Promise((resolve) => setTimeout(resolve, 1500));

	const { data, error: sessionError } = await supabase.auth.getSession();
	console.log("Session check:", data.session ? "valid session" : "no session");

	if (sessionError || !data.session) {
		console.log("No valid session for password reset");
		error =
			"Invalid or expired reset link. Please request a new password reset.";
	} else {
		console.log("Valid reset session established");
	}
});

async function handleSubmit(e: Event) {
	e.preventDefault();
	error = null;

	if (password !== confirmPassword) {
		error = "Passwords do not match";
		return;
	}

	if (password.length < 6) {
		error = "Password must be at least 6 characters";
		return;
	}

	loading = true;

	try {
		const { error: updateError } = await supabase.auth.updateUser({
			password: password,
		});

		if (updateError) throw updateError;

		success = true;

		// Redirect to app after 2 seconds
		setTimeout(() => {
			goto("/");
		}, 2000);
	} catch (err: unknown) {
		if (err instanceof Error && err.message) {
			error = err.message;
		} else if (typeof err === "string") {
			error = err;
		} else {
			error = "Failed to update password";
		}
	} finally {
		loading = false;
	}
}
</script>

<div class="min-h-screen flex items-center justify-center bg-base-200">
  <div class="card w-96 bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Reset Password</h2>

      {#if success}
        <div class="alert alert-success">
          <span>Password updated successfully! Redirecting...</span>
        </div>
      {:else}
        <p class="text-sm opacity-70 mb-4">
          Enter your new password below.
        </p>

        {#if error}
          <div class="alert alert-error">
            <span>{error}</span>
          </div>
        {/if}

        <form onsubmit={handleSubmit} class="space-y-4">
          <div class="form-control">
            <label class="label" for="password">
              <span class="label-text">New Password</span>
            </label>
            <input
              id="password"
              type="password"
              bind:value={password}
              required
              minlength="6"
              class="input input-bordered"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <div class="form-control">
            <label class="label" for="confirmPassword">
              <span class="label-text">Confirm Password</span>
            </label>
            <input
              id="confirmPassword"
              type="password"
              bind:value={confirmPassword}
              required
              minlength="6"
              class="input input-bordered"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <div class="card-actions justify-end">
            <button
              type="submit"
              class="btn btn-primary w-full"
              disabled={loading || !password || !confirmPassword}
            >
              {#if loading}
                <span class="loading loading-spinner"></span>
              {/if}
              Update Password
            </button>
          </div>
        </form>
      {/if}
    </div>
  </div>
</div>
