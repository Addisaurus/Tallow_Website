"""
Flask-WTF Forms for Tallow & Co. Website

This file defines web forms using Flask-WTF (Flask-WTForms):
- CheckoutForm: Collects customer and shipping information during checkout

Flask-WTF provides:
1. Automatic CSRF protection (prevents cross-site request forgery attacks)
2. Built-in validation (required fields, email format, etc.)
3. Easy rendering in templates
4. Error message handling
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TelField
from wtforms.validators import DataRequired, Email, Length, Regexp


class CheckoutForm(FlaskForm):
    """
    Checkout Form - Collects customer information and shipping address

    This form is used on the checkout page to gather all necessary
    information to process and ship an order.

    Validators ensure data quality:
    - DataRequired: Field cannot be empty
    - Email: Must be valid email format
    - Length: Enforces min/max character limits
    - Regexp: Pattern matching (e.g., zip codes, phone numbers)
    """

    # Customer Information
    customer_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Please enter your full name'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ],
        render_kw={'placeholder': 'John Smith'}
    )

    customer_email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email address'),
            Email(message='Please enter a valid email address'),
            Length(max=120)
        ],
        render_kw={'placeholder': 'john.smith@example.com'}
    )

    customer_phone = TelField(
        'Phone Number',
        validators=[
            DataRequired(message='Please enter your phone number'),
            Regexp(
                r'^\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
                message='Please enter a valid 10-digit US phone number (e.g., 555-123-4567)'
            )
        ],
        render_kw={'placeholder': '555-123-4567'}
    )

    # Shipping Address
    shipping_street = TextAreaField(
        'Street Address',
        validators=[
            DataRequired(message='Please enter your street address'),
            Length(min=5, max=200, message='Address must be between 5 and 200 characters')
        ],
        render_kw={'placeholder': '123 Main St, Apt 4B', 'rows': 2}
    )

    shipping_city = StringField(
        'City',
        validators=[
            DataRequired(message='Please enter your city'),
            Length(min=2, max=100, message='City must be between 2 and 100 characters')
        ],
        render_kw={'placeholder': 'Los Angeles'}
    )

    shipping_state = StringField(
        'State',
        validators=[
            DataRequired(message='Please enter your state'),
            Length(min=2, max=50, message='State must be between 2 and 50 characters')
        ],
        render_kw={'placeholder': 'CA or California'}
    )

    shipping_zip = StringField(
        'ZIP Code',
        validators=[
            DataRequired(message='Please enter your ZIP code'),
            Regexp(
                r'^\d{5}(-\d{4})?$',
                message='Please enter a valid ZIP code (e.g., 90210 or 90210-1234)'
            )
        ],
        render_kw={'placeholder': '90210'}
    )

    def validate(self, **kwargs):
        """
        Custom validation method (runs after individual field validators)

        You can add additional cross-field validation here if needed.
        For example:
        - Check if shipping address is within serviceable area
        - Validate that email and phone aren't already in fraud database
        - Ensure city/state/zip combination is valid
        """
        # Run the default validators first
        if not super().validate(**kwargs):
            return False

        # Add any custom validation logic here
        # For now, we'll just return True

        return True