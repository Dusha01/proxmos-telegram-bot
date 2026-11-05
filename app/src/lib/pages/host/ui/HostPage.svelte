<script lang="ts">
	import { onMount } from 'svelte';
	import AppShell from '$lib/widgets/appShell/ui/AppShell.svelte';
	import Card from '$lib/shared/ui/Card.svelte';
	import Button from '$lib/shared/ui/Button.svelte';
	import Dialog from '$lib/shared/ui/Dialog.svelte';
	import { checkHostHealth } from '$lib/features/hostHealth/api/checkHostHealth';
	import { runHostAction } from '$lib/features/hostPowerAction/api/runHostAction';
	import type { HostHealthDto } from '$lib/shared/api/types';
	import { ApiClientError } from '$lib/shared/api/client';
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';

	type HostDialog = 'shutdown1' | 'shutdown2' | 'reboot1' | 'reboot2' | null;

	let health = $state<HostHealthDto | null>(null);
	let healthLoading = $state(false);
	let busy = $state(false);
	let dialog = $state<HostDialog>(null);

	async function runHealthCheck() {
		healthLoading = true;
		try {
			health = await checkHostHealth();
			toastStore.push(health.ok ? 'Нода в норме' : 'Есть предупреждения', health.ok ? 'success' : 'info');
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка';
			toastStore.push(message, 'error');
		} finally {
			healthLoading = false;
		}
	}

	onMount(() => {
		void runHealthCheck();
	});

	async function confirmShutdown() {
		dialog = null;
		busy = true;
		try {
			const result = await runHostAction('shutdown');
			toastStore.push(result.message, 'info');
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка';
			toastStore.push(message, 'error');
		} finally {
			busy = false;
		}
	}

	async function confirmReboot() {
		dialog = null;
		busy = true;
		try {
			const result = await runHostAction('reboot');
			toastStore.push(result.message, 'info');
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка';
			toastStore.push(message, 'error');
		} finally {
			busy = false;
		}
	}
</script>

<AppShell title="Host" subtitle="Управление нодой Proxmox">
	<Card>
		<h2 class="block-title">Здоровье</h2>
		{#if healthLoading && !health}
			<p class="hint">Проверка…</p>
		{:else if health}
			<p class:ok={health.ok} class:warn={!health.ok}>
				{health.ok ? 'OK' : 'Есть предупреждения'} · {health.node}
			</p>
			{#if health.uptime != null}
				<p class="meta">Uptime: {health.uptime} s</p>
			{/if}
			{#if health.warnings.length > 0}
				<ul class="warnings">
					{#each health.warnings as w (w)}
						<li>{w}</li>
					{/each}
				</ul>
			{/if}
		{/if}
		<Button variant="ghost" disabled={healthLoading || busy} onclick={runHealthCheck}>
			Проверить
		</Button>
	</Card>

	<div class="spacer"></div>

	<Card>
		<h2 class="block-title">Питание</h2>
		<p class="warn-text">
			Выключение или перезагрузка остановят бота и Mini App до ручного включения сервера.
		</p>
		<div class="actions">
			<Button variant="danger" disabled={busy} onclick={() => (dialog = 'shutdown1')}>
				Выключить хост
			</Button>
			<Button disabled={busy} onclick={() => (dialog = 'reboot1')}>Перезагрузить</Button>
		</div>
	</Card>
</AppShell>

<Dialog
	open={dialog === 'shutdown1'}
	title="Выключить хост?"
	message="Бот и API перестанут отвечать после остановки Proxmox. Продолжить?"
	confirmLabel="Далее"
	onConfirm={() => (dialog = 'shutdown2')}
	onCancel={() => (dialog = null)}
/>
<Dialog
	open={dialog === 'shutdown2'}
	title="Подтверждение"
	message="Да, выключить хост Proxmox?"
	confirmLabel="Выключить"
	onConfirm={confirmShutdown}
	onCancel={() => (dialog = null)}
/>
<Dialog
	open={dialog === 'reboot1'}
	title="Перезагрузить хост?"
	message="Сервисы будут недоступны несколько минут. Продолжить?"
	confirmLabel="Далее"
	onConfirm={() => (dialog = 'reboot2')}
	onCancel={() => (dialog = null)}
/>
<Dialog
	open={dialog === 'reboot2'}
	title="Подтверждение"
	message="Да, перезагрузить хост Proxmox?"
	confirmLabel="Перезагрузить"
	onConfirm={confirmReboot}
	onCancel={() => (dialog = null)}
/>

<style>
	.block-title {
		margin: 0 0 0.5rem;
		font-size: 1rem;
	}
	.hint,
	.meta {
		margin: 0 0 0.5rem;
		color: var(--tg-theme-hint-color, #666);
		font-size: 0.9rem;
	}
	.ok {
		color: #2ecc71;
		font-weight: 600;
	}
	.warn {
		color: #e67e22;
		font-weight: 600;
	}
	.warnings {
		margin: 0.5rem 0;
		padding-left: 1.1rem;
		font-size: 0.85rem;
		color: var(--tg-theme-hint-color, #666);
	}
	.warn-text {
		margin: 0 0 0.75rem;
		font-size: 0.9rem;
		color: var(--tg-theme-hint-color, #666);
		line-height: 1.45;
	}
	.actions {
		display: grid;
		gap: 0.55rem;
	}
	.spacer {
		height: 0.75rem;
	}
</style>
