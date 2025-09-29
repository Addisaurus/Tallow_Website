"""
Database Models for Tallow & Co. E-Commerce

This file defines the database schema using SQLAlchemy ORM:
- Order: Stores customer orders with shipping and payment info
- OrderItem: Stores individual products within each order

These models will be used to:
1. Save customer orders to the database
2. Track order history
3. Generate order confirmations
4. Eventually integrate with Stripe for payment processing
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
# This will be imported and initialized in app.py
db = SQLAlchemy()


class Order(db.Model):
    """
    Order Model - Represents a customer order

    Each order contains:
    - Customer contact information
    - Shipping address
    - Order totals (subtotal, tax, shipping, total)
    - Order status (pending, paid, shipped, delivered, cancelled)
    - Timestamp for when order was placed
    """
    __tablename__ = 'orders'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Customer information
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)

    # Shipping address
    shipping_street = db.Column(db.String(200), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(50), nullable=False)
    shipping_zip = db.Column(db.String(10), nullable=False)

    # Order totals (stored in cents to avoid floating point issues)
    # We'll convert to dollars when displaying
    subtotal = db.Column(db.Integer, nullable=False)  # Product total in cents
    shipping_cost = db.Column(db.Integer, nullable=False)  # Shipping in cents
    tax = db.Column(db.Integer, nullable=False)  # Tax in cents
    total = db.Column(db.Integer, nullable=False)  # Grand total in cents

    # Order status
    # Possible values: 'pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled'
    status = db.Column(db.String(20), nullable=False, default='pending')

    # Stripe payment ID (for future integration)
    stripe_payment_id = db.Column(db.String(100), nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: One order can have many order items
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """String representation of Order for debugging"""
        return f'<Order {self.id} - {self.customer_name} - ${self.total/100:.2f}>'

    def to_dict(self):
        """
        Convert order to dictionary for JSON serialization
        Useful for API endpoints or passing data to templates
        """
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'shipping_address': {
                'street': self.shipping_street,
                'city': self.shipping_city,
                'state': self.shipping_state,
                'zip': self.shipping_zip
            },
            'subtotal': self.subtotal / 100,  # Convert cents to dollars
            'shipping_cost': self.shipping_cost / 100,
            'tax': self.tax / 100,
            'total': self.total / 100,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    """
    OrderItem Model - Represents individual products in an order

    Each order item contains:
    - Reference to the parent order
    - Product details (name, price at time of purchase)
    - Quantity ordered
    - Line item subtotal

    Why store product details instead of just product ID?
    - Prices may change over time
    - Products may be discontinued
    - We need to preserve the exact details of what was ordered
    """
    __tablename__ = 'order_items'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to orders table
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    # Product information (snapshot at time of purchase)
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)  # Price per unit in cents
    product_size = db.Column(db.String(50), nullable=True)  # e.g., "4 oz", "8 oz"

    # Quantity and totals
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Integer, nullable=False)  # quantity * product_price (in cents)

    def __repr__(self):
        """String representation of OrderItem for debugging"""
        return f'<OrderItem {self.id} - {self.product_name} x{self.quantity}>'

    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_price': self.product_price / 100,  # Convert cents to dollars
            'product_size': self.product_size,
            'quantity': self.quantity,
            'subtotal': self.subtotal / 100
        }