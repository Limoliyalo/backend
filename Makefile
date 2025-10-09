APP_COMPOSE := docker compose --env-file .env -f docker-compose/db.yaml -f docker-compose/rabbitmq.yaml -f docker-compose/app.yaml
DB_COMPOSE := docker compose --env-file .env -f docker-compose/db.yaml

.PHONY: app app-down app-build app-restart app-db

app:
	$(APP_COMPOSE) up -d

app-down:
	$(APP_COMPOSE) down

app-build:
	$(APP_COMPOSE) build

app-restart:
	$(APP_COMPOSE) down
	$(APP_COMPOSE) up -d

app-db:
	$(DB_COMPOSE) up -d