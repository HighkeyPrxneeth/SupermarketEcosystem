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

// Print functionality
document.getElementById('print-bill').addEventListener('click', () => {
    window.print();
});

// Done button functionality
document.getElementById('done-btn').addEventListener('click', () => {
    // Get the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const custId = urlParams.get('cust');
    
    // Clear any remaining cart/order data
    sessionStorage.removeItem('cartData');
    sessionStorage.removeItem('orderSummary');
    
    // Navigate to home page
    window.location.href = '/';
});