# Variables
PYTHON=python3
PIP=pip
UVICORN=uvicorn
APP=backend.app.main:app
PORT=8000
DOCKER_COMPOSE=docker-compose

install:
	$(PIP) install -r backend/requirements.txt

run:
	$(UVICORN) $(APP) --reload --port $(PORT)

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f

check-version:
	@python3 --version | grep "3.10" || (echo "❌ Python 3.10 required" && exit 1)
