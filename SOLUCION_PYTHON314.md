# Solución para Errores de Dependencias con Python 3.14

## Problema Identificado

Estás intentando instalar las dependencias del proyecto en **Python 3.14** en Windows, pero encuentras errores de compilación en:

1. **pydantic-core**: Error en `ForwardRef._evaluate()` - falta el argumento `recursive_guard`
2. **asyncpg**: Error de compilación C en Python 3.14
3. **psycopg2-binary**: Error de linker `_PyInterpreterState_Get` sin resolver

## Causa Raíz

Python 3.14 es una versión **muy reciente** (incluso en beta) que tiene cambios breaking en la API C de Python que afectan a paquetes con extensiones nativas compiladas en Rust/C.

## Soluciones

### Opción 1: Usar Python 3.12 (RECOMENDADA)

El proyecto está configurado y probado con **Python 3.12**. Esta es la opción más estable:

```bash
# Desinstalar Python 3.14 e instalar Python 3.12
# Descargar desde: https://www.python.org/downloads/release/python-31210/

# Crear nuevo virtual environment
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Opción 2: Usar las Versiones Actualizadas del requirements.txt

El archivo `requirements.txt` ya fue actualizado para soportar Python 3.14 con condiciones:

```txt
# Para Python < 3.14
asyncpg==0.30.0; python_version < "3.14"
psycopg2-binary==2.9.10; python_version < "3.14"
pydantic-core==2.27.1; python_version < "3.14"

# Para Python >= 3.14 (usa versiones desde git)
asyncpg @ git+https://github.com/MagicStack/asyncpg.git@master; python_version >= "3.14"
psycopg @ git+https://github.com/psycopg/psycopg.git; python_version >= "3.14"
pydantic-core @ git+https://github.com/pydantic/pydantic-core.git@main; python_version >= "3.14"
```

**Nota**: psycopg2-binary no tiene soporte para Python 3.14, se debe usar `psycopg` (la nueva versión).

### Opción 3: Esperar a que los Paquetes Tengan Wheels para Python 3.14

Muchos paquetes aún no publican wheels precompilados para Python 3.14. Necesitarías:

1. **Rust instalado** (para compilar pydantic-core)
2. **Visual Studio Build Tools** (para compilar extensiones C)
3. **PostgreSQL development libraries** (para asyncpg y psycopg)

## Estado Actual del Proyecto

✅ **En el entorno de testing (Python 3.12.10)**:
- 82 tests pasan exitosamente
- Todas las dependencias instaladas correctamente
- Sin errores críticos

❌ **Tests que requieren infraestructura** (54 tests):
- Requieren PostgreSQL, MongoDB, Redis corriendo
- NO son errores de dependencias
- Se ejecutan con: `docker-compose -f docker/test-services.yml up -d`

## Advertencias No Críticas

Estas advertencias aparecen pero NO bloquean la ejecución:

1. **Pydantic deprecated** (se resolverá en futura migración a Pydantic V3):
   ```
   Support for class-based `config` is deprecated, use ConfigDict instead
   ```

2. **Passlib crypt deprecated** (Python 3.13+):
   ```
   'crypt' is deprecated and slated for removal in Python 3.13
   ```

## Recomendación Final

**Usa Python 3.12** para desarrollo local. Es la versión LTS más estable y todas las dependencias tienen wheels precompilados disponibles.

Si necesitas Python 3.14 específicamente:
1. Asegúrate de tener Rust y VS Build Tools instalados
2. Usa el `requirements.txt` actualizado del proyecto
3. Considera usar contenedores Docker para aislar el entorno
