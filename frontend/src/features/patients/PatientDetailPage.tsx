import { ArrowLeft } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { patientsService } from '../../services';
import { useApiResource } from '../../hooks/useApiResource';
import type { RecetaOptica } from '../../types/patients';
import { dateTime, number } from '../../utils/format';

function prescriptionRow(title: string, esfera: keyof RecetaOptica, cilindro: keyof RecetaOptica, eje: keyof RecetaOptica, adicion: keyof RecetaOptica) {
  return { title, keys: { esfera, cilindro, eje, adicion } };
}

const RX_ROWS = [
  prescriptionRow('Ojo Derecho (OD)', 'od_esfera', 'od_cilindro', 'od_eje', 'od_adicion'),
  prescriptionRow('Ojo Izquierdo (OI)', 'oi_esfera', 'oi_cilindro', 'oi_eje', 'oi_adicion'),
];

function rxTone(fecha: string) {
  const ageDays = (Date.now() - new Date(fecha).getTime()) / 86_400_000;
  if (ageDays > 365) return 'danger' as const;
  if (ageDays > 180) return 'warning' as const;
  return 'success' as const;
}

export function PatientDetailPage() {
  const { patientId = '' } = useParams();

  const patient = useApiResource(() => patientsService.patient(patientId), Boolean(patientId));
  const prescriptions = useApiResource(
    () => patientsService.prescriptions({ paciente_id: patientId, limit: 100 }),
    Boolean(patientId),
  );

  const data = patient.data;
  const rxItems = prescriptions.data ?? [];
  const latestRx = rxItems[0] ?? null;

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Pacientes"
        title={data ? `Expediente de ${data.nombre}` : 'Expediente del paciente'}
        description="Historial clínico óptico: recetas registradas y antigüedad para seguimiento de control visual."
        actions={<Link to="/patients" className="secondary-button"><ArrowLeft size={16} /> Volver a pacientes</Link>}
      />

      <InlineState loading={patient.loading} error={patient.error} empty={!data} emptyTitle="Paciente no encontrado">
        {data ? (
          <>
            <div className="metric-grid">
              <div className="metric-card"><span className="muted">Fecha de nacimiento</span><strong>{data.fecha_nacimiento ? dateTime(data.fecha_nacimiento) : '—'}</strong></div>
              <div className="metric-card"><span className="muted">Teléfono</span><strong>{data.telefono ?? '—'}</strong></div>
              <div className="metric-card"><span className="muted">Correo</span><strong>{data.email ?? '—'}</strong></div>
              <div className="metric-card"><span className="muted">Recetas registradas</span><strong>{rxItems.length}</strong></div>
            </div>

            {latestRx ? (
              <SectionPanel title="Última receta óptica" description={`Fecha: ${dateTime(latestRx.fecha)}`} footer={<StatusBadge tone={rxTone(latestRx.fecha)}>{latestRx.fecha}</StatusBadge>}>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Ojo</th><th>Esfera</th><th>Cilindro</th><th>Eje</th><th>Adición</th></tr></thead>
                    <tbody>
                      {RX_ROWS.map((row) => (
                        <tr key={row.title}>
                          <td>{row.title}</td>
                          <td>{number(latestRx[row.keys.esfera] as number | string | null)}</td>
                          <td>{number(latestRx[row.keys.cilindro] as number | string | null)}</td>
                          <td>{number(latestRx[row.keys.eje] as number | string | null)}</td>
                          <td>{number(latestRx[row.keys.adicion] as number | string | null)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="muted compact">DNP: {number(latestRx.dnp)} · Altura: {number(latestRx.altura)}{latestRx.observaciones ? ` · ${latestRx.observaciones}` : ''}</p>
              </SectionPanel>
            ) : null}

            <SectionPanel title="Historial de recetas" footer={<span className="muted compact">{rxItems.length} registros</span>}>
              <InlineState loading={prescriptions.loading} error={prescriptions.error} empty={rxItems.length === 0} emptyTitle="Sin recetas" emptyDescription="Registra la primera receta desde Ventas o Pacientes.">
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Fecha</th><th>OD (E/C/A)</th><th>OI (E/C/A)</th><th>DNP</th><th>Vigencia</th><th>Observaciones</th></tr></thead>
                    <tbody>
                      {rxItems.map((rx) => (
                        <tr key={rx.id}>
                          <td>{dateTime(rx.fecha)}</td>
                          <td>{number(rx.od_esfera)} / {number(rx.od_cilindro)} / {number(rx.od_eje)}</td>
                          <td>{number(rx.oi_esfera)} / {number(rx.oi_cilindro)} / {number(rx.oi_eje)}</td>
                          <td>{number(rx.dnp)}</td>
                          <td><StatusBadge tone={rxTone(rx.fecha)}>{rx.fecha}</StatusBadge></td>
                          <td className="compact">{rx.observaciones ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </InlineState>
            </SectionPanel>
          </>
        ) : null}
      </InlineState>
    </section>
  );
}
