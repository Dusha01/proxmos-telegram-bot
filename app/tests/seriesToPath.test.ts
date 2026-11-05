import { describe, expect, it } from 'vitest';

import { seriesToPath } from '$lib/entities/metric';

describe('seriesToPath', () => {
	it('builds svg path for two points', () => {
		const path = seriesToPath(
			[
				{ timestamp: 1, value: 10 },
				{ timestamp: 2, value: 20 }
			],
			100,
			50
		);
		expect(path).not.toBeNull();
		expect(path?.d.startsWith('M ')).toBe(true);
	});

	it('returns null for empty series', () => {
		expect(seriesToPath([], 100, 50)).toBeNull();
	});
});
