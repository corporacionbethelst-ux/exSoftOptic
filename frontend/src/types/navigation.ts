import type { ReactNode } from 'react';

export type PageKey = 'dashboard' | 'users' | 'products' | 'inventory' | 'sales' | 'purchases' | 'crm' | 'patients' | 'lab' | 'finance';

export type NavigationItem = {
  key: PageKey;
  label: string;
  icon: ReactNode;
};
