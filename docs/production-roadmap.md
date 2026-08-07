# Ruta de producción en 15 fases

Este documento es la fuente de verdad para medir el avance hacia producción. Una fase solo se considera cerrada cuando cumple todos sus criterios de salida; tener código implementado no equivale a una aprobación operativa.

## Estado resumido

| Fase | Alcance | Estado | Criterio pendiente principal |
| --- | --- | --- | --- |
| 1 | Base funcional y contratos API | En cierre | Ejecutar suite completa y smoke manual en entorno reproducible |
| 2 | Automatización CI y puertas de calidad | En cierre | Activar protección de rama y exigir CI backend/frontend |
| 3 | Configuración y secretos | En curso | Integrar un gestor de secretos real |
| 4 | Seguridad de aplicación | Parcial | Revisar resultados CodeQL, ejecutar DAST y pentest |
| 5 | Datos, migraciones y recuperación | En curso | Ensayo documentado de restauración en base desechable |
| 6 | Infraestructura productiva | Pendiente | Definir plataforma, TLS, DNS y aislamiento de red |
| 7 | Observabilidad | Parcial | Dashboards, alertas y trazas en plataforma destino |
| 8 | Rendimiento y capacidad | Pendiente | Pruebas representativas y objetivos SLO |
| 9 | Resiliencia e integraciones | Parcial | Fallos inyectados, reintentos y circuit breakers validados |
| 10 | Calidad funcional E2E | Pendiente | Automatizar recorridos críticos del navegador |
| 11 | Cumplimiento y privacidad | Pendiente | Políticas de retención, consentimiento y derechos ARCO |
| 12 | Operación y soporte | Parcial | Guardias, escalamiento e incident response probado |
| 13 | Staging y ensayo de release | Pendiente | Despliegue idéntico a producción y UAT aprobada |
| 14 | Lanzamiento controlado | Pendiente | Plan canary/blue-green, rollback y ventana aprobados |
| 15 | Estabilización y mejora continua | Pendiente | Métricas post-lanzamiento y revisión de incidentes |

## Puerta automatizada actual

Desde la raíz del repositorio:

```bash
make readiness-fast
make readiness
```

`readiness-fast` valida sintaxis, contrato API, seguridad declarativa, migraciones, RBAC y el frontend sin requerir servicios. `readiness` añade Docker Compose, preflight, pruebas backend y roundtrip de migraciones. La segunda orden requiere Docker, dependencias Python y servicios de prueba disponibles.

## Cierre de la fase 1

- [ ] `make readiness` finaliza sin errores en una máquina limpia.
- [ ] Login, usuarios, productos, inventario, ventas, compras, CRM, pacientes, laboratorio, finanzas y facturación tienen smoke test aprobado.
- [ ] No existen defectos críticos o altos abiertos en los recorridos anteriores.
- [ ] El contrato OpenAPI generado fue revisado contra los clientes TypeScript.
- [ ] El responsable funcional firma la evidencia de aceptación.

## Cierre de la fase 2

- [x] CI backend valida dependencias, seguridad, RBAC, migraciones y pytest.
- [x] CI frontend instala desde lockfile, ejecuta lint, tipos, build y publica el bundle como artefacto.
- [x] Existe una puerta unificada local rápida y completa.
- [ ] Las ramas `main` y `develop` requieren ambos checks antes de merge.
- [x] Dependabot está configurado para npm, pip y GitHub Actions.
- [ ] El análisis de dependencias y alertas de seguridad está habilitado en el proveedor Git.
- [ ] Se define quién puede aprobar excepciones y por cuánto tiempo.

## Avance de la fase 3

- [x] Existe plantilla versionada sin secretos reales.
- [x] Existe generación criptográficamente segura de `.env` con permisos `0600`.
- [x] La auditoría bloquea debug, algoritmos JWT inválidos, localhost y credenciales de ejemplo en producción.
- [x] Las reglas críticas de configuración tienen pruebas automatizadas.
- [ ] Las credenciales se inyectan desde Vault, AWS Secrets Manager, Azure Key Vault o equivalente.
- [ ] Existe procedimiento probado de rotación de JWT, base de datos, MongoDB y proveedores.
- [ ] Los accesos a secretos dejan trazabilidad y aplican mínimo privilegio.

## Avance de la fase 4

- [x] CodeQL analiza Python y TypeScript en push, pull request y semanalmente.
- [ ] Revisar y resolver todos los hallazgos altos/críticos de CodeQL.
- [ ] Incorporar DAST contra staging y revisión de cabeceras HTTP/TLS.
- [ ] Ejecutar pentest independiente y cerrar los hallazgos de severidad alta/crítica.

## Avance de la fase 5

- [x] Los backups usan formato custom, sin ownership ni privilegios del origen.
- [x] Las contraseñas de PostgreSQL se pasan mediante `PGPASSWORD` y no aparecen en argumentos o logs.
- [x] Cada backup genera un manifiesto SHA-256 y el restore productivo exige su validación.
- [x] Existen pruebas de detección de manipulación del backup.
- [ ] Ejecutar mensualmente un restore completo sobre una base desechable.
- [ ] Medir y documentar RPO/RTO aprobados por negocio.
- [ ] Replicar backups cifrados fuera del host y probar su recuperación.

## Regla de avance

No se marca una fase como completa por porcentaje estimado. Cada casilla pendiente debe tener evidencia (enlace de CI, reporte, captura, ticket o acta). Las fases pueden trabajarse en paralelo, pero ninguna dependencia crítica se omite para acelerar el lanzamiento.
