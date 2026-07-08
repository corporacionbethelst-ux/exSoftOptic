import type { ReactNode } from 'react';

export type PageKey = 'dashboard' | 'users' | 'products' | 'sales' | 'lab';

export type NavigationItem = {
  key: PageKey;
  label: string;
  icon: ReactNode;
};
