.PHONY: help install dev verify verify-fast ci e2e migrate-verify security-audit config-audit permissions-catalog db-backup db-restore outbox-worker-once outbox-worker test lint format run migrate seed clean docker-up docker-down

help:  ## Mostrar ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## Instalar dependencias
	pip install -r requirements.txt

dev:  ## Instalar dependencias de desarrollo
	pip install -r requirements-dev.txt

verify-fast:  ## Validar dependencias y sintaxis sin ejecutar pytest
	python scripts/verify_backend.py --skip-pytest

verify:  ## Validar dependencias, sintaxis y suite pytest
	python scripts/verify_backend.py

ci:  ## Ejecutar el mismo verificador usado por CI
	python scripts/verify_backend.py -- -q

e2e:  ## Ejecutar smoke tests end-to-end de API y base de datos
	python -m pytest tests/test_e2e_smoke.py -q

migrate-verify:  ## Validar migraciones Alembic contra DB de pruebas
	python scripts/verify_migrations.py --roundtrip

security-audit:  ## Auditar endpoints API con dependencias de autenticación/permisos
	python scripts/audit_api_security.py

config-audit:  ## Validar configuración runtime antes de despliegue
	python scripts/validate_runtime_config.py

permissions-catalog:  ## Regenerar catálogo RBAC de permisos declarados en endpoints
	python scripts/generate_permission_catalog.py

db-backup:  ## Crear backup PostgreSQL custom-format en ./backups
	python scripts/manage_database_backup.py backup

db-restore:  ## Restaurar backup PostgreSQL: make db-restore file=./backups/archivo.dump
	python scripts/manage_database_backup.py restore --input "$(file)" --clean

outbox-worker-once:  ## Despachar un lote del outbox y salir
	python scripts/run_outbox_worker.py --once

outbox-worker:  ## Ejecutar worker del outbox en modo continuo
	python scripts/run_outbox_worker.py

test:  ## Ejecutar tests
	pytest -v --cov=app

lint:  ## Ejecutar linters
	flake8 app/
	mypy app/

format:  ## Formatear código
	black app/ tests/
	isort app/ tests/

run:  ## Ejecutar servidor de desarrollo
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:  ## Crear migración
	alembic revision --autogenerate -m "$(msg)"

migrate-up:  ## Aplicar migraciones
	alembic upgrade head

migrate-down:  ## Revertir última migración
	alembic downgrade -1

seed:  ## Cargar datos semilla
	python -m app.core.seed

clean:  ## Limpiar archivos temporales
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +

docker-up:  ## Levantar contenedores Docker
	docker-compose up -d

docker-down:  ## Detener contenedores Docker
	docker-compose down

docker-logs:  ## Ver logs de contenedores
	docker-compose logs -f

docker-restart:  ## Reiniciar contenedores
	docker-compose restart

db-shell:  ## Conectar a PostgreSQL
	docker-compose exec postgres psql -U optica_user -d optica_system

redis-shell:  ## Conectar a Redis
	docker-compose exec redis redis-cli

mongo-shell:  ## Conectar a MongoDB
	docker-compose exec mongodb mongosh -u optica_admin -p optica_mongo_2026