<script lang="ts">
	import type { Snippet } from 'svelte';
	import AppHeader from '$lib/widgets/header/ui/AppHeader.svelte';
	import BottomNav from '$lib/widgets/navbar/ui/BottomNav.svelte';
	import ToastHost from '$lib/shared/ui/ToastHost.svelte';

	let {
		title = 'Proxmox',
		subtitle = '',
		showNav = true,
		children
	}: {
		title?: string;
		subtitle?: string;
		showNav?: boolean;
		children: Snippet;
	} = $props();
</script>

<div class="shell">
	<AppHeader {title} {subtitle} />
	<main>{@render children()}</main>
	{#if showNav}
		<BottomNav />
	{/if}
	<ToastHost />
</div>

<style>
	.shell {
		min-height: 100dvh;
		display: grid;
		grid-template-rows: auto 1fr auto;
		padding: calc(0.75rem + env(safe-area-inset-top)) 0.85rem calc(0.75rem + env(safe-area-inset-bottom));
		background: var(--tg-theme-bg-color, #f8fafc);
		color: var(--tg-theme-text-color, #0f172a);
		gap: 0.75rem;
	}
	main {
		min-height: 0;
		overflow: auto;
	}
</style>
