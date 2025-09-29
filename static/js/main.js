/**
 * Main JavaScript for Tallow & Co. Website
 *
 * This file contains interactive functionality:
 * - Mobile menu toggle
 * - Smooth scrolling
 * - Form validation enhancements
 * - Dynamic UI interactions
 */

// Wait for the DOM to fully load before running JavaScript
document.addEventListener('DOMContentLoaded', function() {

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================

    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        // Toggle mobile menu when hamburger button is clicked
        mobileMenuButton.addEventListener('click', function() {
            // Toggle the 'hidden' class to show/hide the menu
            mobileMenu.classList.toggle('hidden');

            // Change hamburger icon to X icon when menu is open
            const icon = this.querySelector('i');
            if (mobileMenu.classList.contains('hidden')) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            } else {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            }
        });

        // Close mobile menu when a link is clicked
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                const icon = mobileMenuButton.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
    }


    // ============================================
    // SMOOTH SCROLLING FOR ANCHOR LINKS
    // ============================================

    // Select all links that start with #
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only process if it's a valid anchor (not just #)
            if (href !== '#' && href.length > 1) {
                const target = document.querySelector(href);

                if (target) {
                    e.preventDefault();
                    // Scroll to the target element smoothly
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });


    // ============================================
    // FORM VALIDATION ENHANCEMENT
    // ============================================

    // Add real-time validation feedback for forms
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');

        inputs.forEach(input => {
            // Add blur event (when user leaves the field)
            input.addEventListener('blur', function() {
                validateInput(this);
            });

            // Add input event (while user is typing)
            input.addEventListener('input', function() {
                // Remove error styling when user starts correcting
                if (this.value.trim() !== '') {
                    this.classList.remove('border-red-500');
                    this.classList.add('border-gray-300');

                    // Remove error message if exists
                    const errorMsg = this.parentElement.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
        });
    });

    function validateInput(input) {
        // Check if the field is empty
        if (input.value.trim() === '') {
            showError(input, 'This field is required');
            return false;
        }

        // Email validation
        if (input.type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input.value)) {
                showError(input, 'Please enter a valid email address');
                return false;
            }
        }

        // If validation passes, remove error styling
        input.classList.remove('border-red-500');
        input.classList.add('border-gray-300');
        const errorMsg = input.parentElement.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }

        return true;
    }

    function showError(input, message) {
        // Add error styling to input
        input.classList.remove('border-gray-300');
        input.classList.add('border-red-500');

        // Check if error message already exists
        const existingError = input.parentElement.querySelector('.error-message');
        if (!existingError) {
            // Create and insert error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-red-500 text-sm mt-1';
            errorDiv.textContent = message;
            input.parentElement.appendChild(errorDiv);
        }
    }


    // ============================================
    // QUANTITY SELECTOR (Product Page)
    // ============================================

    const quantityInput = document.querySelector('input[type="number"]');

    if (quantityInput) {
        const minusButton = quantityInput.previousElementSibling;
        const plusButton = quantityInput.nextElementSibling;

        if (minusButton) {
            minusButton.addEventListener('click', function(e) {
                e.preventDefault();
                let currentValue = parseInt(quantityInput.value) || 1;
                if (currentValue > 1) {
                    quantityInput.value = currentValue - 1;
                }
            });
        }

        if (plusButton) {
            plusButton.addEventListener('click', function(e) {
                e.preventDefault();
                let currentValue = parseInt(quantityInput.value) || 1;
                const maxValue = parseInt(quantityInput.getAttribute('max')) || 99;
                if (currentValue < maxValue) {
                    quantityInput.value = currentValue + 1;
                }
            });
        }
    }


    // ============================================
    // SCROLL TO TOP BUTTON (Optional Enhancement)
    // ============================================

    // Create scroll-to-top button (hidden by default)
    const scrollButton = document.createElement('button');
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollButton.className = 'fixed bottom-8 right-8 bg-primary text-white w-12 h-12 rounded-full shadow-lg hover:bg-opacity-90 transition-all duration-200 hidden z-50';
    scrollButton.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(scrollButton);

    // Show/hide scroll button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.classList.remove('hidden');
        } else {
            scrollButton.classList.add('hidden');
        }
    });

    // Scroll to top when button is clicked
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });


    // ============================================
    // IMAGE GALLERY (Product Page - Optional)
    // ============================================

    const thumbnails = document.querySelectorAll('.grid img[alt^="Product view"]');
    const mainImage = document.querySelector('img[alt*="Moisturizer"]');

    if (thumbnails.length > 0 && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Remove active border from all thumbnails
                thumbnails.forEach(t => {
                    t.classList.remove('border-2', 'border-primary');
                });

                // Add active border to clicked thumbnail
                this.classList.add('border-2', 'border-primary');

                // Change main image source (in a real app, this would change to different images)
                // For now, it just demonstrates the interaction
                mainImage.src = this.src;
            });
        });
    }


    // ============================================
    // AUTO-DISMISS FLASH MESSAGES
    // ============================================

    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            message.style.transition = 'all 0.3s ease-out';

            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });


    // ============================================
    // CONSOLE MESSAGE (Optional - can remove)
    // ============================================

    console.log('%c🥩 Tallow & Co. Website', 'font-size: 20px; font-weight: bold; color: #8B7355;');
    console.log('%cBuilt with Flask & Tailwind CSS', 'font-size: 12px; color: #666;');

});


/**
 * UTILITY FUNCTIONS
 * Helper functions that can be used throughout the application
 */

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format price (useful for future shopping cart functionality)
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

// Validate email format
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}