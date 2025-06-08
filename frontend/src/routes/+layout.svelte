<script lang="ts">
import "../app.css";
import { goto } from "$app/navigation";
import { page } from "$app/stores";
import Toast from "$lib/components/Toast.svelte";
import { queryClient } from "$lib/queryClient";
import { authStore } from "$lib/stores/authStore.svelte";
import { QueryClientProvider } from "@tanstack/svelte-query";
import { onMount } from "svelte";

const { children } = $props();

onMount(() => {
	let cleanup: (() => void) | undefined;

	authStore.initialize().then((cleanupFn) => {
		cleanup = cleanupFn;
	});

	return () => {
		cleanup?.();
	};
});

async function handleSignOut() {
	await authStore.signOut();
	goto("/login");
}

$effect(() => {
	// Redirect to login if not authenticated and not on public pages
	const publicPaths = ["/", "/login", "/register", "/auth"];
	const isPublicPath = publicPaths.some((path) =>
		$page.url.pathname.startsWith(path),
	);

	if (authStore.initialized && !authStore.isAuthenticated && !isPublicPath) {
		goto("/login");
	}
});
</script>


<div class="min-h-screen bg-base-200">
  <div class="navbar bg-base-100 shadow-lg">
    <div class="navbar-start">
      <div class="dropdown">
        <button type="button" class="btn btn-ghost lg:hidden" aria-label="Open menu">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
          </svg>
        </button>
        <ul class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          {#if authStore.isAuthenticated}
            <li><a href="/" class="{$page.url.pathname === '/' ? 'bg-primary text-primary-content' : ''}">Dashboard</a></li>
            <li><a href="/workorders" class="{$page.url.pathname.startsWith('/workorders') ? 'bg-primary text-primary-content' : ''}">Work Orders</a></li>
          {/if}
        </ul>
      </div>
      <a href="/" class="btn btn-ghost text-xl">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        Work Order System
      </a>
    </div>
    <div class="navbar-center hidden lg:flex">
      {#if authStore.isAuthenticated}
        <ul class="menu menu-horizontal px-1">
          <li>
            <a href="/" class="font-medium {$page.url.pathname === '/' ? 'bg-primary text-primary-content' : ''}">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Dashboard
            </a>
          </li>
          <li>
            <a href="/workorders" class="font-medium {$page.url.pathname.startsWith('/workorders') ? 'bg-primary text-primary-content' : ''}">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              Work Orders
            </a>
          </li>
        </ul>
      {/if}
    </div>
    <div class="navbar-end">
      {#if authStore.isAuthenticated}
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
            <div class="avatar placeholder">
              <div class="bg-primary text-primary-content rounded-full w-10 h-10 flex items-center justify-center">
                <span class="text-sm font-bold leading-none">{authStore.user?.email?.[0]?.toUpperCase() || 'U'}</span>
              </div>
            </div>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li class="menu-title">
              <span>{authStore.user?.email}</span>
            </li>
            <li><a href="/profile" class="{$page.url.pathname === '/profile' ? 'bg-primary text-primary-content' : ''}">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile
            </a></li>
            <li class="mt-2"><button onclick={handleSignOut}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button></li>
          </ul>
        </div>
      {:else if authStore.initialized}
        <a href="/login" class="btn btn-primary">Sign In</a>
      {/if}
    </div>
  </div>

  <main class="w-full p-4">
    <QueryClientProvider client={queryClient}>
      {#if authStore.loading && !authStore.initialized}
        <div class="flex justify-center items-center min-h-[50vh]">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
      {:else}
        {@render children()}
      {/if}
    </QueryClientProvider>
  </main>

  <!-- Toast Notifications -->
  <Toast />
</div>
