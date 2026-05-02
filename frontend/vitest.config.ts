import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: '../.test-results/fe-coverage',
      exclude: ['node_modules/', '.next/', 'src/components/ui/', '*.config.*'],
    },
  },
  resolve: {
    alias: { '@': resolve(__dirname, './src') },
  },
})
