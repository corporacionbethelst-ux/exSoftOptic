# Estabilización posterior al lanzamiento

## Ventana de observación

La versión permanece en estabilización durante al menos 14 días, con revisiones en los días 1, 3, 7 y 14. Durante este período se limita el cambio funcional: solo se aceptan correcciones aprobadas, seguridad urgente y mitigaciones de incidentes.

## Evidencia diaria

Registrar por release SHA: disponibilidad, tasa de error, p95, incidentes SEV-1/SEV-2, defectos críticos abiertos, volumen de soporte, colas, capacidad y cambios aplicados. Los datos deben provenir de dashboards o tickets conservados, no de estimaciones manuales sin referencia.

El archivo de evaluación incluye `days_observed`, `availability`, `error_rate`, `p95_ms`, `sev1_incidents`, `sev2_incidents`, `open_critical_defects` y `completed_reviews`.

La evaluación rechaza campos ausentes, `NaN`, infinitos, valores negativos, tasas fuera de `0..1`, contadores no enteros y listas de revisiones mal formadas. Evidencia inválida nunca puede producir el estado `stabilized`.

```bash
python3 scripts/evaluate_stabilization.py \
  --evidence /secure/stabilization.json --release-sha abc1234 \
  --owner "Service Owner" --review-ticket PIR-1234
```

## Interpretación

- `continue-observation`: aún no concluyen los 14 días.
- `review-required`: faltan revisiones obligatorias.
- `corrective-action`: se incumplió un SLO o límite de incidentes/defectos; devuelve código 2.
- `stabilized`: transcurrió la ventana y todas las revisiones y umbrales fueron satisfechos.

## Revisión de cierre

La revisión conjunta cubre SLO y capacidad, incidentes y soporte, seguridad y privacidad, comentarios de producto y deuda técnica. Cada mejora debe tener propietario, prioridad y fecha objetivo. El estado `stabilized` no cierra por sí solo las demás fases: las aprobaciones externas y evidencias pendientes de la ruta de producción siguen siendo obligatorias.
