<script lang="ts">
	import './layout.css';
	import { onMount } from 'svelte';
	import { fetchMe } from '$lib/features/accessGate/api/fetchMe';
	import AccessDenied from '$lib/features/accessGate/ui/AccessDenied.svelte';
	import { initTelegramChrome } from '$lib/shared/lib/telegram/authHeader';
	import { ApiClientError } from '$lib/shared/api/client';
	import { userMessageForAccessError } from '$lib/features/accessGate/lib/userAccessMessage';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	let denied = $state<{ message: string; detail?: string } | null>(null);
	let loading = $state(true);

	onMount(async () => {
		initTelegramChrome();
		try {
			await fetchMe();
		} catch (error) {
			if (error instanceof ApiClientError) {
				denied = {
					message: userMessageForAccessError(error),
					detail: `${error.code}: ${error.message}`
				};
			} else {
				denied = { message: 'Нет доступа.' };
			}
		} finally {
			loading = false;
		}
	});
</script>


{#if loading}
	<p class="boot">Загрузка…</p>
{:else if denied}
	<AccessDenied message={denied.message} detail={denied.detail} />
{:else}
	{@render children()}
{/if}

<style>
	.boot {
		min-height: 100dvh;
		display: grid;
		place-items: center;
		color: var(--tg-theme-hint-color, #666);
	}
</style>
