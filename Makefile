POETRY_PYTHON_PATH = $(shell poetry env info --path) # wow copilot ur amazing
POETRY_PYTHON_PATH := $(subst  ,,$(POETRY_PYTHON_PATH)) # remove spaces
ifeq ($(OS),Windows_NT)
	# Windows
	PYTHON = $(addsuffix \Scripts\python.exe,$(POETRY_PYTHON_PATH))
else
	# Linux
	PYTHON = $(addsuffix /bin/python,$(POETRY_PYTHON_PATH))
endif

run:
	$(PYTHON) bot.py
install:
	poetry install
update:
	poetry update
beauty: # this is mostly used in CI so just use global python
	python -m isort .
	python -m black .
	python -m flake8 .  --exit-zero
	python -m autoflake --remove-all-unused-imports --remove-unused-variables --in-place -r .
install-beautifier:
	pip install isort black flake8 autoflake
build_image:
	docker build . --tag countable_dev:latest --build-arg="REVISION=$(shell git rev-parse --short main)"
compose_run:
	COUNTABLE_REVISION=$(shell git rev-parse --short main) docker compose up
compose_build:
	COUNTABLE_REVISION=$(shell git rev-parse --short main) docker compose build --no-cache
publish_image:
	docker build . --build-arg="REVISION=$(shell git rev-parse --short main)" --tag ghcr.io/timelessnesses/countable:latest --tag ghcr.io/timelessnesses/countable:$(shell git rev-parse --short main) --tag ghcr.io/timelessnesses/countable:main
	docker push ghcr.io/timelessnesses/countable:latest
	docker push ghcr.io/timelessnesses/countable:main
	docker push ghcr.io/timelessnesses/countable:$(shell git rev-parse --short main)
publish_no_builds:
	docker push ghcr.io/timelessnesses/countable:latest
	docker push ghcr.io/timelessnesses/countable:main
	docker push ghcr.io/timelessnesses/countable:$(shell git rev-parse --short main)
