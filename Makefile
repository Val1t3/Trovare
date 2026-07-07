.PHONY: start stop build logs restart

# Build and start the containers in the background.
start:
	docker compose up --build -d

# Stop and remove the containers.
stop:
	docker compose down

# Build the image without starting.
build:
	docker compose build

# Follow the container logs.
logs:
	docker compose logs -f

# Restart the containers.
restart: stop start
