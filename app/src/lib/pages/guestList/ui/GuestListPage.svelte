<script lang="ts">
	import AppShell from '$lib/widgets/appShell/ui/AppShell.svelte';
	import GuestList from '$lib/widgets/guestList/ui/GuestList.svelte';
	import { fetchGuestList } from '$lib/features/guestList/api/fetchGuestList';
	import type { GuestDto } from '$lib/shared/api/types';
	import { ApiClientError } from '$lib/shared/api/client';
	import { toastStore } from '$lib/shared/ui/toastStore.svelte';
	import GuestListSkeleton from '$lib/shared/ui/skeletons/GuestListSkeleton.svelte';

	let { kind }: { kind: 'qemu' | 'lxc' } = $props();

	let guests = $state<GuestDto[]>([]);
	let loading = $state(true);

	const title = $derived(kind === 'qemu' ? 'Виртуальные машины' : 'Контейнеры LXC');

	async function loadList(forKind: 'qemu' | 'lxc') {
		loading = true;
		try {
			const data = await fetchGuestList(forKind);
			if (forKind !== kind) {
				return;
			}
			guests = data.items;
		} catch (error) {
			if (forKind !== kind) {
				return;
			}
			const message = error instanceof ApiClientError ? error.message : 'Ошибка загрузки';
			toastStore.push(message, 'error');
		} finally {
			if (forKind === kind) {
				loading = false;
			}
		}
	}

	$effect(() => {
		const forKind = kind;
		void loadList(forKind);
	});

	async function load() {
		await loadList(kind);
	}
</script>

<AppShell title={title} subtitle="Управление гостями">
	{#if loading}
		<GuestListSkeleton {kind} count={kind === 'qemu' ? 4 : 3} />
	{:else}
		<GuestList {guests} {kind} />
	{/if}
	<button type="button" class="refresh" onclick={load}>Обновить</button>
</AppShell>

<style>
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
