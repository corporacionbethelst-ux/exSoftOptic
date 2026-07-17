import type { ReactNode } from 'react';

export type PageKey = 'dashboard' | 'users' | 'products' | 'sales' | 'purchases' | 'lab';

export type NavigationItem = {
  key: PageKey;
  label: string;
  icon: ReactNode;
};
