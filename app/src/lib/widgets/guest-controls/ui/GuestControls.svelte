<script lang="ts">
	import type { GuestDto, PowerAction } from '$lib/shared/api/types';
	import Button from '$lib/shared/ui/Button.svelte';
	import { statusButtonLabel } from '$lib/entities/guest/lib/mapStatusLabel';

	let {
		guest,
		busy = false,
		onAction,
		onRefreshStatus
	}: {
		guest: GuestDto;
		busy?: boolean;
		onAction: (action: PowerAction) => void;
		onRefreshStatus: () => void;
	} = $props();
</script>

<div class="controls">
	{#if guest.status === 'stopped'}
		<Button variant="primary" disabled={busy} onclick={() => onAction('start')}>Запуск</Button>
	{:else if guest.status === 'running'}
		<div class="row">
			<Button disabled={busy} onclick={() => onAction('suspend')}>Пауза</Button>
			<Button disabled={busy} onclick={() => onAction('stop')}>Стоп</Button>
		</div>
		<Button disabled={busy} onclick={() => onAction('reboot')}>Перезагрузить</Button>
		<Button variant="danger" disabled={busy} onclick={() => onAction('shutdown')}>Выключить</Button>
	{:else if guest.status === 'paused'}
		<div class="row">
			<Button variant="primary" disabled={busy} onclick={() => onAction('resume')}>Продолжить</Button>
			<Button disabled={busy} onclick={() => onAction('stop')}>Стоп</Button>
		</div>
	{/if}
	<Button variant="ghost" disabled={busy} onclick={onRefreshStatus}>{statusButtonLabel(guest.status)}</Button>
</div>

<style>
	.controls {
		display: grid;
		gap: 0.55rem;
	}
	.row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.55rem;
	}
</style>
