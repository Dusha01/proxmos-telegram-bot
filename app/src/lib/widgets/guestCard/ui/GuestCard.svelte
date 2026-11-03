<script lang="ts">
	import type { GuestDto } from '$lib/shared/api/types';
	import GuestStatusBadge from '$lib/entities/guest/ui/GuestStatusBadge.svelte';

	let { guest, href }: { guest: GuestDto; href: string } = $props();
</script>

<a class="card" {href}>
	<div class="row">
		<strong>{guest.vmid}</strong>
		<GuestStatusBadge status={guest.status} />
	</div>
	<div class="name">{guest.name}</div>
</a>

<style>
	.card {
		display: block;
		text-decoration: none;
		color: inherit;
		background: var(--tg-theme-secondary-bg-color, #fff);
		border-radius: 1rem;
		padding: 0.9rem 1rem;
	}
	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}
	.name {
		margin-top: 0.35rem;
		font-size: 0.95rem;
	}
</style>
