<script lang="ts">
	import { onMount } from 'svelte';
	import AppShell from '$lib/widgets/app-shell/ui/AppShell.svelte';
	import GuestList from '$lib/widgets/guest-list/ui/GuestList.svelte';
	import { fetchGuestList } from '$lib/features/guest-list/api/fetchGuestList';
	import type { GuestDto } from '$lib/shared/api/types';
	import { ApiClientError } from '$lib/shared/api/client';
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';

	let { kind }: { kind: 'qemu' | 'lxc' } = $props();

	let guests = $state<GuestDto[]>([]);
	let loading = $state(true);

	const title = $derived(kind === 'qemu' ? 'Виртуальные машины' : 'Контейнеры LXC');

	async function load() {
		loading = true;
		try {
			const data = await fetchGuestList(kind);
			guests = data.items;
		} catch (error) {
			const message = error instanceof ApiClientError ? error.message : 'Ошибка загрузки';
			toastStore.push(message, 'error');
		} finally {
			loading = false;
		}
	}

	onMount(load);
</script>

<AppShell title={title} subtitle="Управление гостями">
	{#if loading}
		<p class="hint">Загрузка…</p>
	{:else}
		<GuestList {guests} {kind} />
	{/if}
	<button type="button" class="refresh" onclick={load}>Обновить</button>
</AppShell>

<style>
	.hint {
		text-align: center;
		color: var(--tg-theme-hint-color, #666);
		padding: 2rem 0;
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
</style>
