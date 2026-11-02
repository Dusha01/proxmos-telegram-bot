<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';

	let {
		variant = 'secondary',
		disabled = false,
		type = 'button',
		onclick,
		children
	}: {
		variant?: Variant;
		disabled?: boolean;
		type?: 'button' | 'submit';
		onclick?: (event: MouseEvent) => void;
		children: Snippet;
	} = $props();
</script>

<button {type} class="btn btn-{variant}" {disabled} {onclick}>
	{@render children()}
</button>

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 2.5rem;
		padding: 0.5rem 0.85rem;
		border-radius: 0.75rem;
		border: none;
		font-weight: 600;
		font-size: 0.9rem;
		cursor: pointer;
		width: 100%;
	}
	.btn:disabled {
		opacity: 0.55;
		cursor: not-allowed;
	}
	.btn-primary {
		background: var(--tg-theme-button-color, #2481cc);
		color: var(--tg-theme-button-text-color, #fff);
	}
	.btn-secondary {
		background: var(--tg-theme-secondary-bg-color, #eef2f7);
		color: var(--tg-theme-text-color, #111);
	}
	.btn-danger {
		background: color-mix(in srgb, #ef4444 18%, var(--tg-theme-secondary-bg-color, #fff));
		color: #b91c1c;
	}
	.btn-ghost {
		background: transparent;
		color: var(--tg-theme-link-color, #2481cc);
	}
</style>
