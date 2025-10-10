.PHONY: run dev install migrate upgrade help

# Default target
help:
	@echo "Available commands:"
	@echo "  make run      - Run the server with configured settings"
	@echo "  make dev      - Run the server (alias for run)"
	@echo "  make install  - Install dependencies"
	@echo "  make migrate  - Generate a new migration"
	@echo "  make upgrade  - Apply pending migrations"

# Run the server
run:
	python run.py

# Alias for run
dev: run

# Install dependencies
install:
	pip install -r requirements.txt

# Generate migration
migrate:
	alembic revision --autogenerate -m "$(msg)"

# Apply migrations
upgrade:
	alembic upgrade head

