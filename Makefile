start:
	@docker build -t eth_wallet .
	@docker-compose up

stop:
	@docker-compose down

test:
	@docker-compose down
	@docker stop test_postgres || exit 0
	@docker pull postgres:17
	@docker run --rm --name test_postgres \
	    -e POSTGRES_PASSWORD=postgress \
	    -e POSTGRES_USER=postgres \
	    -e POSTGRES_DB=wallets \
	    -d -p 5432:5432 postgres:17

	@docker run --rm --name test_redis -d -p 6379:6379 redis:latest
	@container_name=test_postgres; \
    pattern="ready to accept connections"; \
    while ! docker logs "$$container_name" | grep -q "$$pattern"; do \
      echo "Waiting for the container to be ready..."; \
      sleep 0.1; \
    done; \
    echo "Postgres container is ready"
	@container_name=test_redis; \
	pattern="Ready to accept connections"; \
	while ! docker logs "$$container_name" | grep -q "$$pattern"; do \
	echo "Waiting for the Redis container to be ready..."; \
	sleep 0.1; \
	done; \
	echo "Redis container is ready"

	@python manage.py migrate
	@pytest
	@docker stop test_postgres
	@docker stop test_redis

migrate:
	@docker-compose run web python manage.py migrate

.PHONY: start stop test migrate makemigrations