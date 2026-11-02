<script lang="ts">
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="card">
	{@render children()}
</div>

<style>
	.card {
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 1rem;
		box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
	}
</style>
