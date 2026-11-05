<script lang="ts">
	import SkeletonBlock from './SkeletonBlock.svelte';
</script>

<div class="detail" role="status" aria-busy="true" aria-label="Загрузка гостя…">
	<div class="card">
		<div class="head">
			<SkeletonBlock width="55%" height="1.125rem" />
			<SkeletonBlock width="4.5rem" height="1.375rem" radius="999px" />
		</div>
		<div class="meta">
			<SkeletonBlock width="40%" height="0.875rem" />
		</div>
	</div>
	<div class="controls">
		<SkeletonBlock height="2.75rem" radius="0.75rem" />
		<div class="row">
			<SkeletonBlock height="2.75rem" radius="0.75rem" />
			<SkeletonBlock height="2.75rem" radius="0.75rem" />
		</div>
		<SkeletonBlock height="2.75rem" radius="0.75rem" />
	</div>
</div>

<style>
	.detail {
		display: grid;
		gap: 0.75rem;
	}
	.card {
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 1rem;
		box-shadow: 0 1px 0 color-mix(in srgb, var(--tg-theme-hint-color, #999) 12%, transparent);
	}
	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}
	.meta {
		margin-top: 0.5rem;
	}
	.controls {
		display: grid;
		gap: 0.55rem;
	}
	.row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.55rem;
	}
</style>
