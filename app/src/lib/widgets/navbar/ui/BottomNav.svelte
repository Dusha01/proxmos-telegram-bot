<script lang="ts">
	import { page } from '$app/state';
	import { navItems } from '$lib/widgets/navbar/model/navItems';

	const pathname = $derived(page.url.pathname);
</script>

<nav class="nav" aria-label="Main">
	{#each navItems as item}
		{#if item.disabled}
			<span class="tab disabled" title="Скоро">{item.label}</span>
		{:else}
			<a class="tab" class:active={pathname.startsWith(item.href)} href={item.href}>{item.label}</a>
		{/if}
	{/each}
</nav>

<style>
	.nav {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.25rem;
		padding: 0.35rem;
		background: var(--tg-theme-secondary-bg-color, #eef2f7);
		border-radius: 1rem;
	}
	.tab {
		text-align: center;
		padding: 0.5rem 0.2rem;
		border-radius: 0.75rem;
		font-weight: 600;
		font-size: 0.72rem;
		text-decoration: none;
		color: var(--tg-theme-text-color, #111);
	}
	.tab.active {
		background: var(--tg-theme-bg-color, #fff);
		box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
	}
	.disabled {
		color: var(--tg-theme-hint-color, #888);
	}
</style>
