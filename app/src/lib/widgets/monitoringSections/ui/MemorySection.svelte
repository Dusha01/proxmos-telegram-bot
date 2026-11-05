<script lang="ts">
	import MetricLineChart from '$lib/widgets/metricChart/ui/MetricLineChart.svelte';
	import { formatPercent } from '$lib/entities/metric';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();
</script>

<section class="section" aria-labelledby="mem-heading">
	<h2 id="mem-heading">Оперативная память</h2>
	{#if metrics.memoryPercent != null}
		<p class="snapshot">RAM сейчас: {formatPercent(metrics.memoryPercent)}</p>
	{/if}
	{#if metrics.memorySeries}
		<MetricLineChart
			series={metrics.memorySeries}
			label="Занятость RAM"
			unit="%"
			stroke="#9b59b6"
		/>
	{:else}
		<p class="empty">Нет истории по RAM за последний час.</p>
	{/if}
</section>

<style>
	.section {
		display: grid;
		gap: 0.65rem;
	}
	h2 {
		margin: 0;
		font-size: 1rem;
	}
	.snapshot {
		margin: 0;
		font-size: 0.85rem;
		color: var(--tg-theme-hint-color, #666);
	}
	.empty {
		margin: 0;
		padding: 1rem;
		text-align: center;
		color: var(--tg-theme-hint-color, #666);
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
	}
</style>
