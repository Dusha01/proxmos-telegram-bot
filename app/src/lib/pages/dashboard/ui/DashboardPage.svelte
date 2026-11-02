<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		goto('/guests/qemu', { replace: true });
	});
</script>

<p class="hint">Переход к списку VM…</p>

<style>
	.hint {
		text-align: center;
		color: var(--tg-theme-hint-color, #666);
		padding: 2rem 0;
	}
</style>
