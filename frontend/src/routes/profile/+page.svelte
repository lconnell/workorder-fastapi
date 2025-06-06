<script lang="ts">
import { authStore } from "$lib/stores/authStore.svelte";
import { supabase } from "$lib/supabaseClient"; // Import Supabase client

interface Profile {
	id: string;
	full_name: string | null;
	avatar_url: string | null;
	updated_at: string | null;
}

let profile = $state<Profile | null>(null);
let loading = $state(true);
let error = $state<string | null>(null);

$effect(() => {
	const currentUser = authStore.user;
	if (!currentUser) {
		loading = false;
		error = "User not authenticated.";
		return;
	}

	async function fetchProfile(userId: string) {
		try {
			loading = true;
			const { data, error: supabaseError } = await supabase
				.from("profiles")
				.select("*")
				.eq("id", userId)
				.single();

			if (supabaseError) {
				throw supabaseError;
			}

			if (data) {
				profile = data as Profile;
			} else {
				// Optionally, create a profile if one doesn't exist
				// For now, just indicate no profile found
				error = "No profile data found for this user.";
			}
		} catch (e: unknown) {
			console.error("Error fetching profile:", e);
			error = e instanceof Error ? e.message : "Failed to load profile.";
		} finally {
			loading = false;
		}
	}

	fetchProfile(currentUser.id);
});
</script>

<div class="px-2 py-4 sm:px-4 lg:px-6 max-w-none">
	<h1 class="text-3xl font-bold text-base-content mb-8">User Profile</h1>

	{#if loading}
		<div class="flex justify-center items-center min-h-[50vh]">
			<span class="loading loading-spinner loading-lg"></span>
		</div>
	{:else if error}
		<div role="alert" class="alert alert-error">
			<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
			<span>Error: {error}</span>
		</div>
	{:else if profile}
		<div class="card bg-base-100 shadow-xl max-w-lg mx-auto">
			<div class="card-body items-center text-center">
				<h2 class="card-title mb-6">Profile Details</h2>

				{#if profile.avatar_url}
					<div class="avatar mb-4">
						<div class="w-24 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
							<img src={profile.avatar_url} alt="User avatar" />
						</div>
					</div>
				{:else}
					<div class="avatar placeholder mb-4">
						<div class="bg-neutral text-neutral-content rounded-full w-24 ring ring-primary ring-offset-base-100 ring-offset-2">
							<span class="text-3xl">{authStore.user?.email?.[0]?.toUpperCase() || 'U'}</span>
						</div>
					</div>
				{/if}

				<div class="mb-3 w-full">
					<p class="text-xs text-base-content/70 text-left">Email</p>
					<p class="text-left font-medium">{authStore.user?.email}</p>
				</div>

				<div class="mb-3 w-full">
					<p class="text-xs text-base-content/70 text-left">Full Name</p>
					<p class="text-left font-medium">{profile.full_name || 'Not set'}</p>
				</div>

				<div class="mb-3 w-full">
					<p class="text-xs text-base-content/70 text-left">Profile Last Updated</p>
					<p class="text-left font-medium">{profile.updated_at ? new Date(profile.updated_at).toLocaleString() : 'N/A'}</p>
				</div>

				<div class="card-actions justify-center mt-6">
					<button class="btn btn-primary">Edit Profile</button>
				</div>
			</div>
		</div>
	{:else}
		<p class="text-center">No profile data found.</p>
	{/if}
</div>
