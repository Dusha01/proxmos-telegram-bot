export type ToastTone = 'success' | 'error' | 'info';

export type ToastItem = {
	id: number;
	message: string;
	tone: ToastTone;
};

let nextId = 1;

class ToastStore {
	items: ToastItem[] = $state([]);

	push(message: string, tone: ToastTone = 'info', timeoutMs = 4500) {
		const id = nextId++;
		this.items = [...this.items, { id, message, tone }];
		setTimeout(() => {
			this.items = this.items.filter((item) => item.id !== id);
		}, timeoutMs);
	}
}

export const toastStore = new ToastStore();
