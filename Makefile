.PHONY: help readiness readiness-fast frontend-check browser-e2e compose-check compose-production-check env-production-init config-production-audit

help: ## Mostrar comandos de verificacion del proyecto
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

readiness-fast: ## Ejecutar verificaciones estaticas de backend y frontend
	bash scripts/production_readiness.sh --fast

readiness: ## Ejecutar la puerta completa previa a staging/produccion
	bash scripts/production_readiness.sh --full

frontend-check: ## Ejecutar lint, tipos y build del frontend
	npm --prefix frontend run lint
	npm --prefix frontend run typecheck
	npm --prefix frontend run build

browser-e2e: ## Ejecutar smoke de navegador contra frontend/dist servido en :4173
	@bash -c 'python3 -m http.server 4173 --bind 127.0.0.1 --directory frontend/dist >/tmp/exsoftoptic-frontend.log 2>&1 & pid=$$!; trap "kill $$pid" EXIT; sleep 1; python3 e2e/browser_smoke.py'

compose-check: ## Validar la configuracion Docker Compose renderizada
	docker compose config --quiet

compose-production-check: ## Validar Docker Compose productivo con .env
	docker compose --env-file .env -f docker-compose.production.yml config --quiet

env-production-init: ## Generar .env productivo: make env-production-init domain=app.example.com
	python3 scripts/init_production_environment.py --domain "$(domain)"

config-production-audit: ## Validar .env con reglas estrictas de produccion
	python3 backend/scripts/validate_runtime_config.py --env-file .env --environment production --strict
