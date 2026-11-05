<script lang="ts">
	import { pickSeriesColors } from '$lib/entities/metric/multiSeriesChart';
	import MetricLineChart from '$lib/widgets/metricChart/ui/MetricLineChart.svelte';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();

	const colors = $derived(pickSeriesColors(metrics.diskTemperatureSeries.length));
</script>

<section class="section" aria-labelledby="disk-temp-heading">
	<h2 id="disk-temp-heading">Температура дисков</h2>
	{#if metrics.diskTemperatureAvailable && metrics.diskTemperatureSeries.length > 0}
		<div class="charts">
			{#each metrics.diskTemperatureSeries as series, index (series.label)}
				<MetricLineChart
					{series}
					label={series.label}
					unit="°C"
					stroke={colors[index % colors.length]}
				/>
			{/each}
		</div>
	{:else}
		<p class="empty">Температура дисков недоступна в Influx (hardware).</p>
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
		gap: 0.75rem;
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
