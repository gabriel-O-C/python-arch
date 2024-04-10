# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	awk '/\[tool\.poetry\.dependencies\]/,/\[build-system\]/ {if (!/\[tool\.poetry\.dependencies\]/ && !/\[build-system\]/ && !/python/) {gsub(/=.*/, "", $$0); print}}' pyproject.toml > requirements.txt
	docker-compose build

up:
	docker-compose up -d app

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d app

logs:
	docker-compose logs app | tail -100

test:
	pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')