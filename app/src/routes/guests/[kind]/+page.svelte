<script lang="ts">
	import GuestListPage from '$lib/pages/guest-list/ui/GuestListPage.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<GuestListPage kind={data.kind} />
