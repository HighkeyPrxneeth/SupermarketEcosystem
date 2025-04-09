// Theme toggle functionality
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('i');

// Check for saved theme preference or use preferred color scheme
const savedTheme = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeIcon.classList.replace('fa-moon', 'fa-sun');
}

// Toggle theme when button is clicked
themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    let newTheme;
    
    if (currentTheme === 'dark') {
        newTheme = '';
        themeIcon.classList.replace('fa-sun', 'fa-moon');
    } else {
        newTheme = 'dark';
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    }
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Load cart data from session storage
let cartData;
try {
    const storedCartData = sessionStorage.getItem('cartData');
    if (storedCartData) {
        cartData = JSON.parse(storedCartData);
    } else {
        // If no cart data, redirect to shop
        window.location.href = '/shop';
    }
} catch (error) {
    console.error('Error loading cart data:', error);
    window.location.href = '/shop';
}

// Format currency
const formatCurrency = (amount) => {
    return '₹' + amount.toFixed(2);
};

// Global variables
let appliedDiscount = 0;
let originalTotal = cartData.summary.total;
let finalTotal = originalTotal;

// Populate order summary
const populateOrderSummary = () => {
    const summaryItems = document.getElementById('summary-items');
    const summarySubtotal = document.getElementById('summary-subtotal');
    const summaryTax = document.getElementById('summary-tax');
    const summaryTotal = document.getElementById('summary-total');
    const payAmount = document.getElementById('pay-amount');
    
    // Add items to summary
    cartData.items.forEach(item => {
        const summaryItem = document.createElement('div');
        summaryItem.className = 'summary-item';
        summaryItem.innerHTML = `
            <div class="summary-item-icon">
                <i class="fas ${item.icon}"></i>
            </div>
            <div class="summary-item-details">
                <div class="summary-item-name">${item.name}</div>
                <div class="summary-item-price">${formatCurrency(item.price)} per unit</div>
            </div>
            <div class="summary-item-quantity">${item.quantity.toFixed(1)} units</div>
        `;
        summaryItems.appendChild(summaryItem);
    });
    
    // Update summary amounts
    summarySubtotal.textContent = formatCurrency(cartData.summary.subtotal);
    summaryTax.textContent = formatCurrency(cartData.summary.tax);
    summaryTotal.textContent = formatCurrency(cartData.summary.total);
    payAmount.textContent = formatCurrency(cartData.summary.total);
    
    // Store original total
    originalTotal = cartData.summary.total;
    finalTotal = originalTotal;
};

// Payment method selection
const setupPaymentMethodToggle = () => {
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    const cardDetails = document.getElementById('card-details');
    const upiDetails = document.getElementById('upi-details');
    const walletDetails = document.getElementById('wallet-details');
    const codDetails = document.getElementById('cod-details');
    
    // Hide all initially except default (card)
    cardDetails.style.display = 'block';
    upiDetails.style.display = 'none';
    walletDetails.style.display = 'none';
    codDetails.style.display = 'none';
    
    paymentMethods.forEach(method => {
        method.addEventListener('change', () => {
            // Hide all first
            cardDetails.style.display = 'none';
            upiDetails.style.display = 'none';
            walletDetails.style.display = 'none';
            codDetails.style.display = 'none';
            
            // Show selected
            switch(method.value) {
                case 'card':
                    cardDetails.style.display = 'block';
                    break;
                case 'upi':
                    upiDetails.style.display = 'block';
                    break;
                case 'wallet':
                    walletDetails.style.display = 'block';
                    break;
                case 'cod':
                    codDetails.style.display = 'block';
                    break;
            }
        });
    });
};

// Coupon code functionality
const setupCouponCode = () => {
    const couponToggle = document.getElementById('coupon-toggle');
    const couponMenu = document.getElementById('coupon-menu');
    const closeCoupon = document.getElementById('close-coupon');
    const applyCouponButtons = document.querySelectorAll('.apply-coupon-btn');
    const appliedCoupon = document.getElementById('applied-coupon');
    const appliedCode = document.getElementById('applied-code');
    const removeCoupon = document.getElementById('remove-coupon');
    const discountRow = document.getElementById('discount-row');
    const summaryDiscount = document.getElementById('summary-discount');
    const summaryTotal = document.getElementById('summary-total');
    const payAmount = document.getElementById('pay-amount');
    
    // Toggle coupon menu
    couponToggle.addEventListener('click', () => {
        couponMenu.classList.toggle('active');
    });
    
    // Close coupon menu
    closeCoupon.addEventListener('click', () => {
        couponMenu.classList.remove('active');
    });
    
    // Handle clicking outside to close
    document.addEventListener('click', (e) => {
        if (!couponMenu.contains(e.target) && e.target !== couponToggle) {
            couponMenu.classList.remove('active');
        }
    });
    
    // Apply coupon buttons
    applyCouponButtons.forEach(button => {
        button.addEventListener('click', () => {
            const couponItem = button.closest('.coupon-item');
            const code = couponItem.dataset.code;
            const discount = parseFloat(couponItem.dataset.discount) / 100;
            
            // Calculate discount amount
            const discountAmount = originalTotal * discount;
            finalTotal = originalTotal - discountAmount;
            
            // Update display
            appliedCode.textContent = code;
            summaryDiscount.textContent = `-${formatCurrency(discountAmount)}`;
            summaryTotal.textContent = formatCurrency(finalTotal);
            payAmount.textContent = formatCurrency(finalTotal);
            
            // Show applied message & discount row
            appliedCoupon.style.display = 'flex';
            discountRow.style.display = 'flex';
            
            // Store applied discount
            appliedDiscount = discount;
            
            // Close menu
            couponMenu.classList.remove('active');
            couponToggle.style.display = 'none';
        });
    });
    
    // Remove coupon
    removeCoupon.addEventListener('click', () => {
        // Reset to original total
        finalTotal = originalTotal;
        appliedDiscount = 0;
        
        // Update display
        summaryTotal.textContent = formatCurrency(originalTotal);
        payAmount.textContent = formatCurrency(originalTotal);
        discountRow.style.display = 'none';
        appliedCoupon.style.display = 'none';
        couponToggle.style.display = 'flex';
    });
};

// Payment processing simulation
const simulatePayment = () => {
    const paymentOverlay = document.getElementById('payment-overlay');
    const progressBar = document.getElementById('progress-bar');
    const processTitle = document.getElementById('process-title');
    const processMessage = document.getElementById('process-message');
    const processAnimation = document.querySelector('.process-animation');
    
    // Show overlay
    paymentOverlay.classList.add('active');
    
    // Initialize progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        progressBar.style.width = `${progress}%`;
        
        // Update messages based on progress
        if (progress === 30) {
            processMessage.textContent = 'Verifying payment details...';
        } else if (progress === 60) {
            processMessage.textContent = 'Processing transaction...';
        } else if (progress === 90) {
            processMessage.textContent = 'Almost there...';
        }
        
        if (progress >= 100) {
            clearInterval(progressInterval);
            
            // Show success message
            processTitle.textContent = 'Payment Successful!';
            processMessage.innerHTML = 'Your order has been placed successfully.<br>Thank you for shopping with us.';
            
            // Replace spinner with success icon
            processAnimation.innerHTML = `
                <div class="success-animation">
                    <div class="success-circle">
                        <i class="fas fa-check success-icon"></i>
                    </div>
                </div>
                <div class="redirect-message">
                    Redirecting to shop in <span class="redirect-countdown">5</span> seconds...
                </div>
            `;
            
            // Start countdown for redirect
            let countdown = 5;
            const countdownElement = document.querySelector('.redirect-countdown');
            const countdownInterval = setInterval(() => {
                countdown--;
                countdownElement.textContent = countdown;
                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    
                    // Prepare order data to send to server
                    const selectedPaymentMethod = document.querySelector('input[name="payment-method"]:checked').value;
                    
                    const orderData = {
                        items: cartData.items.map(item => ({
                            id: item.id,
                            quantity: item.quantity,
                            price: item.price
                        })),
                        summary: {
                            subtotal: cartData.summary.subtotal,
                            tax: cartData.summary.tax,
                            discount: appliedDiscount > 0 ? (originalTotal * appliedDiscount) : 0,
                            total: finalTotal
                        },
                        paymentMethod: selectedPaymentMethod
                    };
                    
                    // Send order data to server
                    fetch('/process-payment', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(orderData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Payment processed:', data);
                        // Clear cart data
                        sessionStorage.removeItem('cartData');
                        // Redirect to shop
                        window.location.href = '/shop';
                    })
                    .catch(error => {
                        console.error('Error processing payment:', error);
                        // Still redirect to shop even on error
                        sessionStorage.removeItem('cartData');
                        window.location.href = '/shop';
                    });
                }
            }, 1000);
        }
    }, 100);
};

// Form validation (basic)
const validateForm = () => {
    const selectedMethod = document.querySelector('input[name="payment-method"]:checked').value;
    
    if (selectedMethod === 'card') {
        const cardNumber = document.getElementById('card-number').value;
        const expiry = document.getElementById('expiry').value;
        const cvv = document.getElementById('cvv').value;
        const cardName = document.getElementById('card-name').value;
        
        if (!cardNumber || !expiry || !cvv || !cardName) {
            alert('Please fill in all card details');
            return false;
        }
    } else if (selectedMethod === 'upi') {
        const upiId = document.getElementById('upi-id').value;
        if (!upiId) {
            alert('Please enter UPI ID');
            return false;
        }
    } else if (selectedMethod === 'wallet') {
        const walletType = document.querySelector('input[name="wallet-type"]:checked');
        const mobileNumber = document.getElementById('wallet-mobile').value;
        
        if (!walletType || !mobileNumber) {
            alert('Please select wallet type and enter mobile number');
            return false;
        }
    }
    
    return true;
};

// Setup back button
const setupBackButton = () => {
    const backButton = document.getElementById('back-to-shop');
    backButton.addEventListener('click', () => {
        window.history.back();
    });
};

// Setup pay now button
const setupPayButton = () => {
    const payButton = document.getElementById('pay-now-btn');
    
    payButton.addEventListener('click', () => {
        if (validateForm()) {
            simulatePayment();
        }
    });
};

// Card number formatting
const setupCardFormatting = () => {
    const cardNumber = document.getElementById('card-number');
    const expiry = document.getElementById('expiry');
    
    // Format card number with spaces
    cardNumber.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        let formattedValue = '';
        
        for (let i = 0; i < value.length; i++) {
            if (i > 0 && i % 4 === 0) {
                formattedValue += ' ';
            }
            formattedValue += value[i];
        }
        
        e.target.value = formattedValue;
    });
    
    // Format expiry as MM/YY
    expiry.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        
        if (value.length > 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        
        e.target.value = value;
    });
};

// Initialize all functionality
document.addEventListener('DOMContentLoaded', () => {
    populateOrderSummary();
    setupPaymentMethodToggle();
    setupCouponCode();
    setupBackButton();
    setupPayButton();
    setupCardFormatting();
});