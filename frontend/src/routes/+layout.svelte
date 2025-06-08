<script lang="ts">
import "../app.css";
import { goto } from "$app/navigation";
import { page } from "$app/stores";
import {
	IconAppLogo,
	IconHome,
	IconLogout,
	IconMenu,
	IconUser,
} from "$lib/components/icons";
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
          <IconMenu />
        </button>
        <ul class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          {#if authStore.isAuthenticated}
            <li><a href="/" class="{$page.url.pathname === '/' ? 'bg-primary text-primary-content' : ''}">Dashboard</a></li>
            <li><a href="/workorders" class="{$page.url.pathname.startsWith('/workorders') ? 'bg-primary text-primary-content' : ''}">Work Orders</a></li>
          {/if}
        </ul>
      </div>
      <a href="/" class="btn btn-ghost text-xl">
        <IconAppLogo class="mr-2" />
        Work Order System
      </a>
    </div>
    <div class="navbar-center hidden lg:flex">
      {#if authStore.isAuthenticated}
        <ul class="menu menu-horizontal px-1">
          <li>
            <a href="/" class="font-medium {$page.url.pathname === '/' ? 'bg-primary text-primary-content' : ''}">
              <IconHome class="mr-1" />
              Dashboard
            </a>
          </li>
          <li>
            <a href="/workorders" class="font-medium {$page.url.pathname.startsWith('/workorders') ? 'bg-primary text-primary-content' : ''}">
              <IconAppLogo size="1.25em" class="mr-1" /> {/* h-5 w-5 */}
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
              <IconUser />
              Profile
            </a></li>
            <li class="mt-2"><button onclick={handleSignOut}>
              <IconLogout />
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
