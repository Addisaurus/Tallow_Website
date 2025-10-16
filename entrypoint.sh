#!/bin/bash
# Entrypoint script for Tallow & Co. Flask application
# This script runs before starting the application server

set -e  # Exit on error

echo "==================================="
echo "Tallow & Co. Application Starting"
echo "==================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
timeout=30
counter=0

# Extract database name from DATABASE_URL or use default
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_NAME=${DB_NAME:-tallow_db}

until PGPASSWORD="${POSTGRES_PASSWORD:-changeme}" pg_isready -h db -p 5432 -U "${POSTGRES_USER:-tallow_user}" -d "${DB_NAME}" > /dev/null 2>&1; do
    counter=$((counter+1))
    if [ $counter -gt $timeout ]; then
        echo "ERROR: PostgreSQL did not become ready in time"
        echo "Connection details: host=db, port=5432, user=${POSTGRES_USER:-tallow_user}, database=${DB_NAME}"
        exit 1
    fi
    echo "PostgreSQL is unavailable - waiting... ($counter/$timeout)"
    sleep 1
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
if flask db upgrade; then
    echo "Database migrations completed successfully"
else
    echo "WARNING: Database migrations failed or not configured"
    echo "If this is your first deployment, run: flask db init && flask db migrate"
fi

# Optional: Create initial data (uncomment if you have a script)
# echo "Creating initial data..."
# python scripts/init_data.py

echo "==================================="
echo "Starting application server..."
echo "==================================="

# Execute the CMD from Dockerfile (passed as arguments to this script)
exec "$@"
