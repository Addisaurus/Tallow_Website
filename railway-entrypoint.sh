#!/bin/bash
# Improved Railway entrypoint - starts app quickly for health checks
set -e

echo "==================================="
echo "Tallow & Co. - Railway Deployment"
echo "==================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

echo "DATABASE_URL found: ${DATABASE_URL:0:30}..."

# Set port
PORT=${PORT:-8000}

# Function to run migrations in background
run_migrations() {
    echo ""
    echo "Running database migrations in background..."
    
    # Parse DATABASE_URL
    DB_HOST=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).hostname)")
    DB_PORT=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).port or 5432)")
    DB_USER=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).username)")
    DB_PASSWORD=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).password)")
    DB_NAME=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).path.lstrip('/'))")
    
    # Wait for PostgreSQL (with shorter timeout)
    echo "Waiting for PostgreSQL..."
    timeout=30
    counter=0
    until PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
        counter=$((counter+1))
        if [ $counter -gt $timeout ]; then
            echo "WARNING: PostgreSQL not ready after $timeout seconds"
            return 1
        fi
        sleep 1
    done
    
    echo "✓ PostgreSQL ready"
    
    # Run migrations
    if [ -d "migrations" ] || flask db init 2>/dev/null; then
        echo "Running flask db upgrade..."
        timeout 30 flask db upgrade && echo "✓ Migrations complete" || echo "WARNING: Migrations failed"
    fi
}

# Start migrations in background (don't block app startup)
run_migrations &
MIGRATION_PID=$!

echo ""
echo "Starting Gunicorn (migrations running in background)..."
echo "==================================="

# Start Gunicorn immediately - don't wait for migrations
# Note: --preload is NOT used to avoid race condition with background migrations
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class gevent \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app