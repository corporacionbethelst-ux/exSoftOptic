# Registro de errores de pruebas

Este archivo se usará como bitácora viva para registrar los errores que aparezcan al ejecutar pruebas, verificaciones, migraciones o comandos del backend.

La intención es que puedas pegar aquí los mensajes completos de error para que queden centralizados y sea más fácil identificar qué se debe corregir en cada avance del proyecto.

## Cómo actualizar este archivo

Cuando ocurra un error, agrega una nueva entrada al inicio o al final de la sección **Errores registrados** usando el siguiente formato sugerido:

~~~md
### Error YYYY-MM-DD HH:mm - Nombre breve del problema

**Comando ejecutado:**
```bash
comando que produjo el error
```

**Contexto:**
- Entorno: local / Docker / CI / staging
- Rama o commit:
- Base de datos usada:
- Variables relevantes:

**Mensaje de error completo:**
```text
Pegar aquí el traceback, salida de consola o mensaje completo.
```

**Resultado esperado:**
Describir qué se esperaba que ocurriera.

**Notas adicionales:**
Agregar cualquier observación, captura, log adicional o paso previo relevante.
~~~

## Errores registrados

> Aún no hay errores registrados. Agrega aquí los mensajes cuando aparezcan durante las pruebas.

