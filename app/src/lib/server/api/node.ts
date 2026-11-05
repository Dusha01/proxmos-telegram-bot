import {
	authErrorResponse,
	resolveTelegramContext,
	AuthError
} from '$lib/server/auth/resolveRequestContext';
import { backendErrorResponse, BackendError, backendRequest } from '$lib/server/backend/client';
import type { HostHealthDto, NodeMetricsDto } from '$lib/shared/api/types';

type BackendMetricPoint = { timestamp: number; value: number };
type BackendMetricSeries = { label: string; unit: string; points: BackendMetricPoint[] };
type BackendStorage = {
	id: string;
	name: string;
	type: string | null;
	used: number;
	total: number;
	avail: number;
	used_percent: number;
};
type BackendRootDisk = { used: number; total: number; used_percent: number };
type BackendMetrics = {
	node: string;
	uptime: number | null;
	load_series: BackendMetricSeries[];
	memory_series: BackendMetricSeries | null;
	temperature_series: BackendMetricSeries[];
	temperature_available: boolean;
	disk_temperature_series: BackendMetricSeries[];
	disk_temperature_available: boolean;
	storages: BackendStorage[];
	root_disk: BackendRootDisk | null;
	loadavg: number[];
	cpu_percent: number | null;
	memory_percent: number | null;
};

type BackendHealth = {
	ok: boolean;
	node: string;
	uptime: number | null;
	warnings: string[];
	checked_at: string;
};

function mapSeries(s: BackendMetricSeries) {
	return {
		label: s.label,
		unit: s.unit,
		points: s.points.map((p) => ({ timestamp: p.timestamp, value: p.value }))
	};
}

function mapMetrics(raw: BackendMetrics): NodeMetricsDto {
	return {
		node: raw.node,
		uptime: raw.uptime,
		loadSeries: raw.load_series.map(mapSeries),
		memorySeries: raw.memory_series ? mapSeries(raw.memory_series) : null,
		temperatureSeries: raw.temperature_series.map(mapSeries),
		temperatureAvailable: raw.temperature_available,
		diskTemperatureSeries: raw.disk_temperature_series.map(mapSeries),
		diskTemperatureAvailable: raw.disk_temperature_available,
		storages: raw.storages.map((s) => ({
			id: s.id,
			name: s.name,
			type: s.type,
			used: s.used,
			total: s.total,
			avail: s.avail,
			usedPercent: s.used_percent
		})),
		rootDisk: raw.root_disk
			? {
					used: raw.root_disk.used,
					total: raw.root_disk.total,
					usedPercent: raw.root_disk.used_percent
				}
			: null,
		loadavg: raw.loadavg,
		cpuPercent: raw.cpu_percent,
		memoryPercent: raw.memory_percent
	};
}

function mapHealth(raw: BackendHealth): HostHealthDto {
	return {
		ok: raw.ok,
		node: raw.node,
		uptime: raw.uptime,
		warnings: raw.warnings,
		checkedAt: raw.checked_at
	};
}

export async function handleNodeMetrics(request: Request): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		const raw = await backendRequest<BackendMetrics>(ctx, '/node/metrics');
		return Response.json(mapMetrics(raw));
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}

export async function handleNodeHealth(request: Request): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		const raw = await backendRequest<BackendHealth>(ctx, '/node/health');
		return Response.json(mapHealth(raw));
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}

export async function handleNodePowerAction(
	request: Request,
	action: 'shutdown' | 'reboot'
): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		const result = await backendRequest<{ message: string }>(ctx, `/node/${action}`, {
			method: 'POST'
		});
		return Response.json(result);
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}
