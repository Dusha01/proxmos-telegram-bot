<script lang="ts">
	import MetricMultiLineChart from '$lib/widgets/metricChart/ui/MetricMultiLineChart.svelte';
	import type { NodeMetricsDto } from '$lib/shared/api/types';

	let { metrics }: { metrics: NodeMetricsDto } = $props();
</script>

<section class="section" aria-labelledby="disk-temp-heading">
	<h2 id="disk-temp-heading">Температура дисков</h2>
	{#if metrics.diskTemperatureAvailable && metrics.diskTemperatureSeries.length > 0}
		<MetricMultiLineChart
			seriesList={metrics.diskTemperatureSeries}
			title="Диски (последний час)"
			unit="°C"
		/>
		<p class="hint">
			Для каждого NVMe/HDD нужны точки SMART в bucket <code>hardware</code> (см. docs/telegraf-disk-temperature.example.conf).
		</p>
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
	.hint {
		margin: 0;
		font-size: 0.75rem;
		color: var(--tg-theme-hint-color, #666);
		line-height: 1.35;
	}
	code {
		font-size: 0.72rem;
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
