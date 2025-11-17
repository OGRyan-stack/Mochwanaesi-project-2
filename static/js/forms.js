/**
 * Form validation and submission functionality
 */

// Validate email format
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate South African phone format
// Accepts formats: 0123456789, +27123456789, 012 345 6789, 012-345-6789
function validatePhone(phone) {
    // Remove spaces and dashes
    const cleanPhone = phone.replace(/[\s-]/g, '');

    // Check for South African formats
    const saPhoneRegex = /^(\+27|0)[0-9]{9}$/;
    return saPhoneRegex.test(cleanPhone);
}

// Display inline error message for a field
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Add error styling to field
    field.classList.add('field-error');

    // Remove existing error message if any
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Create and insert error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

// Clear error message for a field
function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.remove('field-error');

    const errorMessage = field.parentElement.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Validate form data
function validateForm(formData) {
    let isValid = true;
    const errors = {};

    // Validate name
    if (!formData.name || formData.name.trim().length < 2) {
        errors.name = 'Name must be at least 2 characters long';
        showFieldError('name', errors.name);
        isValid = false;
    } else {
        clearFieldError('name');
    }

    // Validate email
    if (!formData.email || !validateEmail(formData.email)) {
        errors.email = 'Please enter a valid email address';
        showFieldError('email', errors.email);
        isValid = false;
    } else {
        clearFieldError('email');
    }

    // Validate phone
    if (!formData.phone || !validatePhone(formData.phone)) {
        errors.phone = 'Please enter a valid South African phone number';
        showFieldError('phone', errors.phone);
        isValid = false;
    } else {
        clearFieldError('phone');
    }

    // Validate subject
    if (!formData.subject || formData.subject.trim().length < 3) {
        errors.subject = 'Subject must be at least 3 characters long';
        showFieldError('subject', errors.subject);
        isValid = false;
    } else {
        clearFieldError('subject');
    }

    // Validate message
    if (!formData.message || formData.message.trim().length < 10) {
        errors.message = 'Message must be at least 10 characters long';
        showFieldError('message', errors.message);
        isValid = false;
    } else {
        clearFieldError('message');
    }

    return { isValid, errors };
}

// Show toast notification
function showToast(message, type = 'success') {
    if (typeof toast !== 'undefined') {
        if (type === 'success') {
            toast.success(message);
        } else if (type === 'error') {
            toast.error(message);
        } else {
            toast.show(message, type);
        }
    } else {
        // Fallback: create a simple alert-style notification
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

// Handle form submission
function submitForm(event) {
    event.preventDefault();

    const form = event.target;

    // Collect form data
    const formData = {
        name: form.name.value,
        email: form.email.value,
        phone: form.phone.value,
        subject: form.subject.value,
        message: form.message.value
    };

    // Validate form
    const validation = validateForm(formData);

    if (!validation.isValid) {
        showToast('Please fix the errors in the form', 'error');
        return;
    }

    // Simulate form submission (in production, this would send to backend)
    // For now, we'll just show success message and clear form
    setTimeout(() => {
        showToast('Thank you for your message! We will get back to you soon.', 'success');
        form.reset();

        // Clear any remaining error states
        const errorFields = form.querySelectorAll('.field-error');
        errorFields.forEach(field => {
            field.classList.remove('field-error');
        });

        const errorMessages = form.querySelectorAll('.error-message');
        errorMessages.forEach(msg => {
            msg.remove();
        });
    }, 500);
}

// Initialize form functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Add submit event listener to contact form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', submitForm);

        // Add real-time validation on blur
        const fields = ['name', 'email', 'phone', 'subject', 'message'];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', function () {
                    const formData = {
                        name: document.getElementById('name')?.value || '',
                        email: document.getElementById('email')?.value || '',
                        phone: document.getElementById('phone')?.value || '',
                        subject: document.getElementById('subject')?.value || '',
                        message: document.getElementById('message')?.value || ''
                    };
                    validateForm(formData);
                });
            }
        });
    }

    // Add submit event listener to newsletter forms
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const emailInput = form.querySelector('input[type="email"]');

            if (emailInput && validateEmail(emailInput.value)) {
                showToast('Thank you for subscribing to our newsletter!', 'success');
                form.reset();
            } else {
                showToast('Please enter a valid email address', 'error');
            }
        });
    });
});
