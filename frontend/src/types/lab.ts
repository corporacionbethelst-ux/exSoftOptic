import type { DateTimeString, ID } from './common';

export type OrdenLaboratorioEtapa = {
  id: ID;
  etapa: string;
  estado: string;
};

export type OrdenLaboratorio = {
  id: ID;
  folio: string;
  estado: string;
  prioridad: string;
  fecha_prometida?: DateTimeString | null;
  observaciones?: string | null;
  etapas?: OrdenLaboratorioEtapa[];
};
