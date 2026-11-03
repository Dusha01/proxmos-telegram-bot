<script lang="ts">
	import GuestDetailPage from '$lib/pages/guestDetail/ui/GuestDetailPage.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<GuestDetailPage kind={data.kind} vmid={data.vmid} />
