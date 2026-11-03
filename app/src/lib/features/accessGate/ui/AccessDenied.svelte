<script lang="ts">
	import { dev } from '$app/env';

	let {
		userId,
		chatId,
		message,
		detail
	}: {
		userId?: number;
		chatId?: number;
		message?: string;
		detail?: string;
	} = $props();
</script>

<div class="denied">
	<h2>Нет доступа</h2>
	<p>{message ?? 'Нет доступа.'}</p>
	{#if dev && detail}
		<p class="meta">{detail}</p>
	{/if}
	{#if dev && userId}
		<p class="meta">user_id: {userId}</p>
	{/if}
	{#if dev && chatId}
		<p class="meta">chat_id: {chatId}</p>
	{/if}
</div>

<style>
	.denied {
		padding: 2rem 0.5rem;
		text-align: center;
	}
	h2 {
		margin: 0 0 0.5rem;
	}
	p {
		margin: 0.35rem 0;
		color: var(--tg-theme-hint-color, #666);
		line-height: 1.45;
	}
	.meta {
		font-family: ui-monospace, monospace;
		font-size: 0.85rem;
	}
</style>
