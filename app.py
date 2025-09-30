"""
Main Flask Application for Tallow Moisturizer E-Commerce Website

This is the entry point for the web application. It:
1. Creates the Flask app instance
2. Loads configuration settings
3. Defines routes (URLs) for each page
4. Handles form submissions
"""

from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, Order, OrderItem
from forms import CheckoutForm
from flask_migrate import Migrate
import os
import stripe
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_app(config_name='development'):
    """
    Application Factory Pattern

    This function creates and configures the Flask application.
    Using a factory function makes it easier to create multiple instances
    (e.g., for testing) and keeps the code organized.

    Args:
        config_name: The configuration to use ('development', 'production', or 'testing')

    Returns:
        Configured Flask application instance
    """
    # Create Flask app instance
    # __name__ tells Flask where to find templates and static files
    app = Flask(__name__)

    # Load configuration from config.py based on environment
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate for database migrations
    migrate = Migrate(app, db)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Initialize Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    # Exempt webhook route from CSRF protection (Stripe webhooks can't include CSRF tokens)
    csrf.exempt('stripe_webhook')

    return app


# Create the app instance using development configuration
app = create_app(os.getenv('FLASK_ENV', 'development'))


# HELPER FUNCTIONS: Reusable functions for cart and order management

def get_cart():
    """
    Get cart from session storage

    The cart is stored as a list of dictionaries in the session:
    [
        {
            'name': 'Product Name',
            'price': 24.99,
            'size': '4 oz',
            'quantity': 2
        },
        ...
    ]

    Returns empty list if cart doesn't exist
    """
    return session.get('cart', [])


def get_cart_item_count():
    """
    Get total number of items in cart

    Returns the sum of all quantities across all items
    """
    cart = get_cart()
    return sum(item['quantity'] for item in cart)


def calculate_cart_totals(cart):
    """
    Calculate cart totals (subtotal, tax, shipping, total)

    Args:
        cart: List of cart items

    Returns:
        Dictionary with totals in cents (for database storage):
        {
            'subtotal': int,      # Sum of all items
            'tax': int,           # 8% of subtotal
            'shipping': int,      # Flat rate $5.00
            'total': int          # subtotal + tax + shipping
        }
    """
    # Calculate subtotal (convert to cents)
    subtotal_cents = sum(
        int(item['price'] * 100) * item['quantity']
        for item in cart
    )

    # Calculate tax (8% of subtotal)
    tax_cents = int(subtotal_cents * 0.08)

    # Flat rate shipping ($5.00 = 500 cents)
    # Free shipping over $50
    shipping_cents = 500 if subtotal_cents < 5000 else 0

    # Calculate total
    total_cents = subtotal_cents + tax_cents + shipping_cents

    return {
        'subtotal': subtotal_cents,
        'tax': tax_cents,
        'shipping': shipping_cents,
        'total': total_cents
    }


# ROUTES: These functions handle requests to different URLs
# The @app.route decorator tells Flask which URL should trigger each function

@app.route('/')
def index():
    """
    Homepage route

    When someone visits the root URL ('/'), Flask will:
    1. Call this function
    2. Render the index.html template
    3. Return the HTML to the browser
    """
    return render_template('index.html')


@app.route('/about')
def about():
    """
    About page route

    Displays information about the product origin and benefits
    """
    return render_template('about.html')


@app.route('/product')
def product():
    """
    Product detail page route

    Shows detailed product information, ingredients, and usage instructions.
    In the future, this could accept a product ID parameter to show different products.
    """
    # Product data (in the future, this will come from a database)
    product_data = {
        'name': 'Pure Beef Tallow Moisturizer',
        'price': 24.99,
        'size': '4 oz',
        'description': 'Our handcrafted beef tallow moisturizer is made from 100% grass-fed beef tallow, whipped to perfection for a luxurious, deeply nourishing skincare experience.',
        'ingredients': [
            '100% Grass-Fed Beef Tallow',
            'Organic Jojoba Oil',
            'Vitamin E Oil',
            'Essential Oils (Lavender & Chamomile)'
        ],
        'benefits': [
            'Deep hydration without greasy residue',
            'Rich in vitamins A, D, E, and K',
            'Compatible with skin\'s natural oils',
            'Anti-inflammatory properties',
            'Suitable for sensitive skin'
        ]
    }

    return render_template('product.html', product=product_data)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact page route

    Handles both:
    - GET requests: Display the contact form
    - POST requests: Process form submission

    The form doesn't send emails yet, but the structure is ready for that functionality.
    """
    if request.method == 'POST':
        # Get form data submitted by the user
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # For now, just show a success message
        # Later, you can add email sending functionality here
        flash(f'Thank you for your message, {name}! We\'ll get back to you soon.', 'success')

        # Redirect back to contact page (prevents form resubmission on refresh)
        return redirect(url_for('contact'))

    # If it's a GET request, just show the form
    return render_template('contact.html')


# SHOPPING CART ROUTES

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """
    Add product to shopping cart

    Receives product data via POST request and stores in session.
    If product already exists in cart, increases quantity.

    Expected POST data:
    - product_name: str
    - product_price: float
    - product_size: str
    - quantity: int
    """
    try:
        # Get cart from session (or create empty cart)
        cart = get_cart()

        # Get product data from form
        product_name = request.form.get('product_name')
        product_price = float(request.form.get('product_price'))
        product_size = request.form.get('product_size')
        quantity = int(request.form.get('quantity', 1))

        # Validate quantity
        if quantity < 1 or quantity > 10:
            flash('Quantity must be between 1 and 10', 'error')
            return redirect(url_for('product'))

        # Check if product already in cart
        product_found = False
        for item in cart:
            if item['name'] == product_name:
                # Update quantity (max 10 per product)
                item['quantity'] = min(item['quantity'] + quantity, 10)
                product_found = True
                break

        # If product not in cart, add it
        if not product_found:
            cart.append({
                'name': product_name,
                'price': product_price,
                'size': product_size,
                'quantity': quantity
            })

        # Save cart back to session
        session['cart'] = cart
        session.modified = True

        flash(f'Added {quantity} x {product_name} to your cart!', 'success')
        return redirect(url_for('product'))

    except (ValueError, TypeError) as e:
        flash('Error adding product to cart. Please try again.', 'error')
        return redirect(url_for('product'))


@app.route('/cart')
def cart():
    """
    Shopping cart page

    Displays all items in cart with:
    - Product details
    - Quantity controls
    - Remove option
    - Subtotal, tax, shipping, total
    """
    cart = get_cart()

    # Calculate totals
    if cart:
        totals = calculate_cart_totals(cart)
        # Convert cents to dollars for display
        totals_display = {
            'subtotal': totals['subtotal'] / 100,
            'tax': totals['tax'] / 100,
            'shipping': totals['shipping'] / 100,
            'total': totals['total'] / 100
        }
    else:
        totals_display = {
            'subtotal': 0,
            'tax': 0,
            'shipping': 0,
            'total': 0
        }

    return render_template('cart.html', cart=cart, totals=totals_display)


@app.route('/update-cart', methods=['POST'])
def update_cart():
    """
    Update quantity of item in cart

    Expected POST data:
    - product_name: str (identifies which item to update)
    - quantity: int (new quantity)
    """
    try:
        cart = get_cart()
        product_name = request.form.get('product_name')
        quantity = int(request.form.get('quantity'))

        # Validate quantity
        if quantity < 1 or quantity > 10:
            flash('Quantity must be between 1 and 10', 'error')
            return redirect(url_for('cart'))

        # Find and update item
        for item in cart:
            if item['name'] == product_name:
                item['quantity'] = quantity
                break

        # Save cart
        session['cart'] = cart
        session.modified = True

        flash('Cart updated successfully', 'success')
        return redirect(url_for('cart'))

    except (ValueError, TypeError):
        flash('Error updating cart. Please try again.', 'error')
        return redirect(url_for('cart'))


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """
    Remove item from cart

    Expected POST data:
    - product_name: str (identifies which item to remove)
    """
    cart = get_cart()
    product_name = request.form.get('product_name')

    # Filter out the item to remove
    cart = [item for item in cart if item['name'] != product_name]

    # Save cart
    session['cart'] = cart
    session.modified = True

    flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """
    Checkout page

    GET: Display checkout form with order summary
    POST: Process order, create Stripe Checkout Session, and redirect to Stripe

    Validates:
    - Cart is not empty
    - Form data is valid
    - Database save successful
    - Stripe session created successfully
    """
    # Check if cart is empty
    cart = get_cart()
    if not cart:
        flash('Your cart is empty. Please add items before checking out.', 'error')
        return redirect(url_for('product'))

    # Calculate totals
    totals = calculate_cart_totals(cart)
    totals_display = {
        'subtotal': totals['subtotal'] / 100,
        'tax': totals['tax'] / 100,
        'shipping': totals['shipping'] / 100,
        'total': totals['total'] / 100
    }

    # Create checkout form
    form = CheckoutForm()

    if form.validate_on_submit():
        try:
            # Create new order with pending status
            order = Order(
                customer_name=form.customer_name.data,
                customer_email=form.customer_email.data,
                customer_phone=form.customer_phone.data,
                shipping_street=form.shipping_street.data,
                shipping_city=form.shipping_city.data,
                shipping_state=form.shipping_state.data,
                shipping_zip=form.shipping_zip.data,
                subtotal=totals['subtotal'],
                tax=totals['tax'],
                shipping_cost=totals['shipping'],
                total=totals['total'],
                status='pending'
            )

            # Add order items
            for item in cart:
                order_item = OrderItem(
                    product_name=item['name'],
                    product_price=int(item['price'] * 100),  # Convert to cents
                    product_size=item['size'],
                    quantity=item['quantity'],
                    subtotal=int(item['price'] * 100) * item['quantity']
                )
                order.items.append(order_item)

            # Save to database
            db.session.add(order)
            db.session.commit()

            # Create Stripe Checkout Session
            # Build line items for Stripe
            line_items = []
            for item in cart:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item['name'],
                            'description': f"Size: {item['size']}"
                        },
                        'unit_amount': int(item['price'] * 100),  # Price in cents
                    },
                    'quantity': item['quantity'],
                })

            # Add tax as a line item
            if totals['tax'] > 0:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Tax (8%)',
                        },
                        'unit_amount': totals['tax'],
                    },
                    'quantity': 1,
                })

            # Add shipping as a line item
            if totals['shipping'] > 0:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Shipping',
                        },
                        'unit_amount': totals['shipping'],
                    },
                    'quantity': 1,
                })

            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=url_for('success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('cancel', _external=True) + f'?order_id={order.id}',
                customer_email=form.customer_email.data,
                metadata={
                    'order_id': order.id
                },
                shipping_address_collection={
                    'allowed_countries': ['US'],
                }
            )

            # Clear cart after creating checkout session
            session['cart'] = []
            session.modified = True

            # Redirect to Stripe Checkout
            return redirect(checkout_session.url, code=303)

        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            db.session.rollback()
            flash('Payment system error. Please try again.', 'error')
            print(f"Stripe error: {e}")

        except Exception as e:
            # Handle general errors
            db.session.rollback()
            flash('Error processing order. Please try again.', 'error')
            print(f"Order error: {e}")

    return render_template('checkout.html', form=form, cart=cart, totals=totals_display)


@app.route('/success')
def success():
    """
    Payment success route

    Called by Stripe after successful payment.
    Retrieves the session, verifies payment, updates order status.
    """
    # Get session_id from query parameters
    session_id = request.args.get('session_id')

    if not session_id:
        flash('Invalid payment session.', 'error')
        return redirect(url_for('product'))

    try:
        # Retrieve the Stripe Checkout Session
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Verify payment was successful
        if checkout_session.payment_status != 'paid':
            flash('Payment was not completed. Please try again.', 'error')
            return redirect(url_for('product'))

        # Get order ID from session metadata
        order_id = checkout_session.metadata.get('order_id')

        if not order_id:
            flash('Order not found.', 'error')
            return redirect(url_for('product'))

        # Get order from database
        order = Order.query.get_or_404(order_id)

        # Verify order total matches payment amount (security check)
        if order.total != checkout_session.amount_total:
            # Log this discrepancy
            print(f"WARNING: Order total mismatch. Order {order_id}: DB={order.total}, Stripe={checkout_session.amount_total}")
            flash('Payment amount mismatch. Please contact support.', 'error')
            return redirect(url_for('product'))

        # Update order status to paid
        order.status = 'paid'
        order.stripe_payment_id = checkout_session.payment_intent
        db.session.commit()

        # Show success message
        flash('Payment successful! Your order is confirmed.', 'success')
        return redirect(url_for('confirmation', order_id=order.id))

    except stripe.error.StripeError as e:
        flash('Error verifying payment. Please contact support.', 'error')
        print(f"Stripe error in success route: {e}")
        return redirect(url_for('product'))

    except Exception as e:
        flash('An error occurred. Please contact support.', 'error')
        print(f"Error in success route: {e}")
        return redirect(url_for('product'))


@app.route('/cancel')
def cancel():
    """
    Payment cancellation route

    Called when user cancels payment on Stripe checkout page.
    Marks order as cancelled and provides option to retry.
    """
    order_id = request.args.get('order_id')

    if order_id:
        try:
            order = Order.query.get(order_id)
            if order and order.status == 'pending':
                # Mark order as cancelled
                order.status = 'cancelled'
                db.session.commit()
        except Exception as e:
            print(f"Error updating cancelled order: {e}")

    flash('Payment was cancelled. Your order has been saved if you\'d like to try again.', 'info')
    return render_template('cancel.html', order_id=order_id)


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook endpoint

    Listens for Stripe events (checkout.session.completed, payment_intent.succeeded, etc.)
    Updates order status based on payment events.

    Note: Webhook signature verification is optional if STRIPE_WEBHOOK_SECRET is not set.
    This allows for easier development/testing without webhook setup.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

    try:
        # If webhook secret is configured, verify the signature
        if webhook_secret:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print(f"Webhook signature verification failed: {e}")
                return jsonify({'error': 'Invalid signature'}), 400
        else:
            # No webhook secret configured - parse event without verification
            # ONLY for development/testing
            event = stripe.Event.construct_from(
                request.get_json(), stripe.api_key
            )
            print("WARNING: Processing webhook without signature verification (development mode)")

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Get order ID from metadata
            order_id = session.get('metadata', {}).get('order_id')

            if order_id:
                try:
                    order = Order.query.get(order_id)

                    if order:
                        # Update order status to paid
                        order.status = 'paid'
                        order.stripe_payment_id = session.get('payment_intent')
                        db.session.commit()

                        print(f"Order {order_id} marked as paid via webhook")
                    else:
                        print(f"Order {order_id} not found in database")

                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating order from webhook: {e}")

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Payment intent succeeded: {payment_intent['id']}")

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            print(f"Payment intent failed: {payment_intent['id']}")

        else:
            print(f"Unhandled webhook event type: {event['type']}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    """
    Order confirmation page

    Displays order details after successful checkout

    Args:
        order_id: ID of the order to display
    """
    # Get order from database
    order = Order.query.get_or_404(order_id)

    return render_template('confirmation.html', order=order)


# ERROR HANDLERS: These handle common HTTP errors gracefully

@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors (page not found)

    Instead of showing an ugly error, show a friendly custom page
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 errors (server errors)

    Shows a friendly error page when something goes wrong on the server
    """
    return render_template('500.html'), 500


# CONTEXT PROCESSORS: Make variables available to all templates

@app.context_processor
def inject_site_info():
    """
    Inject site-wide information into all templates

    This makes these variables available in every template without
    having to pass them explicitly from each route.
    """
    return {
        'site_name': 'Tallow & Co.',
        'current_year': 2024,
        'cart_count': get_cart_item_count()  # Make cart count available in all templates
    }


# MAIN EXECUTION: Run the development server

if __name__ == '__main__':
    """
    This block only runs when you execute this file directly (python app.py)
    It starts Flask's built-in development server.

    NOTE: For production, you should use a proper WSGI server like Gunicorn,
    not the built-in development server.
    """
    app.run(
        debug=True,  # Enable debug mode for development
        host='127.0.0.1',  # Only accessible from this computer
        port=5000  # Run on port 5000
    )