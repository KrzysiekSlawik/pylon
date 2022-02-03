SHELL := /bin/bash

.PHONY: setup start-server

setup:
	python3 -m venv env
	source env/bin/activate && pip3 install -r requirements.txt
	@echo run "source env/bin/activate"

init-db:
ifneq ("$(wildcard env)","")
	source env/bin/activate && python3 src/server/database/create_schema.py
else
	@echo "env doesn't exist - run setup first!"
endif

start-server:
ifneq ("$(wildcard env)","")
	source env/bin/activate && hypercorn src/server_main:app --reload
else
	@echo "env doesn't exist - run setup first!"
endif

start-bot:
ifneq ("$(wildcard env)","")
	source env/bin/activate && python3 src/bot_client.py
else
	@echo "env doesn't exist - run setup first!"
endif

run-tests:
ifneq ("$(wildcard env)","")
	source env/bin/activate && python3 -m unittest discover --start-directory test -p test*.py
else
	@echo "env doesn't exist - run setup first!"
endif

flake:
	source env/bin/activate && python3 -m flake8 --config=.flake8


