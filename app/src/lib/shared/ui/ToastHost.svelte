<script lang="ts">
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';
</script>

<div class="toasts" aria-live="polite">
	{#each toastStore.items as item (item.id)}
		<div class="toast toast-{item.tone}">{item.message}</div>
	{/each}
</div>

<style>
	.toasts {
		position: fixed;
		left: 0.75rem;
		right: 0.75rem;
		bottom: calc(4.5rem + env(safe-area-inset-bottom));
		z-index: 60;
		display: grid;
		gap: 0.5rem;
		pointer-events: none;
	}
	.toast {
		padding: 0.75rem 0.9rem;
		border-radius: 0.85rem;
		font-size: 0.9rem;
		line-height: 1.35;
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
	}
	.toast-success {
		background: #ecfdf5;
		color: #065f46;
	}
	.toast-error {
		background: #fef2f2;
		color: #991b1b;
	}
	.toast-info {
		background: var(--tg-theme-secondary-bg-color, #eef2ff);
		color: var(--tg-theme-text-color, #111);
	}
</style>
