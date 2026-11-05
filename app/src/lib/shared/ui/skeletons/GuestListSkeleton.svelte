<script lang="ts">
	import GuestCardSkeleton from './GuestCardSkeleton.svelte';
	import type { GuestKind } from '$lib/shared/api/types';

	let {
		kind = 'qemu',
		count = 4
	}: {
		kind?: GuestKind;
		count?: number;
	} = $props();

	const rows = $derived(Array.from({ length: count }, (_, i) => i));
	const label = $derived(kind === 'qemu' ? 'Загрузка виртуальных машин…' : 'Загрузка контейнеров LXC…');
</script>

<div class="wrap" role="status" aria-busy="true" aria-label={label}>
	<div class="list">
		{#each rows as row (row)}
			<GuestCardSkeleton />
		{/each}
	</div>
</div>

<style>
	.wrap {
		display: block;
	}
	.list {
		display: grid;
		gap: 0.65rem;
	}
</style>
