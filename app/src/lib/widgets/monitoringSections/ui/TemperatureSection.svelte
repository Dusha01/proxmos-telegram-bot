<script lang="ts">
	import MetricLineChart from '$lib/widgets/metricChart/ui/MetricLineChart.svelte';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();
</script>

<section class="section" aria-labelledby="temp-heading">
	<h2 id="temp-heading">Температура CPU</h2>
	{#if metrics.temperatureAvailable && metrics.temperatureSeries.length > 0}
		<div class="charts">
			{#each metrics.temperatureSeries as series (series.label)}
				<MetricLineChart series={series} label={series.label} unit="°C" stroke="#e67e22" />
			{/each}
		</div>
	{:else}
		<p class="empty">Датчики температуры CPU недоступны на этой ноде.</p>
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
	.charts {
		display: grid;
		gap: 0.65rem;
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
