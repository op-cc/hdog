dc=docker-compose
DB_NAME=hdog_db

migrate:
	$(dc) exec hdog-python python manage.py migrate

build:
	$(dc) build

up:
	$(dc) up -d

dev: build up
	$(dc) exec hdog-python python manage.py migrate
	$(dc) exec hdog-python python manage.py loaddata admin_user

clean-data:
	$(dc) stop hdog-python
	$(dc) exec hdog-db psql -U postgres -c 'DROP DATABASE $(DB_NAME);'
	$(dc) exec hdog-db psql -U postgres -c 'CREATE DATABASE $(DB_NAME);'
	$(dc) up -d hdog-python
	$(dc) exec hdog-python python manage.py migrate
	$(dc) exec hdog-python python manage.py loaddata admin_user

tests:
	$(dc) up -d
	$(dc) exec hdog-python python manage.py test
