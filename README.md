# Tallow & Co. - Beef Tallow Moisturizer E-Commerce Website

A beautiful, responsive e-commerce website built with Flask for selling handcrafted beef tallow moisturizer.

## 🌟 Features

- **Modern Design**: Clean, professional design with Tailwind CSS
- **Fully Responsive**: Works beautifully on desktop, tablet, and mobile devices
- **4 Main Pages**:
  - Homepage with hero section and product showcase
  - About page with brand story and values
  - Product detail page with ingredients and usage instructions
  - Contact page with functional form
- **Mobile Navigation**: Hamburger menu for mobile devices
- **Flash Messages**: User feedback system for form submissions
- **Ready for Expansion**: Easy to add database and Stripe payment integration

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- A code editor (VS Code, PyCharm, etc.)

## 🚀 Quick Start Guide

### Step 1: Clone or Navigate to the Project

```bash
cd /mnt/c/Users/acnut/Coding/Tallow_Website
```

### Step 2: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from other Python projects.

**On Windows (WSL/Linux):**
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

**On Windows (WSL/Linux):**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your command line prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask and all other required packages.

### Step 5: Run the Development Server

```bash
flask run
```

Or alternatively:
```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

### Step 6: View the Website

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

🎉 **Congratulations!** Your website is now running locally!

## 📁 Project Structure

```
Tallow_Website/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .flaskenv                   # Flask environment variables
├── README.md                   # This file
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css          # Custom CSS styles
│   ├── js/
│   │   └── main.js            # JavaScript for interactivity
│   └── images/                # Product images
│       ├── placeholder-hero.jpg
│       ├── placeholder-product.jpg
│       ├── placeholder-product-detail.jpg
│       └── placeholder-story.jpg
└── templates/                  # HTML templates
    ├── base.html              # Base template (navbar, footer)
    ├── index.html             # Homepage
    ├── about.html             # About page
    ├── product.html           # Product detail page
    └── contact.html           # Contact page
```

## 🎨 Customization Guide

### Changing Colors

The color scheme is defined in two places:

1. **Tailwind Config** (in `templates/base.html`):
```javascript
colors: {
    primary: '#8B7355',      // Warm brown
    secondary: '#D4A574',    // Light tan
    accent: '#F5E6D3',       // Cream
    dark: '#3E3E3E',         // Dark gray
}
```

2. **CSS File** (`static/css/style.css`):
Look for color values and replace them with your preferred colors.

### Replacing Placeholder Images

Simply replace the files in `static/images/` with your own product photos:
- `placeholder-hero.jpg` - Main hero image (homepage)
- `placeholder-product.jpg` - Product thumbnail
- `placeholder-product-detail.jpg` - Product detail page main image
- `placeholder-story.jpg` - About page story image

### Updating Content

All page content is in the `templates/` folder:
- Edit `templates/index.html` for homepage text
- Edit `templates/about.html` for your brand story
- Edit `templates/product.html` for product details
- Update product data in `app.py` (search for `product_data`)

### Changing Site Name

Edit the `inject_site_info()` function in `app.py`:
```python
return {
    'site_name': 'Your Business Name',
    'current_year': 2024
}
```

## 🔧 Common Commands

### Start the development server:
```bash
flask run
```

### Run with debug mode (auto-reload on code changes):
```bash
flask run --debug
```

### Run on a different port:
```bash
flask run --port=8000
```

### Make the site accessible on your local network:
```bash
flask run --host=0.0.0.0
```

### Stop the server:
Press `Ctrl + C` in the terminal

### Deactivate virtual environment:
```bash
deactivate
```

## 📝 Next Steps - Adding Features

### 1. Database Integration (SQLAlchemy)

Uncomment these lines in `requirements.txt`:
```
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
```

Then run:
```bash
pip install Flask-SQLAlchemy Flask-Migrate
```

Create a `models.py` file to define your database structure.

### 2. Stripe Payment Integration

Uncomment in `requirements.txt`:
```
stripe==7.8.0
```

Install:
```bash
pip install stripe
```

Get your API keys from [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)

Add to `.env` file (create this file):
```
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
```

### 3. Email Functionality

Install Flask-Mail:
```bash
pip install Flask-Mail
```

Configure email settings in `config.py` and use Flask-Mail to send emails from the contact form.

### 4. Shopping Cart

Add session management to track items in the cart. Flask has built-in session support.

## 🐛 Troubleshooting

### Problem: `flask: command not found`

**Solution**: Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

### Problem: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: Port 5000 is already in use

**Solution**: Use a different port:
```bash
flask run --port=8000
```

### Problem: Changes not showing up

**Solution**:
1. Hard refresh your browser (Ctrl + Shift + R or Cmd + Shift + R)
2. Make sure debug mode is on (it should auto-reload)
3. Clear your browser cache

### Problem: CSS/JS not loading

**Solution**: Check that files are in the correct locations:
- CSS should be in `static/css/`
- JS should be in `static/js/`
- Images should be in `static/images/`

## 📚 Learning Resources

### Flask Documentation
- Official Docs: https://flask.palletsprojects.com/
- Quickstart: https://flask.palletsprojects.com/quickstart/
- Tutorial: https://flask.palletsprojects.com/tutorial/

### Tailwind CSS
- Documentation: https://tailwindcss.com/docs
- Components: https://tailwindui.com/components

### Python
- Python.org: https://www.python.org/
- Learn Python: https://docs.python.org/3/tutorial/

## 💡 Tips for Beginners

1. **Make Small Changes**: Don't try to change everything at once. Make one small change, save, and refresh to see the result.

2. **Read the Comments**: The code has extensive comments explaining what each part does. Read them!

3. **Use Print Statements**: Add `print()` statements in `app.py` to see what's happening:
   ```python
   print(f"Name: {name}, Email: {email}")
   ```

4. **Check the Terminal**: Error messages in the terminal often tell you exactly what's wrong.

5. **Browser DevTools**: Press F12 in your browser to see CSS, JavaScript errors, and network issues.

## 🚀 Deployment

When you're ready to deploy your website to production:

1. **Choose a hosting provider**: Heroku, PythonAnywhere, DigitalOcean, AWS, etc.
2. **Set environment variables**: Never commit secrets (API keys) to Git
3. **Use a production server**: Gunicorn or uWSGI instead of Flask's built-in server
4. **Set DEBUG to False**: In production, always use `DEBUG = False`

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Read the error message carefully
3. Search for the error on Google or Stack Overflow
4. Review the Flask documentation

## 🎉 Have Fun!

This is your project now! Experiment, break things, fix them, and learn. The best way to learn web development is by building real projects like this one.

Happy coding! 🥩✨