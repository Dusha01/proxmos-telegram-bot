import { apiFetch } from '$lib/shared/api/client';
import type { NodeMetricsDto } from '$lib/shared/api/types';

export async function fetchNodeMetrics(): Promise<NodeMetricsDto> {
	return apiFetch<NodeMetricsDto>('/api/node/metrics');
}
