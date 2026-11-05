import type { MetricPointDto, MetricSeriesDto } from '$lib/shared/api/types';

export type { MetricPointDto, MetricSeriesDto };

export function formatBytes(bytes: number | null | undefined): string {
	if (bytes == null || Number.isNaN(bytes)) {
		return '—';
	}
	const units = ['B', 'KB', 'MB', 'GB', 'TB'];
	let value = bytes;
	let unit = 0;
	while (value >= 1024 && unit < units.length - 1) {
		value /= 1024;
		unit += 1;
	}
	return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

export function formatPercent(value: number | null | undefined, digits = 1): string {
	if (value == null || Number.isNaN(value)) {
		return '—';
	}
	return `${value.toFixed(digits)}%`;
}

export function formatTempC(value: number | null | undefined): string {
	if (value == null || Number.isNaN(value)) {
		return '—';
	}
	return `${value.toFixed(1)} °C`;
}

export type ChartPath = {
	d: string;
	minY: number;
	maxY: number;
	width: number;
	height: number;
};

export function seriesToPath(
	points: MetricPointDto[],
	width: number,
	height: number,
	padding = 4
): ChartPath | null {
	if (points.length === 0) {
		return null;
	}
	const values = points.map((p) => p.value);
	let minY = Math.min(...values);
	let maxY = Math.max(...values);
	if (minY === maxY) {
		minY -= 1;
		maxY += 1;
	}
	const innerW = width - padding * 2;
	const innerH = height - padding * 2;
	const coords = points.map((p, i) => {
		const x = padding + (points.length === 1 ? innerW / 2 : (i / (points.length - 1)) * innerW);
		const y = padding + innerH - ((p.value - minY) / (maxY - minY)) * innerH;
		return `${x.toFixed(2)},${y.toFixed(2)}`;
	});
	return {
		d: `M ${coords.join(' L ')}`,
		minY,
		maxY,
		width,
		height
	};
}

export function latestValue(series: MetricSeriesDto | null): number | null {
	if (!series || series.points.length === 0) {
		return null;
	}
	return series.points[series.points.length - 1].value;
}
