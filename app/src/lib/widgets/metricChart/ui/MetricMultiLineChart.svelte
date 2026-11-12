<script lang="ts">
	import {
		multiSeriesToPath,
		pickSeriesColors
	} from '$lib/entities/metric/multiSeriesChart';
	import { formatPercent, formatTempC } from '$lib/entities/metric';
	import type { MetricSeriesDto } from '$lib/shared/api/types';

	let {
		seriesList,
		title,
		unit = '',
		height = 140
	}: {
		seriesList: MetricSeriesDto[];
		title: string;
		unit?: string;
		height?: number;
	} = $props();

	const width = 320;
	const colors = $derived(pickSeriesColors(seriesList.length));
	const chart = $derived(multiSeriesToPath(seriesList, width, height, 4, colors));

	function formatValue(value: number | null): string {
		if (value == null) {
			return '—';
		}
		if (unit === '%') {
			return formatPercent(value);
		}
		if (unit === '°C') {
			return formatTempC(value);
		}
		return value.toFixed(1);
	}
</script>

<figure class="chart">
	<figcaption>{title}</figcaption>
	{#if chart}
		<svg class="svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title} за последний час">
			{#each chart.series as item (item.label)}
				<path d={item.d} fill="none" stroke={item.stroke} stroke-width="2" stroke-linecap="round" />
			{/each}
		</svg>
		<ul class="legend">
			{#each chart.series as item (item.label)}
				<li>
					<span class="swatch" style:background={item.stroke} aria-hidden="true"></span>
					<span class="name">{item.label}</span>
					<strong>{formatValue(item.last)}</strong>
				</li>
			{/each}
		</ul>
		<div class="axis">
			<span>−60 мин</span>
			<span>сейчас</span>
		</div>
	{:else}
		<p class="empty">Нет данных</p>
	{/if}
</figure>

<style>
	.chart {
		margin: 0;
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 0.85rem 1rem;
		box-shadow: 0 1px 0 color-mix(in srgb, var(--tg-theme-hint-color, #999) 12%, transparent);
	}
	figcaption {
		margin: 0 0 0.5rem;
		font-size: 0.9rem;
		font-weight: 600;
	}
	.svg {
		width: 100%;
		height: auto;
		display: block;
	}
	.legend {
		list-style: none;
		margin: 0.65rem 0 0;
		padding: 0;
		display: grid;
		gap: 0.35rem;
	}
	.legend li {
		display: grid;
		grid-template-columns: auto 1fr auto;
		align-items: center;
		gap: 0.45rem;
		font-size: 0.82rem;
	}
	.swatch {
		width: 0.65rem;
		height: 0.65rem;
		border-radius: 999px;
	}
	.name {
		color: var(--tg-theme-text-color, #000);
	}
	strong {
		font-size: 0.82rem;
	}
	.axis {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: var(--tg-theme-hint-color, #666);
		margin-top: 0.35rem;
	}
	.empty {
		margin: 0;
		color: var(--tg-theme-hint-color, #666);
		font-size: 0.9rem;
	}
</style>
