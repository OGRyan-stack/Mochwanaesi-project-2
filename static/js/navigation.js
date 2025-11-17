/**
 * Navigation functionality for mobile menu
 */

// Toggle mobile menu visibility
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenu) {
        mobileMenu.classList.toggle('active');
    }
}

// Close mobile menu (used when navigation links are clicked)
function closeMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenu && mobileMenu.classList.contains('active')) {
        mobileMenu.classList.remove('active');
    }
}

// Initialize navigation functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Close mobile menu when clicking outside
    document.addEventListener('click', function (event) {
        const mobileMenu = document.getElementById('mobileMenu');
        const hamburger = document.querySelector('.mobile-menu-toggle');

        if (mobileMenu && hamburger) {
            const isClickInsideMenu = mobileMenu.contains(event.target);
            const isClickOnHamburger = hamburger.contains(event.target);

            if (!isClickInsideMenu && !isClickOnHamburger && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        }
    });

    // Close mobile menu on window resize to desktop size
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 768) {
            closeMobileMenu();
        }
    });
});
