<script lang="ts">
import { goto } from "$app/navigation";
import { authStore } from "$lib/stores/authStore.svelte";
import { supabase } from "$lib/supabaseClient";

interface Props {
	mode?: "signin" | "signup";
	redirectTo?: string;
}

const { mode = "signin", redirectTo = "/" }: Props = $props();

// biome-ignore lint/style/useConst: Svelte 5 binding requires let
let email = $state("");
// biome-ignore lint/style/useConst: Svelte 5 binding requires let
let password = $state("");
// biome-ignore lint/style/useConst: Svelte 5 binding requires let
let fullName = $state("");
let error = $state<string | null>(null);
let success = $state<string | null>(null);
let currentMode = $state(mode);
let showForgotPassword = $state(false);

async function handleSubmit(e: Event) {
	e.preventDefault();
	error = null;

	try {
		if (currentMode === "signin") {
			const { error: signInError } = await authStore.signIn(email, password);
			if (signInError) throw signInError;
		} else {
			const { error: signUpError } = await authStore.signUp(email, password, {
				full_name: fullName,
			});
			if (signUpError) throw signUpError;
		}

		await goto(redirectTo);
	} catch (err: unknown) {
		if (err instanceof Error) {
			error = err.message;
		} else if (typeof err === "string") {
			error = err;
		} else {
			error = "An unexpected error occurred during authentication.";
		}
	}
}

function toggleMode() {
	currentMode = currentMode === "signin" ? "signup" : "signin";
	error = null;
	success = null;
	showForgotPassword = false;
}

async function handleForgotPassword() {
	if (!email) {
		error = "Please enter your email address";
		return;
	}

	error = null;
	success = null;

	try {
		const { error: resetError } = await supabase.auth.resetPasswordForEmail(
			email,
			{
				redirectTo: `${window.location.origin}/auth/reset-password`,
			},
		);

		if (resetError) throw resetError;

		success = "Password reset email sent! Check your inbox.";
		showForgotPassword = false;
	} catch (err: unknown) {
		if (err instanceof Error) {
			error = err.message;
		} else if (typeof err === "string") {
			error = err;
		} else {
			error = "Failed to send reset email due to an unexpected error.";
		}
	}
}
</script>

<div class="card w-96 bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">
      {currentMode === 'signin' ? 'Sign In' : 'Sign Up'}
    </h2>

    {#if error}
      <div class="alert alert-error">
        <span>{error}</span>
      </div>
    {/if}

    {#if success}
      <div class="alert alert-success">
        <span>{success}</span>
      </div>
    {/if}

    <form onsubmit={handleSubmit} class="space-y-4">
      {#if currentMode === 'signup'}
        <div class="form-control">
          <label class="label" for="fullName">
            <span class="label-text">Full Name</span>
          </label>
          <input
            id="fullName"
            type="text"
            bind:value={fullName}
            class="input input-bordered"
            placeholder="John Doe"
          />
        </div>
      {/if}

      <div class="form-control">
        <label class="label" for="email">
          <span class="label-text">Email</span>
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          class="input input-bordered"
          placeholder="user@example.com"
        />
      </div>

      <div class="form-control">
        <label class="label" for="password">
          <span class="label-text">Password</span>
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          minlength="6"
          class="input input-bordered"
          placeholder="••••••••"
        />
      </div>

      <div class="card-actions flex-col gap-2">
        <button
          type="submit"
          class="btn btn-primary w-full"
          disabled={authStore.loading}
        >
          {#if authStore.loading}
            <span class="loading loading-spinner"></span>
          {/if}
          {currentMode === 'signin' ? 'Sign In' : 'Sign Up'}
        </button>

        <div class="flex justify-between items-center w-full">
          <button
            type="button"
            class="btn btn-link btn-sm"
            onclick={toggleMode}
          >
            {currentMode === 'signin' ? 'Need an account?' : 'Already have an account?'}
          </button>

          {#if currentMode === 'signin'}
            <button
              type="button"
              class="btn btn-link btn-sm"
              onclick={() => showForgotPassword = !showForgotPassword}
            >
              Forgot password?
            </button>
          {/if}
        </div>

        {#if showForgotPassword && currentMode === 'signin'}
          <div class="divider">Reset Password</div>
          <div class="form-control">
            <label class="label" for="reset-email">
              <span class="label-text text-sm">Enter your email to receive a reset link</span>
            </label>
            <div class="flex gap-2">
              <input
                id="reset-email"
                type="email"
                bind:value={email}
                placeholder="your@email.com"
                class="input input-bordered input-sm flex-1"
                required
              />
              <button
                type="button"
                class="btn btn-sm btn-outline"
                onclick={handleForgotPassword}
              >
                Send Reset
              </button>
            </div>
          </div>
        {/if}
      </div>
    </form>
  </div>
</div>
