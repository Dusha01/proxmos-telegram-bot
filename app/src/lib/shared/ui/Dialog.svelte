<script lang="ts">
	let {
		open = false,
		title = '',
		message = '',
		confirmLabel = 'Подтвердить',
		cancelLabel = 'Отмена',
		onConfirm,
		onCancel
	}: {
		open?: boolean;
		title?: string;
		message?: string;
		confirmLabel?: string;
		cancelLabel?: string;
		onConfirm?: () => void;
		onCancel?: () => void;
	} = $props();
</script>

{#if open}
	<div class="backdrop" role="presentation" onclick={onCancel}></div>
	<div class="dialog" role="dialog" aria-modal="true">
		<h2>{title}</h2>
		<p>{message}</p>
		<div class="actions">
			<button type="button" class="cancel" onclick={onCancel}>{cancelLabel}</button>
			<button type="button" class="confirm" onclick={onConfirm}>{confirmLabel}</button>
		</div>
	</div>
{/if}

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.35);
		z-index: 40;
	}
	.dialog {
		position: fixed;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		z-index: 50;
		width: min(92vw, 22rem);
		background: var(--tg-theme-bg-color, #fff);
		color: var(--tg-theme-text-color, #111);
		border-radius: 1rem;
		padding: 1rem;
		box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
	}
	h2 {
		margin: 0 0 0.5rem;
		font-size: 1.05rem;
	}
	p {
		margin: 0 0 1rem;
		color: var(--tg-theme-hint-color, #666);
		line-height: 1.4;
	}
	.actions {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}
	button {
		border: none;
		border-radius: 0.75rem;
		padding: 0.65rem;
		font-weight: 600;
		cursor: pointer;
	}
	.cancel {
		background: var(--tg-theme-secondary-bg-color, #eee);
	}
	.confirm {
		background: var(--tg-theme-button-color, #2481cc);
		color: var(--tg-theme-button-text-color, #fff);
	}
</style>
