<script lang="ts">
	import SkeletonBlock from './SkeletonBlock.svelte';
</script>

<div class="card" aria-hidden="true">
	<div class="row">
		<SkeletonBlock width="2.75rem" height="1.125rem" radius="0.4rem" />
		<SkeletonBlock width="4.5rem" height="1.375rem" radius="999px" />
	</div>
	<div class="name">
		<SkeletonBlock width="72%" height="0.95rem" />
	</div>
</div>

<style>
	.card {
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 0.9rem 1rem;
		box-shadow: 0 1px 0 color-mix(in srgb, var(--tg-theme-hint-color, #999) 12%, transparent);
	}
	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}
	.name {
		margin-top: 0.35rem;
	}
</style>
