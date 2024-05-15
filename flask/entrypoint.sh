#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres_db 5432; do
  sleep 1
done

echo "PostgreSQL is ready!"

# Run the Flask application
exec "$@"
