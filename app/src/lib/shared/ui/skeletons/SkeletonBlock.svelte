<script lang="ts">
	let {
		width = '100%',
		height = '0.875rem',
		radius = '0.5rem',
		class: className = ''
	}: {
		width?: string;
		height?: string;
		radius?: string;
		class?: string;
	} = $props();
</script>

<span
	class="bone {className}"
	style:width
	style:height
	style:border-radius={radius}
	aria-hidden="true"
></span>

<style>
	.bone {
		display: block;
		background: color-mix(in srgb, var(--tg-theme-hint-color, #8e8e93) 18%, transparent);
		box-shadow: inset 0 1px 0 color-mix(in srgb, var(--tg-theme-bg-color, #fff) 35%, transparent);
		position: relative;
		overflow: hidden;
	}

	.bone::after {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(
			90deg,
			transparent 0%,
			color-mix(in srgb, var(--tg-theme-bg-color, #fff) 55%, transparent) 45%,
			transparent 100%
		);
		transform: translateX(-100%);
		animation: skeleton-shimmer 1.35s ease-in-out infinite;
	}

	@keyframes skeleton-shimmer {
		to {
			transform: translateX(100%);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.bone::after {
			animation: none;
			opacity: 0.35;
		}
	}
</style>
