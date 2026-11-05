<script lang="ts">
	import { seriesToPath, latestValue, formatPercent, formatTempC } from '$lib/entities/metric';
	import type { MetricSeriesDto } from '$lib/shared/api/types';

	let {
		series,
		label,
		unit = '',
		height = 120,
		stroke = 'var(--tg-theme-link-color, #2481cc)'
	}: {
		series: MetricSeriesDto;
		label: string;
		unit?: string;
		height?: number;
		stroke?: string;
	} = $props();

	const width = 320;
	const path = $derived(seriesToPath(series.points, width, height));
	const last = $derived(latestValue(series));

	function formatLast(value: number | null): string {
		if (value == null) {
			return '—';
		}
		if (unit === '%' || series.unit === '%') {
			return formatPercent(value);
		}
		if (series.unit === '°C' || unit === '°C') {
			return formatTempC(value);
		}
		if (unit) {
			return `${value.toFixed(2)} ${unit}`;
		}
		return value.toFixed(2);
	}
</script>

<figure class="chart">
	<figcaption>
		<span>{label}</span>
		<strong>{formatLast(last)}</strong>
	</figcaption>
	{#if path}
		<svg
			class="svg"
			viewBox="0 0 {width} {height}"
			role="img"
			aria-label="{label} за последний час"
		>
			<path d={path.d} fill="none" {stroke} stroke-width="2" stroke-linecap="round" />
		</svg>
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
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
	}
	strong {
		font-size: 1rem;
	}
	.svg {
		width: 100%;
		height: auto;
		display: block;
	}
	.axis {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: var(--tg-theme-hint-color, #666);
		margin-top: 0.25rem;
	}
	.empty {
		margin: 0;
		color: var(--tg-theme-hint-color, #666);
		font-size: 0.9rem;
	}
	@media (prefers-reduced-motion: reduce) {
		.svg path {
			stroke-dasharray: none;
		}
	}
</style>
