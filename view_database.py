#!/usr/bin/env python3
"""
Database Viewer Script for Tallow & Co.

This script allows you to easily view and query your database
without needing to use psql or other database tools.

Usage:
    python view_database.py                 # View all orders
    python view_database.py --orders        # View all orders
    python view_database.py --items         # View all order items
    python view_database.py --stats         # View database statistics
    python view_database.py --order 1       # View specific order details
"""

import sys
from datetime import datetime
from app import create_app
from models import db, Order, OrderItem

def print_separator():
    print("=" * 100)

def print_header(title):
    print_separator()
    print(f" {title}")
    print_separator()

def format_currency(cents):
    """Convert cents to dollar format"""
    return f"${cents / 100:.2f}"

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def view_all_orders():
    """Display all orders in the database"""
    orders = Order.query.order_by(Order.created_at.desc()).all()

    if not orders:
        print("\n📭 No orders found in the database.\n")
        return

    print_header(f"ALL ORDERS ({len(orders)} total)")
    print()

    for order in orders:
        print(f"Order ID: {order.id}")
        print(f"  Customer: {order.customer_name}")
        print(f"  Email: {order.customer_email}")
        print(f"  Phone: {order.customer_phone}")
        print(f"  Total: {format_currency(order.total)}")
        print(f"  Status: {order.status.upper()}")
        print(f"  Created: {format_datetime(order.created_at)}")
        print(f"  Items: {len(order.items)}")
        print()

    print_separator()

def view_order_details(order_id):
    """Display detailed information about a specific order"""
    order = Order.query.get(order_id)

    if not order:
        print(f"\n❌ Order #{order_id} not found.\n")
        return

    print_header(f"ORDER DETAILS - Order #{order.id}")
    print()

    # Customer Information
    print("👤 CUSTOMER INFORMATION")
    print(f"  Name: {order.customer_name}")
    print(f"  Email: {order.customer_email}")
    print(f"  Phone: {order.customer_phone}")
    print()

    # Shipping Address
    print("📦 SHIPPING ADDRESS")
    print(f"  {order.shipping_street}")
    print(f"  {order.shipping_city}, {order.shipping_state} {order.shipping_zip}")
    print()

    # Order Items
    print("🛒 ORDER ITEMS")
    for item in order.items:
        print(f"  • {item.product_name} ({item.product_size})")
        print(f"    Quantity: {item.quantity}")
        print(f"    Price: {format_currency(item.product_price)} each")
        print(f"    Subtotal: {format_currency(item.subtotal)}")
        print()

    # Order Totals
    print("💰 ORDER TOTALS")
    print(f"  Subtotal: {format_currency(order.subtotal)}")
    print(f"  Tax (8%): {format_currency(order.tax)}")
    print(f"  Shipping: {format_currency(order.shipping_cost)}")
    print(f"  TOTAL: {format_currency(order.total)}")
    print()

    # Order Status
    print("📊 ORDER STATUS")
    print(f"  Status: {order.status.upper()}")
    print(f"  Created: {format_datetime(order.created_at)}")
    print(f"  Updated: {format_datetime(order.updated_at)}")
    if order.stripe_payment_id:
        print(f"  Stripe Payment ID: {order.stripe_payment_id}")
    print()

    print_separator()

def view_all_items():
    """Display all order items across all orders"""
    items = OrderItem.query.join(Order).order_by(Order.created_at.desc()).all()

    if not items:
        print("\n📭 No order items found in the database.\n")
        return

    print_header(f"ALL ORDER ITEMS ({len(items)} total)")
    print()

    for item in items:
        print(f"Item ID: {item.id}")
        print(f"  Order: #{item.order_id} - {item.order.customer_name}")
        print(f"  Product: {item.product_name} ({item.product_size})")
        print(f"  Quantity: {item.quantity}")
        print(f"  Price: {format_currency(item.product_price)} each")
        print(f"  Subtotal: {format_currency(item.subtotal)}")
        print()

    print_separator()

def view_statistics():
    """Display database statistics"""
    total_orders = Order.query.count()
    total_items = OrderItem.query.count()

    # Count orders by status
    pending = Order.query.filter_by(status='pending').count()
    paid = Order.query.filter_by(status='paid').count()
    cancelled = Order.query.filter_by(status='cancelled').count()

    # Calculate revenue (only paid orders)
    paid_orders = Order.query.filter_by(status='paid').all()
    total_revenue = sum(order.total for order in paid_orders)

    print_header("DATABASE STATISTICS")
    print()

    print("📊 ORDER SUMMARY")
    print(f"  Total Orders: {total_orders}")
    print(f"  Pending: {pending}")
    print(f"  Paid: {paid}")
    print(f"  Cancelled: {cancelled}")
    print()

    print("🛒 PRODUCT SUMMARY")
    print(f"  Total Items Ordered: {total_items}")
    print()

    print("💰 REVENUE")
    print(f"  Total Revenue (Paid Orders): {format_currency(total_revenue)}")
    if paid > 0:
        avg_order = total_revenue / paid
        print(f"  Average Order Value: {format_currency(int(avg_order))}")
    print()

    # Recent orders
    recent = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    if recent:
        print("🕒 RECENT ORDERS (Last 5)")
        for order in recent:
            print(f"  Order #{order.id} - {order.customer_name} - {format_currency(order.total)} - {order.status}")
        print()

    print_separator()

def print_usage():
    """Print usage information"""
    print()
    print("Database Viewer - Tallow & Co.")
    print()
    print("Usage:")
    print("  python view_database.py              # View all orders")
    print("  python view_database.py --orders     # View all orders")
    print("  python view_database.py --items      # View all order items")
    print("  python view_database.py --stats      # View database statistics")
    print("  python view_database.py --order ID   # View specific order details")
    print("  python view_database.py --help       # Show this help message")
    print()

def main():
    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Parse command line arguments
        if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '--orders'):
            view_all_orders()

        elif len(sys.argv) == 2:
            arg = sys.argv[1]

            if arg == '--help':
                print_usage()
            elif arg == '--items':
                view_all_items()
            elif arg == '--stats':
                view_statistics()
            else:
                print(f"\n❌ Unknown option: {arg}\n")
                print_usage()

        elif len(sys.argv) == 3 and sys.argv[1] == '--order':
            try:
                order_id = int(sys.argv[2])
                view_order_details(order_id)
            except ValueError:
                print(f"\n❌ Invalid order ID: {sys.argv[2]}\n")
                print_usage()

        else:
            print_usage()

if __name__ == '__main__':
    main()
