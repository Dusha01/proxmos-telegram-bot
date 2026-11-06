<script lang="ts">
	import AppShell from '$lib/widgets/appShell/ui/AppShell.svelte';
	import LoadSection from '$lib/widgets/monitoringSections/ui/LoadSection.svelte';
	import MemorySection from '$lib/widgets/monitoringSections/ui/MemorySection.svelte';
	import TemperatureSection from '$lib/widgets/monitoringSections/ui/TemperatureSection.svelte';
	import DiskTemperatureSection from '$lib/widgets/monitoringSections/ui/DiskTemperatureSection.svelte';
	import DisksSection from '$lib/widgets/monitoringSections/ui/DisksSection.svelte';
	import { fetchNodeMetrics } from '$lib/features/metricsFetch/api/fetchNodeMetrics';
	import type { NodeMetricsDto } from '$lib/shared/api/types';
	import { ApiClientError } from '$lib/shared/api/client';
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';
	import MonitoringPageSkeleton from '$lib/shared/ui/skeletons/MonitoringPageSkeleton.svelte';

	let metrics = $state<NodeMetricsDto | null>(null);
	let loading = $state(true);

	async function load() {
		loading = true;
		try {
			metrics = await fetchNodeMetrics();
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка загрузки';
			toastStore.push(message, 'error');
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		void load();
	});

	const title = $derived(metrics ? `Нода ${metrics.node}` : 'Monitoring');
</script>

<AppShell {title} subtitle="Метрики Proxmox">
	{#if loading && !metrics}
		<MonitoringPageSkeleton />
	{:else if metrics}
		<div class="sections">
			<LoadSection {metrics} />
			<MemorySection {metrics} />
			<TemperatureSection {metrics} />
			<DiskTemperatureSection {metrics} />
			<DisksSection {metrics} />
		</div>
	{/if}
	<button type="button" class="refresh" onclick={load} disabled={loading}>Обновить</button>
	{#if metrics?.grafanaDashboardUrl}
		<a class="grafana" href={metrics.grafanaDashboardUrl} target="_blank" rel="noopener noreferrer">
			Открыть в Grafana
		</a>
	{/if}
</AppShell>

<style>
	.sections {
		display: grid;
		gap: 1.25rem;
	}
	.refresh {
		margin-top: 0.75rem;
		width: 100%;
		border: none;
		background: transparent;
		color: var(--tg-theme-link-color, #2481cc);
		font-weight: 600;
		padding: 0.5rem;
		cursor: pointer;
	}
	.refresh:disabled {
		opacity: 0.5;
	}
	.grafana {
		display: block;
		margin-top: 0.35rem;
		text-align: center;
		color: var(--tg-theme-link-color, #2481cc);
		font-weight: 600;
		text-decoration: none;
	}
</style>
