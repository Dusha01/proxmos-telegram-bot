import type { MetricSeriesDto } from '$lib/shared/api/types';

export type MultiSeriesStroke = {
	label: string;
	stroke: string;
};

export type MultiSeriesPath = {
	width: number;
	height: number;
	minY: number;
	maxY: number;
	minTs: number;
	maxTs: number;
	series: {
		label: string;
		stroke: string;
		d: string;
		last: number | null;
	}[];
};

const DEFAULT_COLORS = [
	'var(--tg-theme-link-color, #2481cc)',
	'#e67e22',
	'#16a085',
	'#c0392b',
	'#2980b9',
	'#8e44ad',
	'#d35400',
	'#2ecc71'
];

export function pickSeriesColors(count: number): string[] {
	return Array.from({ length: count }, (_, index) => DEFAULT_COLORS[index % DEFAULT_COLORS.length]);
}

export function multiSeriesToPath(
	seriesList: MetricSeriesDto[],
	width: number,
	height: number,
	padding = 4,
	colors: string[] = DEFAULT_COLORS
): MultiSeriesPath | null {
	const withPoints = seriesList.filter((series) => series.points.length > 0);
	if (withPoints.length === 0) {
		return null;
	}

	let minY = Number.POSITIVE_INFINITY;
	let maxY = Number.NEGATIVE_INFINITY;
	let minTs = Number.POSITIVE_INFINITY;
	let maxTs = Number.NEGATIVE_INFINITY;

	for (const series of withPoints) {
		for (const point of series.points) {
			minY = Math.min(minY, point.value);
			maxY = Math.max(maxY, point.value);
			minTs = Math.min(minTs, point.timestamp);
			maxTs = Math.max(maxTs, point.timestamp);
		}
	}

	if (minY === maxY) {
		minY -= 1;
		maxY += 1;
	}
	if (minTs === maxTs) {
		minTs -= 60;
		maxTs += 60;
	}

	const innerW = width - padding * 2;
	const innerH = height - padding * 2;
	const tsSpan = maxTs - minTs;

	const mapped = withPoints.map((series, index) => {
		const coords = series.points.map((point) => {
			const x = padding + ((point.timestamp - minTs) / tsSpan) * innerW;
			const y = padding + innerH - ((point.value - minY) / (maxY - minY)) * innerH;
			return `${x.toFixed(2)},${y.toFixed(2)}`;
		});
		const last = series.points[series.points.length - 1]?.value ?? null;
		return {
			label: series.label,
			stroke: colors[index % colors.length],
			d: coords.length ? `M ${coords.join(' L ')}` : '',
			last
		};
	});

	return {
		width,
		height,
		minY,
		maxY,
		minTs,
		maxTs,
		series: mapped.filter((item) => item.d)
	};
}
