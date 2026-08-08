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
| 6 | Infraestructura productiva | En curso | Definir plataforma destino, TLS, DNS y proxy perimetral |
| 7 | Observabilidad | En curso | Instalar Prometheus/log aggregation y validar alertas |
| 8 | Rendimiento y capacidad | En curso | Ejecutar baseline y prueba sostenida con datos representativos |
| 9 | Resiliencia e integraciones | En curso | Validar fallos inyectados contra sandbox de proveedores |
| 10 | Calidad funcional E2E | En curso | Ampliar cobertura a flujos transaccionales con backend real |
| 11 | Cumplimiento y privacidad | En curso | Aprobación legal de retención, consentimiento y derechos ARCO |
| 12 | Operación y soporte | En curso | Aprobar guardias, escalamiento y ejecutar simulacro SEV-1 |
| 13 | Staging y ensayo de release | En curso | Ejecutar el ensayo y obtener UAT aprobada |
| 14 | Lanzamiento controlado | En curso | Ejecutar canary real y aprobar la ventana de cambio |
| 15 | Estabilización y mejora continua | En curso | Completar 14 días de observación y revisión post-implementación |

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

## Avance de la fase 6

- [x] Existe un Compose productivo separado, sin montajes de código ni servidores con reload.
- [x] PostgreSQL, Redis y MongoDB no publican puertos al host y viven en una red interna.
- [x] Redis exige autenticación y todos los secretos críticos son obligatorios al renderizar Compose.
- [x] Backend y frontend usan filesystem de solo lectura, `no-new-privileges` y capacidades reducidas.
- [x] Nginx se ejecuta sin privilegios, incluye cabeceras de seguridad y caché inmutable de assets.
- [x] CI renderiza Compose y construye las imágenes de aplicación.
- [ ] Instalar proxy/LB perimetral con TLS, certificados renovables y límite de solicitudes.
- [ ] Definir DNS, firewall, segmentación por ambiente y almacenamiento administrado.
- [ ] Definir estrategia de escalamiento, presupuesto y alta disponibilidad.

## Avance de la fase 7

- [x] Logs HTTP estructurados incluyen correlation ID, ruta normalizada, estado y duración.
- [x] Los correlation IDs externos se validan para evitar inyección y valores sin límite.
- [x] Métricas usan plantillas de ruta para evitar cardinalidad por UUID/ID.
- [x] Prometheus expone requests, errores, in-flight e histograma de latencia.
- [x] El scrape `/metrics` usa un token dedicado, distinto del JWT de usuarios.
- [x] Existe un conjunto inicial de alertas para disponibilidad, 5xx, latencia, excepciones y reinicios.
- [ ] Desplegar Prometheus/Grafana y agregación central de logs en la plataforma elegida.
- [ ] Conectar Alertmanager con guardias y probar cada alerta mediante simulacro.
- [ ] Incorporar trazas distribuidas OpenTelemetry en API, workers y proveedores externos.

## Avance de la fase 8

- [x] Existe un plan SLO versionado para staging con error, p95, p99 y throughput mínimo.
- [x] El runner soporta múltiples URLs, warmup, concurrencia, timeout y headers autenticados.
- [x] Los resultados incluyen percentiles, RPS, códigos HTTP, errores y artefacto JSON.
- [x] Una regresión de cualquiera de los umbrales produce código de salida no cero para CI.
- [x] Las funciones de resumen, umbrales y carga de planes tienen pruebas automatizadas.
- [x] CI ejecuta el smoke SLO y conserva el resultado JSON como artefacto.
- [ ] Ejecutar baseline sobre endpoints de negocio y dataset con volumen representativo.
- [ ] Ejecutar soak test de 2–8 horas y verificar memoria, conexiones y crecimiento de colas.
- [ ] Aprobar capacidad máxima, margen de seguridad y estrategia de escalamiento.

## Avance de la fase 9

- [x] Los reintentos usan backoff exponencial con jitter y límites configurables.
- [x] Errores permanentes 4xx no se reintentan ni degradan el circuit breaker.
- [x] Timeouts, fallos de conexión, 408, 429 y 5xx transitorios sí se reintentan.
- [x] CFDI y banca tienen circuit breakers independientes con estado half-open.
- [x] El circuito abierto falla rápido y evita saturar proveedores degradados.
- [x] Existen pruebas de apertura, recuperación, errores no contabilizados y clasificación HTTP.
- [ ] Ejecutar fault injection contra sandboxes reales de CFDI y banca.
- [ ] Definir reconciliación manual y automática para operaciones con resultado incierto.
- [ ] Crear dashboards y alertas específicas de circuit breaker y reintentos.

## Avance de la fase 10

- [x] Existe smoke Chromium reproducible para login inválido, login correcto, navegación y logout.
- [x] El navegador valida rotación automática cuando expira el access token.
- [x] Las APIs se interceptan con contratos deterministas para evitar pruebas inestables.
- [x] CI construye el frontend, instala Chromium y ejecuta el smoke en cada cambio relevante.
- [x] Fallos conservan screenshot y trace Playwright durante 14 días.
- [ ] Ejecutar los mismos recorridos contra backend y base de datos reales en staging.
- [ ] Cubrir ventas, compras, inventario, laboratorio y facturación con datos aislados.
- [ ] Añadir matriz Chromium/Firefox/WebKit y viewport móvil para release candidates.

## Avance de la fase 11

- [x] Existe clasificación documentada de datos personales, clínicos y secretos.
- [x] Operadores autorizados pueden exportar un sujeto con aislamiento por empresa y auditoría.
- [x] Existe anonimización confirmada que conserva integridad referencial y registros obligatorios.
- [x] Exportación y anonimización usan permisos RBAC independientes.
- [x] Logs estructurados redactan bearer tokens, secretos, passwords, API keys y emails.
- [x] Existe una propuesta de retención y checklist operativo sujeto a aprobación legal.
- [ ] Obtener aprobación jurídica por país para privacidad, expediente clínico y fiscalidad.
- [ ] Registrar consentimiento, finalidad, versión del aviso y revocación en el modelo de datos.
- [ ] Automatizar retención únicamente después de aprobar legal holds y períodos definitivos.

## Avance de la fase 12

- [x] Existe clasificación SEV-1 a SEV-4 con objetivos iniciales de respuesta y comunicación.
- [x] Existe checklist de primeros 15 minutos, mitigación, comunicación y postmortem.
- [x] `/health` identifica release SHA y fecha de despliegue para correlacionar incidentes.
- [x] Producción exige metadata de release válida en la auditoría de configuración.
- [x] Existe colector diagnóstico que excluye deliberadamente variables de entorno y logs.
- [x] El diagnóstico incluye salud, readiness, Git, capacidad del host y estado Compose.
- [ ] Aprobar SLA/OLA, calendario de guardias y contactos de escalamiento.
- [ ] Ejecutar game day SEV-1 y documentar tiempos reales, decisiones y mejoras.
- [ ] Integrar paging, status page y sistema formal de gestión de incidentes.

## Avance de la fase 13

- [x] Existe un plan de release versionado con evidencia técnica obligatoria.
- [x] El ensayo reutiliza el Compose productivo y separa el proyecto de staging.
- [x] La secuencia audita configuración y ejecuta migraciones antes del despliegue.
- [x] El proceso espera health/readiness y ejecuta smoke API y navegador.
- [x] Se rechazan tags de imagen mutables durante la ejecución del ensayo.
- [x] Existe runbook de UAT, criterios `GO`/`NO-GO` y rollback sin downgrade automático.
- [ ] Ejecutar el ensayo completo con infraestructura y proveedores sandbox reales.
- [ ] Conservar evidencia de migración, SLO, E2E y restauración de la versión anterior.
- [ ] Obtener aprobación UAT de responsables funcionales y operativos.

## Avance de la fase 14

- [x] Existe una política canary versionada con etapas 5%, 25%, 50% y 100%.
- [x] Cada etapa tiene una ventana mínima y umbrales de error, salud, p95 y p99.
- [x] El evaluador emite decisiones auditables `advance`, `hold`, `rollback` o `complete`.
- [x] Una violación crítica devuelve código no cero para detener automatizaciones.
- [x] Cada decisión identifica SHA, aprobador, ticket de cambio, métricas y siguiente etapa.
- [x] Existe runbook de lanzamiento, aborto y rollback sin downgrade automático de datos.
- [ ] Configurar tráfico canary/blue-green en el balanceador de la plataforma elegida.
- [ ] Aprobar ventana, responsables, comunicación y versión estable de rollback.
- [ ] Ejecutar el lanzamiento controlado y conservar evidencia de cada etapa.

## Avance de la fase 15

- [x] Existe una política versionada de estabilización de 14 días con cuatro checkpoints.
- [x] Se evalúan disponibilidad, errores, p95, incidentes y defectos críticos por release SHA.
- [x] El evaluador distingue observación, revisión pendiente, acción correctiva y estabilización.
- [x] Los incumplimientos críticos devuelven código no cero para activar seguimiento.
- [x] El cierre exige revisiones de capacidad, soporte, seguridad, producto y deuda técnica.
- [x] Existe runbook de evidencia diaria y revisión post-implementación.
- [ ] Ejecutar los checkpoints con telemetría real del lanzamiento productivo.
- [ ] Realizar revisión post-implementación y asignar responsables a cada mejora.
- [ ] Obtener aprobación final de servicio estable por negocio, operaciones y tecnología.

## Regla de avance

No se marca una fase como completa por porcentaje estimado. Cada casilla pendiente debe tener evidencia (enlace de CI, reporte, captura, ticket o acta). Las fases pueden trabajarse en paralelo, pero ninguna dependencia crítica se omite para acelerar el lanzamiento.
