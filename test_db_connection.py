#!/usr/bin/env python3
"""
Database Connection Tester for Tallow & Co.

This script tests your database connection and verifies that everything is set up correctly.

Usage:
    python test_db_connection.py
"""

import os
import sys
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def main():
    print("\n🔍 Database Connection Test - Tallow & Co.")
    print_header("Step 1: Loading Environment Variables")

    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        print("\nPlease ensure you have a .env file with:")
        print("DATABASE_URL=postgresql://tallow_user:tallow_dev_password_2024@localhost:5432/tallow_db")
        sys.exit(1)

    print(f"✅ Found DATABASE_URL: {database_url[:30]}...")

    # Determine database type
    if database_url.startswith('postgresql'):
        db_type = "PostgreSQL"
    elif database_url.startswith('sqlite'):
        db_type = "SQLite"
    else:
        db_type = "Unknown"

    print(f"   Database Type: {db_type}")

    print_header("Step 2: Testing Database Connection")

    try:
        from app import create_app
        from models import db

        app = create_app()

        with app.app_context():
            # Try to connect
            db.engine.connect()
            print("✅ Database connection successful!")

            # Check if tables exist
            print_header("Step 3: Checking Database Tables")

            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   • {table}")
            else:
                print("⚠️  No tables found!")
                print("\nYou may need to run migrations:")
                print("   flask db upgrade")

            # Check if our required tables exist
            required_tables = ['orders', 'order_items']
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                print(f"\n⚠️  Missing required tables: {', '.join(missing_tables)}")
                print("\nRun migrations to create them:")
                print("   flask db upgrade")
            else:
                print("\n✅ All required tables exist!")

            # Count records
            print_header("Step 4: Checking Data")

            from models import Order, OrderItem

            order_count = Order.query.count()
            item_count = OrderItem.query.count()

            print(f"   Orders: {order_count}")
            print(f"   Order Items: {item_count}")

            if order_count == 0:
                print("\n💡 Tip: Your database is empty. Place a test order to see data!")
            else:
                print(f"\n✅ Database contains {order_count} order(s)")

                # Show most recent order
                recent_order = Order.query.order_by(Order.created_at.desc()).first()
                if recent_order:
                    print(f"\n   Most recent order:")
                    print(f"   • Order #{recent_order.id}")
                    print(f"   • Customer: {recent_order.customer_name}")
                    print(f"   • Total: ${recent_order.total / 100:.2f}")
                    print(f"   • Status: {recent_order.status}")

            print_header("✅ All Tests Passed!")

            print("\n🎉 Your database is configured correctly!")
            print("\nNext steps:")
            print("   • Place a test order: http://localhost:5000")
            print("   • View database: python view_database.py")
            print("   • Check stats: python view_database.py --stats")
            print()

    except ImportError as e:
        print(f"❌ ERROR: Failed to import required modules")
        print(f"   {str(e)}")
        print("\nMake sure you've installed all requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"❌ ERROR: Database connection failed")
        print(f"   {str(e)}")
        print("\nTroubleshooting:")

        if db_type == "PostgreSQL":
            print("   1. Check if PostgreSQL is running:")
            print("      sudo service postgresql status")
            print("   2. Verify database exists:")
            print("      psql -U tallow_user -d tallow_db -c 'SELECT 1;'")
            print("   3. Check credentials in .env file")
            print("   4. Run setup script:")
            print("      ./setup_postgres.sh")
        elif db_type == "SQLite":
            print("   1. Check if database file exists:")
            print("      ls -la instance/tallow.db")
            print("   2. Run migrations:")
            print("      flask db upgrade")

        print("\nFor more help, see POSTGRESQL_MIGRATION_GUIDE.md")
        sys.exit(1)

if __name__ == '__main__':
    main()
