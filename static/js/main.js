// AASEAANIC Flight Booking Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavbar();
    initForms();
    initAnimations();
    initDatePickers();
    initTooltips();
    initModals();
});

// Navbar functionality
function initNavbar() {
    const navbar = document.getElementById('mainNavbar');
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu close on link click
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {
                navbarCollapse.classList.remove('show');
            }
        });
    });
}

// Form enhancements
function initForms() {
    // Flight search form
    const searchForm = document.querySelector('#flightSearchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const departure = document.querySelector('#departure').value;
            const destination = document.querySelector('#destination').value;
            
            if (departure === destination) {
                e.preventDefault();
                showAlert('Departure and destination cannot be the same!', 'warning');
                return false;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Newsletter form
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[name="email"]').value;
            
            if (validateEmail(email)) {
                // Simulate subscription
                fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: new URLSearchParams(new FormData(this))
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Successfully subscribed to newsletter!', 'success');
                        this.reset();
                    } else {
                        showAlert('Error subscribing. Please try again.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Error subscribing. Please try again.', 'error');
                });
            } else {
                showAlert('Please enter a valid email address.', 'warning');
            }
        });
    }
    
    // Real-time form validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

// Animation functions
function initAnimations() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = '0.1s';
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.card, .destination-card, .feature-item').forEach(el => {
        observer.observe(el);
    });
}

// Date picker initialization
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (input.name === 'departure_date' || input.name === 'return_date') {
            input.min = today;
        }
    });
    
    // Return date should be after departure date
    const departureDate = document.querySelector('input[name="departure_date"]');
    const returnDate = document.querySelector('input[name="return_date"]');
    
    if (departureDate && returnDate) {
        departureDate.addEventListener('change', function() {
            returnDate.min = this.value;
            if (returnDate.value && returnDate.value < this.value) {
                returnDate.value = this.value;
            }
        });
    }
}

// Bootstrap tooltips and popovers
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Modal functionality
function initModals() {
    // Auto-focus first input in modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

// Utility functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required.';
    }
    
    // Email validation
    if (field.type === 'email' && value && !validateEmail(value)) {
        isValid = false;
        message = 'Please enter a valid email address.';
    }
    
    // Phone validation
    if (field.type === 'tel' && value && !/^[+]?[\d\s\-()]+$/.test(value)) {
        isValid = false;
        message = 'Please enter a valid phone number.';
    }
    
    // Date validation
    if (field.type === 'date' && value) {
        const date = new Date(value);
        const today = new Date();
        if (date < today) {
            isValid = false;
            message = 'Date cannot be in the past.';
        }
    }
    
    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) feedback.style.display = 'none';
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, message);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
    feedback.style.display = 'block';
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.messages-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Flight search functionality
function toggleTripType() {
    const tripType = document.querySelector('input[name="trip_type"]:checked').value;
    const returnDateGroup = document.querySelector('#returnDateGroup');
    
    if (returnDateGroup) {
        if (tripType === 'round_trip') {
            returnDateGroup.style.display = 'block';
            returnDateGroup.querySelector('input').required = true;
        } else {
            returnDateGroup.style.display = 'none';
            returnDateGroup.querySelector('input').required = false;
        }
    }
}

// Seat selection functionality
function selectSeat(seatElement, seatNumber) {
    // Remove previous selections
    document.querySelectorAll('.seat.selected').forEach(seat => {
        seat.classList.remove('selected');
    });
    
    // Select new seat
    seatElement.classList.add('selected');
    
    // Update hidden input
    const seatInput = document.querySelector('input[name="selected_seat"]');
    if (seatInput) {
        seatInput.value = seatNumber;
    }
    
    // Update seat info display
    updateSeatInfo(seatNumber);
}

function updateSeatInfo(seatNumber) {
    const seatInfo = document.querySelector('#selected-seat-info');
    if (seatInfo) {
        seatInfo.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-chair"></i>
                Selected Seat: <strong>${seatNumber}</strong>
            </div>
        `;
    }
}

// Booking form steps
function nextStep(currentStep) {
    const current = document.querySelector(`#step-${currentStep}`);
    const next = document.querySelector(`#step-${currentStep + 1}`);
    
    if (validateStep(currentStep)) {
        current.style.display = 'none';
        next.style.display = 'block';
        updateProgressBar(currentStep + 1);
    }
}

function prevStep(currentStep) {
    const current = document.querySelector(`#step-${currentStep}`);
    const prev = document.querySelector(`#step-${currentStep - 1}`);
    
    current.style.display = 'none';
    prev.style.display = 'block';
    updateProgressBar(currentStep - 1);
}

function validateStep(step) {
    const stepElement = document.querySelector(`#step-${step}`);
    const requiredFields = stepElement.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function updateProgressBar(step) {
    const progressBar = document.querySelector('.progress-bar');
    const totalSteps = document.querySelectorAll('[id^="step-"]').length;
    const progress = (step / totalSteps) * 100;
    
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
}

// Search suggestions
function initSearchSuggestions() {
    const searchInputs = document.querySelectorAll('.airport-search');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            if (query.length >= 2) {
                showAirportSuggestions(this, query);
            } else {
                hideAirportSuggestions(this);
            }
        });
    });
}

function showAirportSuggestions(input, query) {
    // This would typically fetch from an API
    const airports = [
        { code: 'JFK', name: 'John F. Kennedy International Airport', city: 'New York' },
        { code: 'LAX', name: 'Los Angeles International Airport', city: 'Los Angeles' },
        { code: 'CHI', name: 'Chicago O\'Hare International Airport', city: 'Chicago' },
        { code: 'MIA', name: 'Miami International Airport', city: 'Miami' },
        { code: 'SFO', name: 'San Francisco International Airport', city: 'San Francisco' }
    ];
    
    const filtered = airports.filter(airport => 
        airport.code.toLowerCase().includes(query) ||
        airport.name.toLowerCase().includes(query) ||
        airport.city.toLowerCase().includes(query)
    );
    
    if (filtered.length > 0) {
        const suggestions = createSuggestionsDropdown(filtered, input);
        showDropdown(input, suggestions);
    }
}

function createSuggestionsDropdown(airports, input) {
    const dropdown = document.createElement('div');
    dropdown.className = 'airport-suggestions dropdown-menu show';
    
    airports.forEach(airport => {
        const item = document.createElement('a');
        item.className = 'dropdown-item';
        item.href = '#';
        item.innerHTML = `
            <strong>${airport.code}</strong> - ${airport.name}
            <br><small class="text-muted">${airport.city}</small>
        `;
        
        item.addEventListener('click', function(e) {
            e.preventDefault();
            input.value = airport.code;
            hideAirportSuggestions(input);
        });
        
        dropdown.appendChild(item);
    });
    
    return dropdown;
}

function showDropdown(input, dropdown) {
    hideAirportSuggestions(input);
    input.parentNode.appendChild(dropdown);
}

function hideAirportSuggestions(input) {
    const existing = input.parentNode.querySelector('.airport-suggestions');
    if (existing) {
        existing.remove();
    }
}

// Initialize search suggestions
document.addEventListener('DOMContentLoaded', function() {
    initSearchSuggestions();
});
