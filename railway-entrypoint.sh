#!/bin/bash
# Railway-specific entrypoint script for Tallow & Co. Flask application
# This script is optimized for Railway's environment and DATABASE_URL format

set -e  # Exit on error

echo "==================================="
echo "Tallow & Co. - Railway Deployment"
echo "==================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "DATABASE_URL found: ${DATABASE_URL:0:30}... (truncated for security)"

# Parse DATABASE_URL to extract connection details
# Format: postgresql://user:password@hostname:port/database
# Using Python for reliable URL parsing
DB_HOST=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).hostname)")
DB_PORT=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).port or 5432)")
DB_USER=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).username)")
DB_PASSWORD=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).password)")
DB_NAME=$(python3 -c "from urllib.parse import urlparse; import os; print(urlparse(os.environ['DATABASE_URL']).path.lstrip('/'))")

echo "Parsed database connection:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"

# Wait for PostgreSQL to be ready
echo ""
echo "Waiting for PostgreSQL to be ready..."
timeout=60
counter=0

until PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    counter=$((counter+1))
    if [ $counter -gt $timeout ]; then
        echo "ERROR: PostgreSQL did not become ready in time ($timeout seconds)"
        echo "This usually means:"
        echo "  1. Database service is not running"
        echo "  2. DATABASE_URL is incorrect"
        echo "  3. Network connectivity issue"
        exit 1
    fi
    echo "PostgreSQL is unavailable - waiting... ($counter/$timeout)"
    sleep 1
done

echo "✓ PostgreSQL is ready!"

# Run database migrations
echo ""
echo "Running database migrations..."

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "Migrations directory not found. Initializing Flask-Migrate..."
    if flask db init; then
        echo "✓ Flask-Migrate initialized"
        echo "Creating initial migration..."
        if flask db migrate -m "Initial migration"; then
            echo "✓ Initial migration created"
        else
            echo "WARNING: Failed to create initial migration"
        fi
    else
        echo "WARNING: Failed to initialize Flask-Migrate"
    fi
fi

# Run migrations
if flask db upgrade; then
    echo "✓ Database migrations completed successfully"
else
    echo "WARNING: Database migrations failed"
    echo "This might be okay if it's a fresh database with no migrations"
fi

# Display environment info
echo ""
echo "==================================="
echo "Environment Information:"
echo "  FLASK_ENV: ${FLASK_ENV:-not set}"
echo "  PORT: ${PORT:-8000}"
echo "  Python: $(python3 --version)"
echo "==================================="

echo ""
echo "Starting Gunicorn application server..."
echo "==================================="

# Start the application using gunicorn
# Railway provides the PORT environment variable
PORT=${PORT:-8000}

exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class gevent \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
