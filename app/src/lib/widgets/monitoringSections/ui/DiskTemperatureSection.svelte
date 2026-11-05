<script lang="ts">
	import MetricLineChart from '$lib/widgets/metricChart/ui/MetricLineChart.svelte';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();

	const diskColors = ['#e67e22', '#16a085', '#c0392b', '#2980b9', '#8e44ad'];
</script>

<section class="section" aria-labelledby="disk-temp-heading">
	<h2 id="disk-temp-heading">Температура дисков</h2>
	{#if metrics.diskTemperatureAvailable && metrics.diskTemperatureSeries.length > 0}
		<div class="charts">
			{#each metrics.diskTemperatureSeries as series, i (series.label)}
				<MetricLineChart
					series={series}
					label={series.label}
					unit="°C"
					stroke={diskColors[i % diskColors.length]}
				/>
			{/each}
		</div>
	{:else}
		<p class="empty">Температура дисков недоступна (нет полей *_temp в RRD ноды).</p>
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
