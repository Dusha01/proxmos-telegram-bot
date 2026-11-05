<script lang="ts">
	import SkeletonBlock from './SkeletonBlock.svelte';
</script>

<div class="page" role="status" aria-busy="true" aria-label="Загрузка мониторинга">
	<SkeletonBlock height="1rem" width="40%" />
	<div class="block">
		<SkeletonBlock height="7rem" />
	</div>
	<div class="block">
		<SkeletonBlock height="7rem" />
	</div>
	<div class="block">
		<SkeletonBlock height="4rem" />
		<SkeletonBlock height="4rem" />
	</div>
</div>

<style>
	.page {
		display: grid;
		gap: 0.75rem;
	}
	.block {
		display: grid;
		gap: 0.5rem;
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 0.85rem 1rem;
	}
</style>
