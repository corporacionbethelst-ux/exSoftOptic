import { useMemo } from 'react';
import type { PrescriptionValues } from './prescription';

type PrescriptionFormProps = {
  values: PrescriptionValues;
  onChange: (patch: Partial<PrescriptionValues>) => void;
};

const EYE_FIELDS = [
  { suffix: 'esfera', label: 'Esfera', step: '0.25', placeholder: '-2.50' },
  { suffix: 'cilindro', label: 'Cilindro', step: '0.25', placeholder: '-1.00' },
  { suffix: 'eje', label: 'Eje °', step: '1', placeholder: '90' },
  { suffix: 'adicion', label: 'Adición', step: '0.25', placeholder: '+1.50' },
] as const;

function eyeFields(prefix: 'od' | 'oi') {
  return EYE_FIELDS.map((field) => ({ ...field, key: `${prefix}_${field.suffix}` as keyof PrescriptionValues }));
}

export function PrescriptionForm({ values, onChange }: PrescriptionFormProps) {
  const summary = useMemo(() => {
    const parts: string[] = [];
    const fmt = (value: string) => (value.trim() === '' ? '—' : value.trim());
    parts.push(`OD: ${fmt(values.od_esfera)} / ${fmt(values.od_cilindro)} x ${fmt(values.od_eje)}°`);
    parts.push(`OI: ${fmt(values.oi_esfera)} / ${fmt(values.oi_cilindro)} x ${fmt(values.oi_eje)}°`);
    if (values.od_adicion.trim() || values.oi_adicion.trim()) parts.push(`Ad: ${fmt(values.od_adicion)} / ${fmt(values.oi_adicion)}`);
    if (values.dnp.trim()) parts.push(`DNP: ${values.dnp.trim()}`);
    return parts.join('  ·  ');
  }, [values]);

  return (
    <div className="wide-field prescription-form">
      <div className="split">
        <strong>Receta óptica</strong>
        <span className="muted compact">{summary}</span>
      </div>
      <div className="optical-grid">
        <label>Fecha examen
          <input type="date" value={values.fecha} max={new Date().toISOString().slice(0, 10)} onChange={(event) => onChange({ fecha: event.target.value })} required />
        </label>
        {(['od', 'oi'] as const).map((eye) =>
          eyeFields(eye).map((field) => (
            <label key={field.key}>
              {eye.toUpperCase()} · {field.label}
              <input
                type="number"
                step={field.step}
                min={field.suffix === 'eje' ? 0 : undefined}
                max={field.suffix === 'eje' ? 180 : undefined}
                placeholder={field.placeholder}
                value={values[field.key]}
                onChange={(event) => onChange({ [field.key]: event.target.value } as Partial<PrescriptionValues>)}
              />
            </label>
          )),
        )}
        <label>DNP (mm)
          <input type="number" min="0" step="0.5" placeholder="64" value={values.dnp} onChange={(event) => onChange({ dnp: event.target.value })} />
        </label>
        <label>Altura pupilar (mm)
          <input type="number" min="0" step="0.5" placeholder="22" value={values.altura} onChange={(event) => onChange({ altura: event.target.value })} />
        </label>
        <label className="prescription-notes">Observaciones
          <textarea rows={2} maxLength={500} placeholder="Notas del optometrista, tipo de lente recomendado, etc." value={values.observaciones} onChange={(event) => onChange({ observaciones: event.target.value })} />
        </label>
      </div>
    </div>
  );
}
