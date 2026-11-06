import { describe, expect, it } from 'vitest';

import { multiSeriesToPath } from '$lib/entities/metric/multiSeriesChart';

describe('multiSeriesToPath', () => {
	it('builds paths for two series with legend values', () => {
		const chart = multiSeriesToPath(
			[
				{
					label: 'NVMe 0',
					unit: '°C',
					points: [
						{ timestamp: 100, value: 30 },
						{ timestamp: 160, value: 32 }
					]
				},
				{
					label: 'NVMe 1',
					unit: '°C',
					points: [
						{ timestamp: 100, value: 35 },
						{ timestamp: 160, value: 36 }
					]
				}
			],
			100,
			50
		);
		expect(chart?.series).toHaveLength(2);
		expect(chart?.series[0].last).toBe(32);
	});
});
