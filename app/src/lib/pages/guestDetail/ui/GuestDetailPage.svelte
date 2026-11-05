<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import AppShell from '$lib/widgets/appShell/ui/AppShell.svelte';
	import Card from '$lib/shared/ui/Card.svelte';
	import GuestControls from '$lib/widgets/guestControls/ui/GuestControls.svelte';
	import GuestStatusBadge from '$lib/entities/guest/ui/GuestStatusBadge.svelte';
	import Dialog from '$lib/shared/ui/Dialog.svelte';
	import { fetchGuest } from '$lib/features/guestRefreshStatus/api/fetchGuest';
	import { runPowerAction } from '$lib/features/guestPowerAction/api/runPowerAction';
	import { mapActionLabel, formatActionResultMessage } from '$lib/entities/guest';
	import { mapStatusLabel } from '$lib/entities/guest/lib/mapStatusLabel';
	import type { GuestDto, GuestKind, PowerAction } from '$lib/shared/api/types';
	import { ApiClientError } from '$lib/shared/api/client';
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';
	import { getTelegramWebApp, hapticError, hapticSuccess } from '$lib/shared/lib/telegram/authHeader';
	import GuestDetailSkeleton from '$lib/shared/ui/skeletons/GuestDetailSkeleton.svelte';

	let { kind, vmid }: { kind: GuestKind; vmid: number } = $props();

	let guest = $state<GuestDto | null>(null);
	let loading = $state(true);
	let busy = $state(false);
	let confirmOpen = $state(false);
	let pendingAction = $state<PowerAction | null>(null);

	async function loadGuest(forKind: GuestKind, forVmid: number) {
		loading = true;
		guest = null;
		try {
			const data = await fetchGuest(forKind, forVmid);
			if (forKind !== kind || forVmid !== vmid) {
				return;
			}
			guest = data;
		} catch (error) {
			if (forKind !== kind || forVmid !== vmid) {
				return;
			}
			const message = error instanceof ApiClientError ? error.message : 'Ошибка';
			toastStore.push(message, 'error');
			hapticError();
		} finally {
			if (forKind === kind && forVmid === vmid) {
				loading = false;
			}
		}
	}

	$effect(() => {
		const forKind = kind;
		const forVmid = vmid;
		void loadGuest(forKind, forVmid);
	});

	function requestAction(action: PowerAction) {
		pendingAction = action;
		confirmOpen = true;
	}

	async function confirmAction() {
		if (!pendingAction || !guest) {
			return;
		}
		const action = pendingAction;
		confirmOpen = false;
		pendingAction = null;
		busy = true;
		try {
			const result = await runPowerAction(kind, vmid, action);
			guest = result.guest;
			const message = formatActionResultMessage(result.guest, action, result.reachedExpected);
			toastStore.push(message, result.reachedExpected ? 'success' : 'info');
			hapticSuccess();
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка действия';
			toastStore.push(message, 'error');
			hapticError();
		} finally {
			busy = false;
		}
	}

	async function refreshStatus() {
		busy = true;
		try {
			const data = await fetchGuest(kind, vmid);
			guest = data;
			toastStore.push(`Статус: ${mapStatusLabel(data.status)}`, 'info');
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка';
			toastStore.push(message, 'error');
		} finally {
			busy = false;
		}
	}

	onMount(() => {
		const webApp = getTelegramWebApp();
		webApp?.BackButton?.show();
		return () => {
			webApp?.BackButton?.hide();
		};
	});

	$effect(() => {
		const listKind = kind;
		const webApp = getTelegramWebApp();
		const back = () => goto(`/guests/${listKind}`);
		webApp?.BackButton?.onClick(back);
		return () => webApp?.BackButton?.offClick(back);
	});
</script>

<AppShell
	title={guest ? `${guest.kind.toUpperCase()} ${guest.vmid}` : 'Гость'}
	subtitle={guest?.name ?? ''}
	showNav={false}
>
	{#if loading}
		<GuestDetailSkeleton />
	{:else if guest}
		<Card>
			<div class="head">
				<strong>{guest.name}</strong>
				<GuestStatusBadge status={guest.status} />
			</div>
			<p class="meta">Статус: {mapStatusLabel(guest.status)}</p>
		</Card>
		<div class="spacer"></div>
		<GuestControls {guest} {busy} onAction={requestAction} onRefreshStatus={refreshStatus} />
	{/if}
</AppShell>

<Dialog
	open={confirmOpen}
	title="Подтверждение"
	message={pendingAction
		? `Выполнить «${mapActionLabel(pendingAction)}» для ${kind.toUpperCase()} ${vmid}?`
		: ''}
	confirmLabel="Подтвердить"
	onConfirm={confirmAction}
	onCancel={() => {
		confirmOpen = false;
		pendingAction = null;
	}}
/>

<style>
	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}
	.meta {
		margin: 0.5rem 0 0;
		color: var(--tg-theme-hint-color, #666);
		font-size: 0.9rem;
	}
	.spacer {
		height: 0.75rem;
	}
</style>
