"""
Flask Configuration Settings

This file contains configuration classes for different environments:
- DevelopmentConfig: Used during local development
- ProductionConfig: Used when deployed to a live server
- TestingConfig: Used for running automated tests

You can switch between configs by setting the FLASK_ENV environment variable
"""

import os


class Config:
    """
    Base configuration class with settings shared across all environments
    """
    # Secret key used for session encryption and CSRF protection
    # IMPORTANT: Change this to a random string in production!
    # You can generate one in Python with: import secrets; secrets.token_hex(16)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # SQLAlchemy settings (for future database integration)
    # This prevents SQLAlchemy from tracking modifications (saves resources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database URI (will be configured when you add database support)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tallow.db'

    # Email settings (for future contact form functionality)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Stripe API keys (for future payment integration)
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')


class DevelopmentConfig(Config):
    """
    Configuration for local development
    - Debug mode enabled (auto-reloads on code changes, shows detailed errors)
    - Uses local SQLite database
    """
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """
    Configuration for production deployment
    - Debug mode disabled for security
    - Should use environment variables for sensitive data
    """
    DEBUG = False
    TESTING = False

    # In production, make sure SECRET_KEY is set via environment variable
    # Uncomment this to enforce it:
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # if not SECRET_KEY:
    #     raise ValueError("No SECRET_KEY set for Flask application in production!")


class TestingConfig(Config):
    """
    Configuration for running automated tests
    """
    TESTING = True
    DEBUG = True
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable CSRF in testing for easier form testing
    WTF_CSRF_ENABLED = False


# Dictionary to easily select config based on environment name
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}