<script lang="ts">
	import MetricLineChart from '$lib/widgets/metricChart/ui/MetricLineChart.svelte';
	import { formatPercent } from '$lib/entities/metric';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();

	const cpuSeries = $derived(
		metrics.loadSeries.find((s) => s.label === 'CPU') ?? metrics.loadSeries[0] ?? null
	);
	const loadSeries = $derived(metrics.loadSeries.find((s) => s.label === 'Load') ?? null);
</script>

<section class="section" aria-labelledby="load-heading">
	<h2 id="load-heading">Нагрузка</h2>
	{#if metrics.cpuPercent != null}
		<p class="snapshot">CPU сейчас: {formatPercent(metrics.cpuPercent)}</p>
	{/if}
	<div class="charts">
		{#if cpuSeries}
			<MetricLineChart series={cpuSeries} label="CPU" unit="%" />
		{/if}
		{#if loadSeries}
			<MetricLineChart series={loadSeries} label="Load average" />
		{/if}
	</div>
	{#if metrics.loadavg.length >= 3}
		<p class="meta">
			Load 1/5/15: {metrics.loadavg[0].toFixed(2)} / {metrics.loadavg[1].toFixed(2)} /
			{metrics.loadavg[2].toFixed(2)}
		</p>
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
	.snapshot,
	.meta {
		margin: 0;
		font-size: 0.85rem;
		color: var(--tg-theme-hint-color, #666);
	}
	.charts {
		display: grid;
		gap: 0.65rem;
	}
</style>
