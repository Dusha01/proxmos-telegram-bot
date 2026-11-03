import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	resolve: {
		alias: [
			{ find: '$lib', replacement: path.resolve('src/lib') },
			{
				find: '$app/env/private',
				replacement: path.resolve('tests/mocks/app-env-private.ts')
			},
			{ find: '$app/env', replacement: path.resolve('tests/mocks/app-env.ts') }
		]
	},
	test: {
		include: ['tests/**/*.test.ts']
	}
});
