.PHONY: up down logs init dbshell

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

# Apply schema.sql inside the Postgres container
init:
	cat app/db/schema.sql | docker exec -i asa_postgres psql -U postgres -d asa

# Optional: open a psql shell inside the container
dbshell:
	docker exec -it asa_postgres psql -U postgres -d asa