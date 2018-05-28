SLEEP_TIMER=5
dc=docker-compose

migrate:
	$(dc) exec hdog-python python manage.py migrate

build:
	$(dc) build

up:
	$(dc) up -d hdog-db
	sleep $(SLEEP_TIMER)
	$(dc) up -d hdog-python

dev: build up
	sleep $(SLEEP_TIMER)
	$(dc) exec hdog-python python manage.py migrate
