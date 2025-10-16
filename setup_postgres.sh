#!/bin/bash
# PostgreSQL Database Setup Script for Tallow & Co.
# This script creates the database and user for the application

echo "=========================================="
echo "PostgreSQL Setup for Tallow & Co."
echo "=========================================="
echo ""

# Database configuration
DB_NAME="tallow_db"
DB_USER="tallow_user"
DB_PASSWORD="tallow_dev_password_2024"

echo "Creating PostgreSQL database and user..."
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""

# Switch to postgres user and create database and user
sudo -u postgres psql << EOF
-- Create the database
CREATE DATABASE $DB_NAME;

-- Create the user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to the database and grant schema permissions
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;

-- Exit
\q
EOF

echo ""
echo "=========================================="
echo "Database setup complete!"
echo "=========================================="
echo ""
echo "Connection details:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Host: localhost"
echo "  Port: 5432"
echo ""
echo "Connection string for .env:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the connection string above"
echo "2. Install psycopg2: pip install psycopg2-binary"
echo "3. Run migrations: flask db upgrade"
echo ""
