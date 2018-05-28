# HDog

### Запуск через docker

Получите исходный код приложения

    git clone git@github.com:op-cc/hdog.git

Установите `docker` и `docker-compose`. Также, для использования команды `make` вам понадобится пакет `build-essential`. В Ubuntu, Debian и т.п. установить их можно командой

    apt install docker docker-compose build-essential

Перейдите в каталог `docker`, скопируйте файл `.env.dist` в `.env`

    cd docker
    cp .env.dist .env

Отредактируйте файл `.env`:
1. измените значение `DJANGO_SETTINGS_MODULE` на `hdog.settings.dev`
1. в `VIRTUAL_HOST_EXPOSE_PORT` установите номер порта, по которому вам будет удобно открывать сайт. Можно оставить значение по умолчанию, тогда сайт будет доступен по адресу `localhost:8000`
1. в `DB_PASS` поместите пароль к СУБД
1. значение `SECRET_KEY` замените на случайный набор символов, букв и цифр. Рекомендуемая длина — не менее 50 символов. Можно получить выполнением следующей команды
```
head /dev/urandom | tr -dc 'A-Za-z0-9~!@#$%^&*()-_=+' | head -c 50 ; echo ''
```

#### Запуск dev-версии

    make dev
