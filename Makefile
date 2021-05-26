.PHONY: help run start stop restart log remove

#==========================================
VENV_NAME?=venv
ENV=.env
VENV_ACTIVATE=. ${VENV_NAME}/bin/activate
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip3
PYCODESTYLE=${VENV_NAME}/bin/pycodestyle
PYFLAKES=${VENV_NAME}/bin/pyflakes
PWD=$(shell pwd)
DOCKER=$(shell which docker)
COMPOSE=$(shell which docker-compose)
COMPOSE_FILE=docker-compose.yml
DEPENDENCES=requirements.txt
DEPENDENCESDEV=requirements-dev.txt
RETHINKDBSRV=rethinkdbsrv.py
RETHINKDBASYNC=rethinkdbasync.py
include ${ENV}

#==========================================
.DEFAULT: help

help:
	@echo "make install	- Installing dependencies and applications"
	@echo "make install-dev - Installing dependencies for code validation"
	@echo "make uninstall	- Deleting an applications"
	@echo "make run	- Run the applications"
	@echo "make check	- Checking the code"
	@echo "make clean	- Cleaning up garbage"
	@echo "make start	- Start RethinkDB in Docker"
	@echo "make stop	- Stopping RethinkDB in Docker"
	@echo "make log	- Output of logs for RethinkDB in Docker"
	@echo "make remove	- Deleting a RethinkDB in Docker"

#=============================================
# Установка зависимостей
install:
	[ -d $(VENV_NAME) ] || python3 -m $(VENV_NAME) $(VENV_NAME)
	${PIP} install pip wheel -U
	${PIP} install -r ${DEPENDENCES}

# Установка зависимостей для проверки кода
install-dev:
	[ -d $(VENV_NAME) ] || python3 -m $(VENV_NAME) $(VENV_NAME)
	${PIP} install pip wheel -U
	${PIP} install -r ${DEPENDENCESDEV}

# Активация виртуального окружения
venv: ${VENV_NAME}/bin/activate
$(VENV_NAME)/bin/activate: ${SETUP}
	[ -d $(VENV_NAME) ] || python3 -m $(VENV_NAME) $(VENV_NAME)
	${PIP} install -U pip
	${PIP} install -e .
	${VENV_ACTIVATE}

# Очистка мусора
clean:
	rm -fr build
	rm -fr .eggs
	rm -fr *.egg-info
	rm -fr *.log 
	rm -fr *.log.zip
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# Удаление виртуального окружения
uninstall: ${VENV_NAME}
	make clean
	rm -fr ${VENV_NAME}

# Запуск приложения
run: ${VENV_NAME}
	${PYTHON} ${RETHINKDBSRV}

#===============================================
# Проверка кода
check: ${PYCODESTYLE} ${PYFLAKES} ${RETHINKDBSRV} ${RETHINKDBASYNC}
	@echo "==================================="
	${PYCODESTYLE} ${RETHINKDBSRV} ${RETHINKDBASYNC}
	${PYFLAKES} ${RETHINKDBSRV} ${RETHINKDBASYNC}
	@echo "=============== OK! ==============="

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
