<script lang="ts">
	import type { GuestDto } from '$lib/shared/api/types';
	import GuestCard from '$lib/widgets/guest-card/ui/GuestCard.svelte';

	let {
		guests,
		kind
	}: {
		guests: GuestDto[];
		kind: 'qemu' | 'lxc';
	} = $props();
</script>

{#if guests.length === 0}
	<p class="empty">Нет гостей</p>
{:else}
	<div class="list">
		{#each guests as guest (guest.vmid)}
			<GuestCard {guest} href={`/guests/${kind}/${guest.vmid}`} />
		{/each}
	</div>
{/if}

<style>
	.list {
		display: grid;
		gap: 0.65rem;
	}
	.empty {
		color: var(--tg-theme-hint-color, #666);
		text-align: center;
		padding: 2rem 0;
	}
</style>
