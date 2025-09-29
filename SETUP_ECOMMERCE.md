# E-Commerce Setup Instructions

This guide will help you set up and test the shopping cart and checkout functionality for your Tallow & Co. website.

## Prerequisites

- Python 3.10+ installed
- Virtual environment activated (`venv`)
- Basic understanding of Flask and SQLite

## Step 1: Install New Dependencies

The shopping cart requires database support. Install the new dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- **Flask-SQLAlchemy** (3.1.1) - Database ORM for managing orders
- **Flask-Migrate** (4.0.5) - Database migration tool

## Step 2: Initialize the Database

The application uses SQLite (a file-based database) for development. You need to:

1. **Initialize the migration repository** (one-time setup):
   ```bash
   flask db init
   ```

2. **Create the initial migration** (this generates the SQL to create tables):
   ```bash
   flask db migrate -m "Initial database with Order and OrderItem models"
   ```

3. **Apply the migration** (this actually creates the tables):
   ```bash
   flask db upgrade
   ```

After these steps, you should see a `tallow.db` file in your project root. This is your SQLite database.

## Step 3: Start the Development Server

Start the Flask development server:

```bash
python app.py
```

Or use Flask's built-in command:

```bash
flask run
```

The application should be running at: http://127.0.0.1:5000

## Step 4: Test the Complete Flow

### 4.1 Add Items to Cart

1. Navigate to the **Product** page: http://127.0.0.1:5000/product
2. Use the quantity controls (+ / -) to select a quantity (1-10)
3. Click **"Add to Cart"**
4. You should see a success flash message
5. Notice the cart icon in the navigation now shows the item count

### 4.2 View Cart

1. Click the shopping cart icon in the navigation
2. You should see your item(s) listed with:
   - Product image, name, size
   - Price per unit
   - Quantity controls
   - Remove button
   - Subtotal for each item
3. Try the quantity controls:
   - Click **+** or **-** to adjust quantity
   - Click **"Update"** to save changes
4. Try removing an item:
   - Click **"Remove"**
   - Confirm the removal
5. Check the order summary sidebar:
   - Subtotal (sum of all items)
   - Tax (8% of subtotal)
   - Shipping ($5.00 flat rate, FREE over $50)
   - Total

### 4.3 Proceed to Checkout

1. Click **"Proceed to Checkout"** from the cart page
2. Fill out the checkout form:
   - **Customer Information:**
     - Full Name (required, 2-100 characters)
     - Email Address (required, valid email format)
     - Phone Number (required, 10-digit US format: 555-123-4567)
   - **Shipping Address:**
     - Street Address (required, 5-200 characters)
     - City (required, 2-100 characters)
     - State (required, 2-50 characters)
     - ZIP Code (required, 5-digit or 9-digit format)
3. Review the order summary sidebar (sticky, stays visible when scrolling)
4. Click **"Place Order"**

### 4.4 Order Confirmation

1. After successful checkout, you'll be redirected to the confirmation page
2. You should see:
   - Success message with order number
   - Customer information (name, email, phone)
   - Shipping address
   - Order items with quantities and prices
   - Order totals (subtotal, tax, shipping, total)
   - Order status (pending)
   - What happens next (order processing steps)
3. A yellow notice explains that payment integration is coming soon

### 4.5 Verify Database

You can verify that the order was saved to the database:

**Option A: Using Python Shell**
```bash
python
>>> from app import app, db
>>> from models import Order
>>> with app.app_context():
...     orders = Order.query.all()
...     for order in orders:
...         print(f"Order #{order.id}: {order.customer_name} - ${order.total/100:.2f}")
...         for item in order.items:
...             print(f"  - {item.product_name} x{item.quantity}")
```

**Option B: Using DB Browser for SQLite** (free tool)
1. Download from: https://sqlitebrowser.org/
2. Open `tallow.db` from your project directory
3. Browse the `orders` and `order_items` tables

## Step 5: Test Edge Cases

### Empty Cart Protection
1. Try navigating directly to `/checkout` with an empty cart
2. You should be redirected to the product page with an error message

### Form Validation
1. Try submitting the checkout form with:
   - Missing required fields → Should show validation errors
   - Invalid email format → Should show email validation error
   - Invalid phone number → Should show phone validation error
   - Invalid ZIP code → Should show ZIP validation error

### Quantity Limits
1. Try adding more than 10 items to cart
2. Should be capped at 10
3. Try setting quantity to 0 or negative → Should show error

### Session Persistence
1. Add items to cart
2. Close browser (not just the tab)
3. Reopen browser and navigate back to the site
4. Cart should be empty (session-based carts don't persist)

## Step 6: Understanding the Architecture

### How the Cart Works

**Session-Based Storage:**
- Cart data is stored in Flask's session (encrypted cookie)
- Format: List of dictionaries with product info
- Persists during browser session only
- No login required

**Cart Structure:**
```python
session['cart'] = [
    {
        'name': 'Pure Beef Tallow Moisturizer',
        'price': 24.99,
        'size': '4 oz',
        'quantity': 2
    }
]
```

### Order Processing Flow

1. **Add to Cart** (`/add-to-cart` POST)
   - Validates product data
   - Checks if product already in cart
   - Updates session

2. **View Cart** (`/cart` GET)
   - Retrieves cart from session
   - Calculates totals
   - Displays cart items

3. **Update Cart** (`/update-cart` POST)
   - Validates new quantity
   - Updates session

4. **Remove from Cart** (`/remove-from-cart` POST)
   - Filters out item from cart
   - Updates session

5. **Checkout** (`/checkout` GET/POST)
   - GET: Displays form with order summary
   - POST: Validates form, creates Order and OrderItems, saves to DB, clears cart

6. **Confirmation** (`/confirmation/<order_id>` GET)
   - Retrieves order from database
   - Displays order details

### Database Models

**Order Model** (`models.py`):
- Stores customer info, shipping address, totals, status
- All monetary values stored in cents (avoids floating-point issues)
- Relationship: One order has many order items

**OrderItem Model** (`models.py`):
- Stores product snapshot (name, price, size)
- Quantity and subtotal
- Foreign key to Order

### Configuration

**Tax Rate:** 8% (configurable in `calculate_cart_totals()` function in `app.py`)

**Shipping:**
- $5.00 flat rate for orders under $50
- FREE for orders $50 and above
- Configurable in `calculate_cart_totals()` function

**Session Security:**
- CSRF protection enabled via Flask-WTF
- Secret key used for session encryption (set in `config.py`)

## Troubleshooting

### Database Migration Errors

If you encounter migration errors:

```bash
# Remove existing migrations
rm -rf migrations/

# Remove database file
rm tallow.db

# Start fresh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Cart Not Updating

If cart changes aren't reflected:

1. Check that `session.modified = True` is set in cart update functions
2. Verify that SECRET_KEY is set in `config.py`
3. Clear browser cookies and try again

### Form Validation Not Working

If form validation isn't working:

1. Check that CSRF token is included in forms: `{{ form.csrf_token }}`
2. Verify Flask-WTF is installed: `pip list | grep Flask-WTF`
3. Check browser console for JavaScript errors

### Orders Not Saving to Database

If orders aren't being saved:

1. Check database connection: Does `tallow.db` file exist?
2. Verify migrations ran: `flask db current` (should show a revision ID)
3. Check app logs for errors
4. Try creating order manually in Python shell to isolate issue

## Next Steps (Future Phases)

### Phase 3: Stripe Payment Integration
- Add Stripe API keys to `.env` file
- Implement Stripe Checkout Session
- Update order status after successful payment
- Send order confirmation emails

### Additional Features to Consider
- Product inventory tracking
- Order history for customers (requires user authentication)
- Admin panel to view/manage orders
- Email notifications (order confirmation, shipping updates)
- Multiple product support (currently only 1 product)
- Discount codes/coupons
- Multiple shipping options

## Getting Help

If you encounter issues:

1. Check Flask logs for error messages
2. Verify all dependencies are installed: `pip list`
3. Ensure database migrations completed successfully
4. Review form validation errors in browser
5. Check browser console for JavaScript errors

## Summary

You've successfully implemented:
- ✅ Session-based shopping cart
- ✅ Add/update/remove cart items
- ✅ Dynamic cart counter in navigation
- ✅ Checkout form with validation
- ✅ Order storage in SQLite database
- ✅ Order confirmation page
- ✅ Responsive design (mobile-friendly)

The e-commerce foundation is ready. Next phase will add Stripe payment processing!