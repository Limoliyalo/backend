COMPOSE := docker compose -f docker-compose.yaml

.PHONY: app app-down app-build app-restart app-db

app:
	$(COMPOSE) up -d

app-down:
	$(COMPOSE) down

app-build:
	$(COMPOSE) build

app-restart:
	$(COMPOSE) down
	$(COMPOSE) up -d

app-db:
	$(COMPOSE) up -d postgres