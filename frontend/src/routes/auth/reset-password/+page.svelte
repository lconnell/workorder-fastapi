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
// biome-ignore lint/style/useConst: Svelte 5 bind:this requires let
let formElement: HTMLFormElement | null = null;

onMount(async () => {
	// Give Supabase time to process the URL hash and establish session
	await new Promise((resolve) => setTimeout(resolve, 1500));

	const { data, error: sessionError } = await supabase.auth.getSession();

	if (sessionError || !data.session) {
		error =
			"Invalid or expired reset link. Please request a new password reset.";
	}
});

$effect(() => {
	// Clear was-validated classes when component initializes or error/success changes
	// (indirectly indicating a new submission attempt might occur or has finished)
	if (formElement) {
		const inputs = formElement.querySelectorAll(".validator");
		for (const input of inputs) {
			input.classList.remove("was-validated");
		}
	}
	// Dependencies
	error;
	success;
});

async function doSubmit() {
	error = null; // Clear previous general errors
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

        <!-- Only show general error if not success -->
        {#if error && !success}
          <div class="alert alert-error">
            <span>{error}</span>
          </div>
        {/if}

        <form
          bind:this={formElement}
          onsubmit={(e) => {
            e.preventDefault();
            if (!formElement) return;
            error = null; // Clear previous errors at the start of a new submission attempt

            const inputs = formElement.querySelectorAll(".validator");
            for (const input of inputs) {
              input.classList.add("was-validated");
            }

            // Custom check for password match FIRST
            if (password !== confirmPassword) {
              error = "Passwords do not match";
              const confirmInput = formElement.querySelector<HTMLInputElement>('#confirmPassword');
              if (confirmInput) {
                confirmInput.focus();
                // confirmInput.setCustomValidity("Passwords do not match"); // This makes it :invalid
              }
              // The .was-validated class is already added, so CSS will try to show hint if :invalid
              // The global 'error' state is the primary message for this.
              return;
            }
            // else {
            //   const confirmInput = formElement.querySelector<HTMLInputElement>('#confirmPassword');
            //   if (confirmInput) confirmInput.setCustomValidity(""); // Clear custom validity
            // }

            if (formElement.checkValidity()) {
              doSubmit(); // This will also clear the main 'error' if successful
            } else {
              error = "Please correct the errors highlighted below.";
              const firstInvalid = formElement.querySelector<HTMLElement>('.validator:invalid');
              firstInvalid?.focus();
            }
          }}
          class="space-y-4"
          novalidate
        >
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
              class="input input-bordered validator"
              placeholder="••••••••"
              disabled={loading}
              title="Password must be at least 6 characters"
            />
            <p class="validator-hint text-xs mt-1">Must be at least 6 characters.</p>
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
              class="input input-bordered validator"
              placeholder="••••••••"
              disabled={loading}
              title="Passwords must match"
            />
            <p class="validator-hint text-xs mt-1">Must be at least 6 characters.</p>
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
