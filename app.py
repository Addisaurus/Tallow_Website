"""
Main Flask Application for Tallow Moisturizer E-Commerce Website

This is the entry point for the web application. It:
1. Creates the Flask app instance
2. Loads configuration settings
3. Defines routes (URLs) for each page
4. Handles form submissions
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from config import config
import os


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

    return app


# Create the app instance using development configuration
app = create_app(os.getenv('FLASK_ENV', 'development'))


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
        'current_year': 2024
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