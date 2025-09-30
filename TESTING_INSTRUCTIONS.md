# Quick Testing Instructions for Stripe Integration

## Prerequisites
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` file (copy from `.env.example`):
   ```env
   SECRET_KEY=your-secret-key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=
   ```

3. Start the Flask app:
   ```bash
   python app.py
   ```

## Quick Test - Successful Payment

1. **Navigate to product page**: http://localhost:5000/product

2. **Add to cart**:
   - Select quantity
   - Click "Add to Cart"

3. **Go to checkout**: http://localhost:5000/cart
   - Click "Proceed to Checkout"

4. **Fill out form**:
   - Name: Test Customer
   - Email: test@example.com
   - Phone: (555) 123-4567
   - Address: 123 Test St, Test City, CA 12345

5. **Click "Proceed to Secure Checkout"**
   - You'll be redirected to Stripe's checkout page

6. **Use test card on Stripe page**:
   - Card: `4242 4242 4242 4242`
   - Expiration: `12/34`
   - CVC: `123`
   - Name: Any name
   - Billing ZIP: `12345`

7. **Complete payment**:
   - Click "Pay"
   - You should be redirected back to confirmation page
   - Order status should show "Payment Successful" (green banner)

## Quick Test - Cancelled Payment

1. Follow steps 1-5 above
2. On Stripe checkout page, click **browser back button** or close the tab
3. You should see the cancellation page with options to try again

## Test Card Numbers

| Scenario | Card Number | Result |
|----------|-------------|--------|
| Success | `4242 4242 4242 4242` | Payment succeeds |
| Declined | `4000 0000 0000 0002` | Card declined |
| Insufficient funds | `4000 0000 0000 9995` | Declined - insufficient funds |
| 3D Secure | `4000 0025 0000 3155` | Requires authentication |

**All test cards**:
- Expiration: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

## Verify in Stripe Dashboard

1. Go to: https://dashboard.stripe.com/test/payments
2. You should see your test payment listed
3. Click on it to see details including order metadata

## Testing Webhooks (Optional)

### Option 1: Without Webhook Secret (Easiest)
- Leave `STRIPE_WEBHOOK_SECRET` empty in `.env`
- Payments will work, but webhooks won't have signature verification
- Check Flask console for webhook logs

### Option 2: With Stripe CLI (Recommended)
1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks: `stripe listen --forward-to localhost:5000/webhook`
4. Copy the webhook secret to `.env`
5. Restart Flask app
6. Make a test payment
7. Watch the Stripe CLI output for webhook events

## What to Check

✅ **Payment Success Flow**:
- Order created in database with "pending" status
- Redirected to Stripe checkout
- After payment, redirected to confirmation page
- Order status updated to "paid"
- Stripe payment ID stored in database

✅ **Payment Cancel Flow**:
- Order created in database
- User cancels on Stripe page
- Redirected to cancel page
- Order status updated to "cancelled"

✅ **Database**:
```bash
# Check orders in database
sqlite3 instance/tallow.db
SELECT id, customer_name, status, total, stripe_payment_id FROM orders;
.exit
```

## Common Issues

**Issue**: "Invalid API key"
- Check `.env` file has correct Stripe keys
- Make sure you're using test keys (start with `sk_test_`)

**Issue**: "Cart is empty after cancellation"
- This is expected behavior - cart is cleared when checkout session is created
- User needs to add items to cart again

**Issue**: "Order status not updating to paid"
- Check Flask console for errors
- Verify Stripe webhook is set up correctly
- The `/success` route should update the status even without webhooks

## Need More Help?

See full documentation in: **STRIPE_SETUP.md**

## Summary of Changes

**Files Modified**:
- ✅ requirements.txt - Added Stripe
- ✅ config.py - Added Stripe config
- ✅ app.py - Added Stripe integration + 3 new routes
- ✅ templates/checkout.html - Updated messaging
- ✅ templates/confirmation.html - Added payment status display

**Files Created**:
- ✅ .env.example - Environment variable template
- ✅ templates/cancel.html - Payment cancellation page
- ✅ STRIPE_SETUP.md - Complete setup guide
- ✅ TESTING_INSTRUCTIONS.md - This file

**Database**:
- No new migrations needed - `stripe_payment_id` field already exists in Order model

---

**You're ready to test!** 🎉