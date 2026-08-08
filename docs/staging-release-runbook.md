# Ensayo de release en staging

## Objetivo y alcance

Staging debe usar el mismo Compose, imágenes y secuencia de migración que producción. Solo cambian dominio, credenciales, proveedores sandbox y volúmenes. El ensayo no autoriza un lanzamiento: produce evidencia técnica para UAT y para la aprobación operativa.

## Preparación

1. Crear `.env.staging` fuera del control de versiones.
2. Definir `BACKEND_IMAGE` y `FRONTEND_IMAGE` con tags de release inmutables o digest; se rechazan `latest` y `production`.
3. Inyectar `RELEASE_SHA` y `DEPLOYED_AT`, secretos exclusivos de staging y URLs sandbox.
4. Confirmar backup reciente y propietario de la decisión de rollback.
5. Congelar el candidato durante el ensayo; cualquier cambio genera un candidato nuevo.

## Plan revisable y ejecución

Generar primero un plan sin modificar infraestructura:

```bash
make staging-release-plan
```

Revisar `artifacts/staging-release-plan.json` y luego ejecutar:

```bash
python3 scripts/staging_release_rehearsal.py --execute \
  --env-file .env.staging --base-url https://staging.example.com
```

La secuencia audita configuración, renderiza Compose, obtiene/construye imágenes, ejecuta migraciones como trabajo único, despliega, espera salud/readiness y ejecuta smoke API y navegador. El registro termina en `technical-checks-passed`; UAT se aprueba por separado.

## Evidencia y UAT

- Conservar registro del ensayo, artefacto SLO, trazas/capturas E2E y SHA de release.
- Probar login, permisos, ventas, compras, inventario, laboratorio, facturación y exportaciones críticas.
- Registrar aprobador funcional, fecha, defectos conocidos y decisión explícita `GO`/`NO-GO`.
- Un defecto crítico, migración fallida, readiness inestable o incumplimiento SLO obliga a `NO-GO`.

## Rollback

1. Detener tráfico y conservar evidencia antes de modificar el entorno.
2. Volver a los tags inmutables anteriores para backend y frontend.
3. No ejecutar una migración descendente automáticamente: evaluar compatibilidad y restaurar backup solo con autorización del responsable de datos.
4. Repetir health, readiness y smoke después de restaurar la versión.
5. Documentar tiempos, pérdida de datos potencial y causa en el registro del ensayo.
