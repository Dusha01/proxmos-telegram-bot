<script lang="ts">
	import type { GuestStatus } from '$lib/shared/api/types';
	import { mapPowerStatusLabel } from '$lib/entities/guest/lib/mapStatusLabel';

	let { status }: { status: GuestStatus } = $props();

	const tone = $derived(
		status === 'running' ? 'ok' : status === 'stopped' ? 'off' : status === 'paused' ? 'warn' : 'muted'
	);
</script>

<span class="badge badge-{tone}">{mapPowerStatusLabel(status)}</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		padding: 0.15rem 0.55rem;
		border-radius: 999px;
		font-size: 0.75rem;
		font-weight: 600;
	}
	.badge-ok {
		background: color-mix(in srgb, #22c55e 20%, var(--tg-theme-secondary-bg-color, #eee));
		color: #166534;
	}
	.badge-off {
		background: color-mix(in srgb, #64748b 20%, var(--tg-theme-secondary-bg-color, #eee));
		color: #334155;
	}
	.badge-warn {
		background: color-mix(in srgb, #f59e0b 25%, var(--tg-theme-secondary-bg-color, #eee));
		color: #92400e;
	}
	.badge-muted {
		background: var(--tg-theme-secondary-bg-color, #eee);
		color: var(--tg-theme-hint-color, #666);
	}
</style>
