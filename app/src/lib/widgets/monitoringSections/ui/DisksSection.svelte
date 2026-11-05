<script lang="ts">
	import { formatBytes, formatPercent } from '$lib/entities/metric';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();
</script>

<section class="section" aria-labelledby="disk-heading">
	<h2 id="disk-heading">Диски</h2>
	{#if metrics.rootDisk}
		<div class="row">
			<div class="head">
				<span>Root (нода)</span>
				<span>{formatBytes(metrics.rootDisk.used)} / {formatBytes(metrics.rootDisk.total)}</span>
			</div>
			<div class="bar" aria-hidden="true">
				<div class="fill" style:width="{Math.min(metrics.rootDisk.usedPercent, 100)}%"></div>
			</div>
			<p class="meta">Свободно: {formatPercent(100 - metrics.rootDisk.usedPercent)}</p>
		</div>
	{/if}
	{#each metrics.storages as storage (storage.id)}
		<div class="row">
			<div class="head">
				<span>{storage.name}</span>
				<span>{formatBytes(storage.used)} / {formatBytes(storage.total)}</span>
			</div>
			<div class="bar" aria-hidden="true">
				<div class="fill" style:width="{Math.min(storage.usedPercent, 100)}%"></div>
			</div>
			<p class="meta">
				{storage.type ?? 'storage'} · свободно {formatBytes(storage.avail)}
			</p>
		</div>
	{/each}
	{#if !metrics.rootDisk && metrics.storages.length === 0}
		<p class="empty">Нет данных по storage.</p>
	{/if}
</section>

<style>
	.section {
		display: grid;
		gap: 0.75rem;
	}
	h2 {
		margin: 0;
		font-size: 1rem;
	}
	.row {
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 0.85rem 1rem;
		box-shadow: 0 1px 0 color-mix(in srgb, var(--tg-theme-hint-color, #999) 12%, transparent);
	}
	.head {
		display: flex;
		justify-content: space-between;
		gap: 0.5rem;
		font-size: 0.9rem;
		font-weight: 600;
	}
	.bar {
		margin-top: 0.5rem;
		height: 0.5rem;
		border-radius: 999px;
		background: color-mix(in srgb, var(--tg-theme-hint-color, #999) 20%, transparent);
		overflow: hidden;
	}
	.fill {
		height: 100%;
		border-radius: inherit;
		background: var(--tg-theme-link-color, #2481cc);
	}
	.meta {
		margin: 0.35rem 0 0;
		font-size: 0.8rem;
		color: var(--tg-theme-hint-color, #666);
	}
	.empty {
		margin: 0;
		color: var(--tg-theme-hint-color, #666);
		text-align: center;
	}
</style>
