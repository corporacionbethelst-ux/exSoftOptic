export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '',
  appName: import.meta.env.VITE_APP_NAME ?? 'ExSoftOptic',
  demoUsername: import.meta.env.VITE_DEMO_USERNAME ?? 'admin',
  demoPassword: import.meta.env.VITE_DEMO_PASSWORD ?? 'Admin123!',
} as const;
