.PHONY: help build start stop log remove

#==========================================

VENV_NAME?=venv
ENV=. .env
VENV_ACTIVATE=. ${VENV_NAME}/bin/activate
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip3
PWD=$(shell pwd)
DOCKER=$(shell which docker)
COMPOSE=$(shell which docker-compose)
COMPOSE_FILE=docker-compose.yml
#==========================================

.DEFAULT: help

help:
	@echo "make start	- Start Redis in Docker"
	@echo "make stop	- Stopping Redis in Docker"
	@echo "make log	- Output of logs for Redis in Docker"
	@echo "make remove	- Deleting a Redis in Docker"

#=============================================
# Установка зависимостей для работы приложений
install:
	[ -d $(VENV_NAME) ] || python3 -m $(VENV_NAME) $(VENV_NAME)
	${VENV_NAME}/bin/pip3 install pip -U
	${VENV_NAME}/bin/pip3 install wheel

# Активация виртуального окружения для работы приложений
venv: ${VENV_NAME}/bin/activate
$(VENV_NAME)/bin/activate: ${SETUP}
	[ -d $(VENV_NAME) ] || python3 -m $(VENV_NAME) $(VENV_NAME)
	${PIP} install -U pip
	${PIP} install -e .
	${VENV_ACTIVATE}

#==========================================
start: ${DOCKER} ${DOCKERFILE}
	[ `${DOCKER} ps | grep ${RETHINKDB} | wc -l` -eq 1 ] || \
	${COMPOSE} -f ${COMPOSE_FILE} up -d

stop: ${DOCKER} ${DOCKERFILE}
	! [ `${DOCKER} ps | grep ${RETHINKDB} | wc -l` -eq 1 ] || \
	${COMPOSE} -f ${COMPOSE_FILE} down

restart: ${DOCKER} ${DOCKERFILE}
	! [ `${DOCKER} ps | grep ${RETHINKDB} | wc -l` -eq 1 ] || \
	make stop && sleep 3 && make start

remove: ${DOCKER} ${DOCKERFILE}
	make stop
	${DOCKER} rmi ${RETHINKDB_RELEASE}

log: ${DOCKER} ${DOCKERFILE}
	! [ `${DOCKER} ps | grep ${RETHINKDB} | wc -l` -eq 1 ] || \
	${COMPOSE} -f ${COMPOSE_FILE} logs --follow --tail 500 ${RETHINKDB}
#==========================================

