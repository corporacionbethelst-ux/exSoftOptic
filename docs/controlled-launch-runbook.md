# Lanzamiento controlado a producción

## Estrategia

El lanzamiento usa canary progresivo `5% → 25% → 50% → 100%`. Cada incremento requiere imágenes inmutables, ticket de cambio, responsable de release, guardia operativa activa y evidencia del ensayo de staging. No se mezcla más de un SHA candidato durante una ventana.

## Puerta previa

- UAT, migraciones, restore y smoke de staging aprobados para el mismo SHA.
- Backup verificado y versión anterior disponible mediante tags inmutables.
- Dashboard, alertas, paging y canal de incidente operativos.
- Ventana, responsables, comunicaciones y criterios de aborto aprobados.
- Migraciones compatibles hacia atrás durante toda la ventana canary.

## Evaluación de cada etapa

Recolectar un JSON con `error_rate`, `p95_ms`, `p99_ms`, `health_success_rate` y `observation_minutes`. Evaluarlo sin alterar tráfico:

```bash
python3 scripts/evaluate_production_rollout.py \
  --metrics /secure/canary-metrics.json --release-sha abc1234 \
  --current-stage 5 --approved-by "Release Manager" --change-ticket CHG-1234
```

La decisión queda en `artifacts/production-rollout-decision.json`. `advance` autoriza únicamente la siguiente etapa; `hold` conserva el porcentaje; `rollback` devuelve código 2 y exige retirar el candidato. El cambio de tráfico se realiza en el balanceador de la plataforma, nunca desde este evaluador.

## Rollback y aborto

1. Congelar nuevos incrementos y declarar el canal operativo.
2. Llevar tráfico del candidato a 0% y confirmar la versión estable anterior.
3. No revertir automáticamente migraciones; activar el plan de recuperación de datos aprobado.
4. Comprobar health, readiness, tasa de error, colas y operaciones críticas.
5. Informar impacto y abrir postmortem si hubo afectación de usuarios o datos.

Fallo de health, error superior a 1%, p95 mayor a 750 ms o p99 mayor a 1500 ms dispara rollback. Una ventana incompleta solo produce `hold`, evitando promover con evidencia insuficiente.
