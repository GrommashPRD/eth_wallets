VENV_DIR = venv
REQUIREMENTS = req.txt

start:
	@docker build -t eth_wallet .
	@docker-compose up -d

stop:
	@docker-compose down

test:
	@docker-compose down
	@docker stop test_postgres || exit 0
	@docker stop test_redis || exit 0
	@docker pull postgres:17
	@docker pull redis:7
	@docker run --rm --name test_postgres \
	    -e POSTGRES_PASSWORD=postgress \
	    -e POSTGRES_USER=postgres \
	    -e POSTGRES_DB=wallets \
	    -d -p 5432:5432 postgres:17
	@docker run --rm --name test_redis -d -p 6379:6379 redis:4-alpine
	@container_name=test_postgres; \
	pattern="ready to accept connections"; \
	while ! docker logs "$$container_name" | grep -q "$$pattern"; do \
	  echo "Waiting for PostgreSQL container to be ready..."; \
	  sleep 0.1; \
	done; \
	echo "PostgreSQL container is ready"
	@container_name=test_redis; \
	pattern="Ready to accept connections"; \
	while ! docker logs "$$container_name" | grep -q "$$pattern"; do \
	  echo "Waiting for Redis container to be ready..."; \
	  sleep 0.1; \
	done; \
	echo "Redis container is ready"
	@python manage.py migrate
	@python -m pytest
	@docker stop test_postgres
	@docker stop test_redis

migrate:
	@docker-compose run web python manage.py migrate

venv:
	@if [ ! -d $(VENV_DIR) ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	fi

install: venv
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

clean:
	@rm -rf $(VENV_DIR)

.PHONY: start stop test migrate makemigrations venv install clean