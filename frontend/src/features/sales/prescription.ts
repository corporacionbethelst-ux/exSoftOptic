import type { VentaRecetaInline } from '../../types/sales';

export type PrescriptionValues = {
  fecha: string;
  od_esfera: string;
  od_cilindro: string;
  od_eje: string;
  od_adicion: string;
  oi_esfera: string;
  oi_cilindro: string;
  oi_eje: string;
  oi_adicion: string;
  dnp: string;
  altura: string;
  observaciones: string;
};

export const EMPTY_PRESCRIPTION: PrescriptionValues = {
  fecha: new Date().toISOString().slice(0, 10),
  od_esfera: '',
  od_cilindro: '',
  od_eje: '',
  od_adicion: '',
  oi_esfera: '',
  oi_cilindro: '',
  oi_eje: '',
  oi_adicion: '',
  dnp: '',
  altura: '',
  observaciones: '',
};

const EJE_ERROR = 'El eje debe estar entre 0° y 180°.';
const VISION_ERROR = 'Captura al menos una graduación (esfera o cilindro) para OD u OI.';

function toNumber(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed === '') return null;
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : null;
}

/**
 * Valida la receta con reglas clínicas básicas antes de enviarla al backend:
 * ejes en rango 0-180 y al menos una graduación (esfera o cilindro).
 */
export function validatePrescription(values: PrescriptionValues): string | null {
  for (const key of ['od_eje', 'oi_eje'] as const) {
    const parsed = toNumber(values[key]);
    if (parsed !== null && (parsed < 0 || parsed > 180)) return `${EJE_ERROR} (campo ${key.toUpperCase()})`;
  }
  const hasOd = values.od_esfera.trim() !== '' || values.od_cilindro.trim() !== '';
  const hasOi = values.oi_esfera.trim() !== '' || values.oi_cilindro.trim() !== '';
  if (!hasOd && !hasOi) return VISION_ERROR;
  return null;
}

export function hasPrescriptionData(values: PrescriptionValues): boolean {
  return Object.entries(values).some(([key, value]) => key !== 'fecha' && value.trim() !== '');
}

export function buildPrescriptionPayload(values: PrescriptionValues): VentaRecetaInline {
  return {
    fecha: values.fecha,
    od_esfera: toNumber(values.od_esfera),
    od_cilindro: toNumber(values.od_cilindro),
    od_eje: toNumber(values.od_eje),
    od_adicion: toNumber(values.od_adicion),
    oi_esfera: toNumber(values.oi_esfera),
    oi_cilindro: toNumber(values.oi_cilindro),
    oi_eje: toNumber(values.oi_eje),
    oi_adicion: toNumber(values.oi_adicion),
    dnp: toNumber(values.dnp),
    altura: toNumber(values.altura),
    observaciones: values.observaciones.trim() || null,
  };
}
