export type NavItem = {
	id: string;
	label: string;
	href: string;
	disabled?: boolean;
};

export const navItems: NavItem[] = [
	{ id: 'qemu', label: 'VM', href: '/guests/qemu' },
	{ id: 'lxc', label: 'LXC', href: '/guests/lxc' },
	{ id: 'monitoring', label: 'Monitor', href: '/monitoring' },
	{ id: 'host', label: 'Host', href: '/host' }
];
