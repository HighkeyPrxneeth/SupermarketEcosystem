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

// Form validation
const form = document.getElementById('pavilions-form');
const vehicleInput = document.getElementById('vehicle-number');
const phoneInput = document.getElementById('phone-number');
const vehicleError = document.getElementById('vehicle-error');
const phoneError = document.getElementById('phone-error');

// Simple validation patterns
const vehiclePattern = /^[A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{1,4}$/;
const phonePattern = /^\d{10}$/;

form.addEventListener('submit', function(event) {
    let isValid = true;
    
    // Validate vehicle number
    if (!vehiclePattern.test(vehicleInput.value.toUpperCase())) {
        vehicleError.style.display = 'block';
        vehicleInput.focus();
        isValid = false;
    } else {
        vehicleError.style.display = 'none';
    }
    
    // Validate phone number
    if (!phonePattern.test(phoneInput.value)) {
        phoneError.style.display = 'block';
        if (isValid) phoneInput.focus();
        isValid = false;
    } else {
        phoneError.style.display = 'none';
    }
    
    if (!isValid) {
        event.preventDefault();
    }
});

// Clean input as user types
vehicleInput.addEventListener('input', function() {
    this.value = this.value.toUpperCase();
    if (vehiclePattern.test(this.value)) {
        vehicleError.style.display = 'none';
    }
});

phoneInput.addEventListener('input', function() {
    this.value = this.value.replace(/[^\d]/g, '').substring(0, 10);
    if (phonePattern.test(this.value)) {
        phoneError.style.display = 'none';
    }
});
const vehicleOptions = document.querySelectorAll('.vehicle-option');
const vehicleTypeInput = document.getElementById('vehicle-type');

vehicleOptions.forEach(option => {
    option.addEventListener('click', function() {
        // Remove active class from all options
        vehicleOptions.forEach(opt => opt.classList.remove('active'));
        
        // Add active class to clicked option
        this.classList.add('active');
        
        // Update hidden input value
        vehicleTypeInput.value = this.dataset.type;
        
        // Update vehicle number label icon based on selected vehicle type
        const vehicleLabel = document.querySelector('label[for="vehicle-number"] i');
        if (this.dataset.type === 'bike') {
            vehicleLabel.className = 'fas fa-motorcycle';
        } else {
            vehicleLabel.className = 'fas fa-car';
        }
    });
});