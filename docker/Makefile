dc=docker-compose

migrate:
	$(dc) exec hdog-python python manage.py migrate

build:
	$(dc) build

up:
	$(dc) up -d

dev: build up
	$(dc) exec hdog-python python manage.py migrate
	$(dc) exec hdog-python python manage.py loaddata admin_user
