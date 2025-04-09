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

let cart = [];
const productGrid = document.getElementById('product-grid');
const cartItems = document.getElementById('cart-items');
const cartEmpty = document.getElementById('cart-empty');
const cartCount = document.getElementById('cart-count');
const cartSubtotal = document.getElementById('cart-subtotal');
const cartTax = document.getElementById('cart-tax');
const cartTotal = document.getElementById('cart-total');
const cartDropArea = document.getElementById('cart-drop-area');
const cartBubbles = document.getElementById('cart-bubbles');

// Format currency
const formatCurrency = (amount) => {
    return '₹' + amount.toFixed(2);
};

// Update cart summary
const updateCartSummary = () => {
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    const tax = subtotal * 0.18;
    const total = subtotal + tax;
    
    cartSubtotal.textContent = formatCurrency(subtotal);
    cartTax.textContent = formatCurrency(tax);
    cartTotal.textContent = formatCurrency(total);
    cartCount.textContent = cart.reduce((count, item) => count + item.quantity, 0).toFixed(1);
    
    if (cart.length === 0) {
        cartEmpty.style.display = 'block';
    } else {
        cartEmpty.style.display = 'none';
    }
};

// Add item to cart
const addToCart = (product, quantity) => {
    // Check if product already in cart
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: quantity,
            icon: product.icon
        });
    }
    
    updateCartDisplay();
    addCartBubble();
};

// Remove item from cart
const removeFromCart = (productId) => {
    // Find and remove the item by filtering the array
    cart = cart.filter(item => item.id !== productId);
    // Update display after modifying the cart data
    updateCartDisplay();
};

// Update item quantity in cart
const updateCartQuantity = (productId, newQuantity) => {
    // Find the item index in the cart array
    const itemIndex = cart.findIndex(item => item.id === productId);
    
    if (itemIndex !== -1) {
        if (newQuantity <= 0) {
            // Remove item if quantity becomes zero or negative
            cart.splice(itemIndex, 1);
        } else {
            // Update quantity of existing item
            cart[itemIndex].quantity = newQuantity;
        }
        // Update the cart display after modifying cart data
        updateCartDisplay();
    }
};

// Update cart display
const updateCartDisplay = () => {
    // Clear current items
    while (cartItems.children.length > 0) {
        if (cartItems.firstChild === cartEmpty) {
            break;
        }
        cartItems.removeChild(cartItems.firstChild);
    }
    
    // Add each cart item to display
    cart.forEach(item => {
        const cartItemElement = document.createElement('div');
        cartItemElement.className = 'cart-item';
        cartItemElement.innerHTML = `
            <div class="cart-item-icon">
                <i class="fas ${item.icon}"></i>
            </div>
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${formatCurrency(item.price)} per unit</div>
            </div>
            <div class="cart-item-actions">
                <div class="cart-item-quantity">
                    <button class="quantity-btn decrease-btn" data-id="${item.id}">-</button>
                    <div class="cart-item-amount">${item.quantity.toFixed(1)}</div>
                    <button class="quantity-btn increase-btn" data-id="${item.id}">+</button>
                </div>
                <button class="cart-item-remove" data-id="${item.id}">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        
        cartItems.appendChild(cartItemElement);
    });
    
    // Show or hide the empty cart message
    if (cart.length === 0) {
        cartEmpty.style.display = 'block';
    } else {
        cartEmpty.style.display = 'none';
    }
    
    // Add event listeners to buttons - THIS IS THE KEY FIX for issues 2 & 3
    document.querySelectorAll('.cart-item .increase-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.dataset.id);
            const item = cart.find(item => item.id === id);
            if (item) {
                updateCartQuantity(id, item.quantity + 0.5);
            }
        });
    });
    
    document.querySelectorAll('.cart-item .decrease-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.dataset.id);
            const item = cart.find(item => item.id === id);
            if (item) {
                updateCartQuantity(id, item.quantity - 0.5);
            }
        });
    });
    
    document.querySelectorAll('.cart-item .cart-item-remove').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.dataset.id);
            removeFromCart(id);
        });
    });
    
    updateCartSummary();
};

// Create product cards
products.forEach(product => {
    const productCard = document.createElement('div');
    productCard.className = 'product-card';
    // Remove draggable attribute from the entire card
    productCard.dataset.id = product.id;
    
    productCard.innerHTML = `
        <div class="stock-info">${product.stock} in stock</div>
        <div class="product-image" draggable="true" data-id="${product.id}">
            <i class="fas ${product.icon}"></i>
        </div>
        <div class="product-details">
            <div class="product-name">${product.name}</div>
            <div class="product-category">${product.category}</div>
            <div class="product-price">${formatCurrency(product.price)} per unit</div>
            <div class="quantity-control">
                <div class="quantity-label">
                    <span>Quantity</span>
                    <span class="quantity-value" id="quantity-value-${product.id}">0.5</span>
                </div>
                <input type="range" class="quantity-slider" id="quantity-slider-${product.id}"
                    min="0.5" max="10" step="0.5" value="0.5">
            </div>
        </div>
    `;
    
    productGrid.appendChild(productCard);
    
    // Add quantity slider functionality
    const slider = document.getElementById(`quantity-slider-${product.id}`);
    const quantityValue = document.getElementById(`quantity-value-${product.id}`);
    
    slider.addEventListener('input', () => {
        // Snap to multiples of 0.5
        const value = parseFloat(slider.value);
        quantityValue.textContent = value.toFixed(1);
    });
    
    // Fix drag functionality to only apply to the image
    const productImage = productCard.querySelector('.product-image');
    
    productImage.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', JSON.stringify({
            id: product.id,
            quantity: parseFloat(document.getElementById(`quantity-slider-${product.id}`).value)
        }));
        productImage.classList.add('dragging');
    });
    
    productImage.addEventListener('dragend', () => {
        productImage.classList.remove('dragging');
    });
    
    // For touch devices (alternative to drag & drop)
    if (window.matchMedia('(hover: none)').matches) {
        // Replace slider with button for touch devices
        const touchBtn = document.createElement('button');
        touchBtn.className = 'add-to-cart-btn';
        touchBtn.innerHTML = `<i class="fas fa-cart-plus"></i> Add to Cart`;
        
        touchBtn.addEventListener('click', () => {
            const quantity = parseFloat(slider.value);
            addToCart(product, quantity);
        });
        
        productCard.querySelector('.product-details').appendChild(touchBtn);
    }
});

// Cart drop area functionality
cartDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    cartDropArea.classList.add('dragover');
});

cartDropArea.addEventListener('dragleave', () => {
    cartDropArea.classList.remove('dragover');
});

cartDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    cartDropArea.classList.remove('dragover');
    
    try {
        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        const product = products.find(p => p.id === data.id);
        
        if (product && data.quantity > 0) {
            addToCart(product, data.quantity);
        }
    } catch (error) {
        console.error('Invalid drop data:', error);
    }
});

// Add bubble animation to cart
const addCartBubble = () => {
    const bubble = document.createElement('div');
    bubble.className = 'cart-item-bubble';
    
    // Random position within the cart graphic
    const top = Math.floor(Math.random() * 30);
    const left = Math.floor(Math.random() * 30);
    
    bubble.style.top = `${top}px`;
    bubble.style.left = `${left}px`;
    
    // Random +1 or the actual item quantity
    bubble.textContent = Math.random() > 0.5 ? '+1' : '+';
    
    cartBubbles.appendChild(bubble);
    
    // Fade out and remove after animation
    setTimeout(() => {
        bubble.style.opacity = '0';
        setTimeout(() => {
            if (bubble.parentNode === cartBubbles) {
                cartBubbles.removeChild(bubble);
            }
        }, 300);
    }, 1000);
};

// Initialize cart display
updateCartDisplay();