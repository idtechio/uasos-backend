include .env
export
S ?=
DC_CMD = COMPOSE_PROFILES=$(DC_PROFILES) docker-compose -f $(DC_FILE) -p $(PROJECT_NAME)


install: build sleep db-up
reinstall: recreate db-reset
uninstall: db-clear down clean


build: build-base-image build-fnc-images
	$(DC_CMD) up --build -d --remove-orphans

build-base-image:
	./fnc-base-image/build.sh

build-fnc-images:
	GCF_NAME="hosts-insert" ./fnc-image/build.sh
	GCF_NAME="hosts-update" ./fnc-image/build.sh
	GCF_NAME="hosts-delete" ./fnc-image/build.sh
	GCF_NAME="guests-insert" ./fnc-image/build.sh
	GCF_NAME="guests-update" ./fnc-image/build.sh
	GCF_NAME="guests-delete" ./fnc-image/build.sh
	GCF_NAME="accounts-insert" ./fnc-image/build.sh
	GCF_NAME="accounts-update" ./fnc-image/build.sh

build-f:
	GCF_NAME=$(f) ./fnc-image/build.sh
	$(DC_CMD) up -d --remove-orphans


up:
	$(DC_CMD) up -d --remove-orphans

restart:
	$(DC_CMD) restart $(s)

ps:
	$(DC_CMD) ps

stop:
	$(DC_CMD) stop $(s)

down:
	$(DC_CMD) down $(s)

clean:
	$(DC_CMD) rm -f $(s)

recreate:
	$(DC_CMD) stop $(s)
	$(DC_CMD) rm -f $(s)
	$(DC_CMD) pull $(s)
	$(DC_CMD) up --build -d --remove-orphans $(s)

exec:
	$(DC_CMD) exec $(s) $(c)

logs:
	$(DC_CMD) logs --tail=100 -f $(s)


db-up:
	$(DC_CMD) exec postgres bash -c "psql -h localhost -p $(DB_PORT) -d $(DB_NAME) -U $(DB_USER) < /tmp/ddl/_create_all.sql"

db-clear:
	$(DC_CMD) exec postgres bash -c "psql -h localhost -p $(DB_PORT) -d $(DB_NAME) -U $(DB_USER) < /tmp/ddl/_drop_all.sql"

db-reset: db-clear db-up


sleep:
	sleep 10


.PHONY: %
.DEFAULT: up