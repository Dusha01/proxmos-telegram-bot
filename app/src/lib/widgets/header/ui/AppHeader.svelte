<script lang="ts">
	let { title = 'Proxmox', subtitle = '' }: { title?: string; subtitle?: string } = $props();
</script>

<header class="header">
	<div>
		<h1>{title}</h1>
		{#if subtitle}
			<p>{subtitle}</p>
		{/if}
	</div>
</header>

<style>
	.header {
		padding: 0.25rem 0 0.75rem;
	}
	h1 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 700;
	}
	p {
		margin: 0.2rem 0 0;
		font-size: 0.85rem;
		color: var(--tg-theme-hint-color, #666);
	}
</style>
