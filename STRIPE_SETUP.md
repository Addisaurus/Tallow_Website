# Stripe Payment Integration Setup Guide

This guide will help you set up and test Stripe payments for the Tallow & Co. e-commerce website.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Testing Payments](#testing-payments)
4. [Webhook Setup](#webhook-setup)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

- A Stripe account (sign up at https://stripe.com)
- Python environment with all dependencies installed (`pip install -r requirements.txt`)
- Flask application running locally

---

## Environment Setup

### Step 1: Get Your Stripe API Keys

1. Log into your Stripe Dashboard: https://dashboard.stripe.com/test/apikeys
2. Make sure you're in **TEST MODE** (toggle in top right should say "Test mode")
3. Copy your API keys:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)

### Step 2: Create .env File

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Stripe keys:
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-here

   # Stripe API Keys (Test Mode)
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here

   # Leave webhook secret empty for now
   STRIPE_WEBHOOK_SECRET=
   ```

3. **IMPORTANT**: Never commit your `.env` file to version control! It's already in `.gitignore`.

### Step 3: Verify Installation

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Check the console for any errors related to Stripe initialization.

---

## Testing Payments

### Stripe Test Card Numbers

Stripe provides test card numbers for different scenarios:

#### Successful Payment
- **Card Number**: `4242 4242 4242 4242`
- **Expiration**: Any future date (e.g., `12/34`)
- **CVC**: Any 3 digits (e.g., `123`)
- **ZIP**: Any 5 digits (e.g., `12345`)

#### Declined Payment
- **Card Number**: `4000 0000 0000 0002`
- **Result**: Card will be declined

#### Requires Authentication (3D Secure)
- **Card Number**: `4000 0025 0000 3155`
- **Result**: Will prompt for 3D Secure authentication

#### Insufficient Funds
- **Card Number**: `4000 0000 0000 9995`
- **Result**: Card will be declined due to insufficient funds

**Full list of test cards**: https://stripe.com/docs/testing#cards

### Testing the Complete Flow

1. **Add Product to Cart**:
   - Navigate to the product page
   - Add item to cart
   - Go to cart and proceed to checkout

2. **Fill Out Checkout Form**:
   - Enter customer information
   - Fill in shipping address
   - Click "Proceed to Secure Checkout"

3. **Complete Payment on Stripe**:
   - You'll be redirected to Stripe's checkout page
   - Use test card number `4242 4242 4242 4242`
   - Enter any future expiration date
   - Enter any 3-digit CVC
   - Enter any email address
   - Fill in billing/shipping address
   - Click "Pay"

4. **Verify Success**:
   - You should be redirected back to the confirmation page
   - Order status should be "paid"
   - Check the database: order status should be updated to "paid"

### Testing Cancellation

1. Follow steps 1-2 above
2. On the Stripe checkout page, click the back button or close the tab
3. You should be redirected to the cancellation page
4. Check the database: order status should be "cancelled"

---

## Webhook Setup

Webhooks allow Stripe to notify your application about payment events even if the user closes their browser. This ensures payment status is always updated.

### Option 1: Local Testing with Stripe CLI (Recommended for Development)

1. **Install Stripe CLI**:
   - macOS: `brew install stripe/stripe-cli/stripe`
   - Windows: Download from https://github.com/stripe/stripe-cli/releases
   - Linux:
     ```bash
     wget https://github.com/stripe/stripe-cli/releases/latest/download/stripe_linux_amd64.tar.gz
     tar -xvf stripe_linux_amd64.tar.gz
     sudo mv stripe /usr/local/bin
     ```

2. **Login to Stripe CLI**:
   ```bash
   stripe login
   ```
   This will open a browser window to authenticate.

3. **Start Webhook Forwarding**:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

4. **Copy Webhook Secret**:
   - The CLI will display a webhook signing secret (starts with `whsec_`)
   - Copy this secret and add it to your `.env` file:
     ```env
     STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
     ```

5. **Restart Your Flask App**:
   ```bash
   python app.py
   ```

6. **Test Webhooks**:
   - Complete a test payment
   - Check the Stripe CLI output - you should see webhook events being received
   - Check your Flask console logs for webhook processing messages

### Option 2: Testing Webhooks Without Stripe CLI

The application is designed to work without webhook secrets for initial development:

1. Leave `STRIPE_WEBHOOK_SECRET` empty in `.env`
2. Webhooks will still process events but won't verify signatures
3. You'll see a warning in logs: "Processing webhook without signature verification (development mode)"

**Note**: This is only for development. Production must use webhook secrets!

### Option 3: Manual Webhook Testing

You can also trigger test webhooks from the Stripe Dashboard:

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Test in a local environment" or create a webhook endpoint
3. Select event type (e.g., `checkout.session.completed`)
4. Send test webhook

---

## Production Deployment

### Step 1: Switch to Live Mode

1. Log into Stripe Dashboard
2. Toggle from "Test mode" to "Live mode"
3. Navigate to: https://dashboard.stripe.com/apikeys
4. Copy your LIVE API keys:
   - Publishable key (starts with `pk_live_`)
   - Secret key (starts with `sk_live_`)

### Step 2: Update Production Environment Variables

Update your production `.env` file (or hosting platform's environment variables):

```env
FLASK_ENV=production
SECRET_KEY=your-super-secure-random-secret-key

# Stripe LIVE Keys
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
```

### Step 3: Set Up Production Webhooks

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL: `https://yourdomain.com/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Click "Add endpoint"
6. Copy the "Signing secret" and add it to your environment variables

### Step 4: Test Live Payments

**WARNING**: Use real card numbers carefully in live mode!

1. Make a small test purchase (e.g., $0.50)
2. Use a real card or your own card
3. Verify the payment appears in your Stripe Dashboard
4. Verify the order is marked as "paid" in your database
5. Refund the test transaction from Stripe Dashboard

---

## Troubleshooting

### Issue: "Stripe API key is not set"

**Solution**: Make sure your `.env` file has `STRIPE_SECRET_KEY` and the file is in the same directory as `app.py`.

### Issue: "Invalid API key provided"

**Solution**:
- Verify you copied the entire key from Stripe Dashboard
- Make sure there are no spaces before/after the key in `.env`
- Ensure you're using test keys (`sk_test_`) in test mode

### Issue: "Payment successful but order status not updated"

**Possible causes**:
1. Database not committing changes - check Flask logs for errors
2. Webhook not configured - order status is updated via webhooks
3. Order ID not found - check Stripe Dashboard > Payments > Metadata for order_id

**Solution**:
- Check Flask console logs for errors
- Verify webhooks are being received (Stripe CLI or Dashboard)
- Check database directly to see order status

### Issue: "Webhook signature verification failed"

**Solution**:
- Make sure `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe CLI or Dashboard
- Restart Flask app after updating `.env`
- If testing locally, make sure Stripe CLI is running: `stripe listen --forward-to localhost:5000/webhook`

### Issue: "Amount mismatch" error on success page

**Solution**:
- This is a security check to prevent payment tampering
- Check that cart totals match exactly between order creation and Stripe checkout
- Verify tax and shipping calculations are consistent

### Issue: User clicks "back" during payment and cart is empty

**Explanation**: The cart is cleared when the Stripe Checkout Session is created (not after payment). This prevents users from accidentally creating duplicate orders.

**Solution**: On the cancel page, direct users back to the product page to start a new order.

---

## Payment Flow Diagram

```
User adds to cart
       ↓
User proceeds to checkout
       ↓
Form validation (Flask)
       ↓
Order created in DB (status: "pending")
       ↓
Stripe Checkout Session created
       ↓
User redirected to Stripe
       ↓
    ┌───────────────┐
    │  User pays?   │
    └───────────────┘
         ↙      ↘
    YES          NO
     ↓            ↓
Success     Cancel page
route         (status: "cancelled")
     ↓
Verify payment
     ↓
Update order (status: "paid")
     ↓
Show confirmation
     ↓
Stripe sends webhook
     ↓
Webhook updates order (backup)
```

---

## Security Best Practices

1. **Never commit API keys** - Always use environment variables
2. **Use webhook secrets in production** - Verify webhook signatures
3. **Validate payment amounts** - Check order total matches payment amount
4. **Use HTTPS in production** - Required for Stripe
5. **Monitor Stripe Dashboard** - Regularly check for failed payments or disputes
6. **Keep Stripe library updated** - Run `pip install --upgrade stripe`
7. **Log payment events** - Keep logs for debugging and auditing

---

## Useful Links

- **Stripe Dashboard**: https://dashboard.stripe.com
- **Stripe API Docs**: https://stripe.com/docs/api
- **Stripe Testing Guide**: https://stripe.com/docs/testing
- **Stripe CLI**: https://stripe.com/docs/stripe-cli
- **Stripe Checkout Docs**: https://stripe.com/docs/payments/checkout

---

## Support

If you encounter issues not covered in this guide:

1. Check Flask console logs for error messages
2. Check Stripe Dashboard > Logs for API errors
3. Review Stripe's official documentation
4. Contact Stripe support: https://support.stripe.com

---

**Last Updated**: 2025-09-29
**Stripe API Version**: 2023-10-16
**Integration Type**: Stripe Checkout (Hosted)