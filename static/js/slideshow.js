/**
 * Hero Slideshow Functionality
 */

let currentSlide = 0;
let slideInterval;
const slides = document.querySelectorAll('.slide');
const indicators = document.querySelectorAll('.indicator');
const autoPlayDelay = 5000; // 5 seconds

/**
 * Show a specific slide
 * @param {number} index - The index of the slide to show
 */
function showSlide(index) {
    // Ensure index is within bounds
    if (index >= slides.length) {
        currentSlide = 0;
    } else if (index < 0) {
        currentSlide = slides.length - 1;
    } else {
        currentSlide = index;
    }

    // Hide all slides
    slides.forEach(slide => {
        slide.classList.remove('active');
    });

    // Remove active class from all indicators
    indicators.forEach(indicator => {
        indicator.classList.remove('active');
    });

    // Show current slide
    slides[currentSlide].classList.add('active');

    // Highlight current indicator
    if (indicators[currentSlide]) {
        indicators[currentSlide].classList.add('active');
    }
}

/**
 * Change slide by a given offset
 * @param {number} offset - The number of slides to move (positive or negative)
 */
function changeSlide(offset) {
    showSlide(currentSlide + offset);
    resetAutoPlay();
}

/**
 * Go to a specific slide
 * @param {number} index - The index of the slide to go to
 */
function goToSlide(index) {
    showSlide(index);
    resetAutoPlay();
}

/**
 * Automatically advance to the next slide
 */
function autoPlaySlides() {
    slideInterval = setInterval(() => {
        showSlide(currentSlide + 1);
    }, autoPlayDelay);
}

/**
 * Reset the auto-play timer
 */
function resetAutoPlay() {
    clearInterval(slideInterval);
    autoPlaySlides();
}

/**
 * Pause auto-play when user hovers over slideshow
 */
function pauseAutoPlay() {
    clearInterval(slideInterval);
}

/**
 * Resume auto-play when user stops hovering
 */
function resumeAutoPlay() {
    autoPlaySlides();
}

// Initialize slideshow when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Start auto-play
    if (slides.length > 0) {
        showSlide(0);
        autoPlaySlides();

        // Pause on hover
        const slideshowContainer = document.querySelector('.hero-slideshow');
        if (slideshowContainer) {
            slideshowContainer.addEventListener('mouseenter', pauseAutoPlay);
            slideshowContainer.addEventListener('mouseleave', resumeAutoPlay);
        }

        // Keyboard navigation
        document.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowLeft') {
                changeSlide(-1);
            } else if (event.key === 'ArrowRight') {
                changeSlide(1);
            }
        });

        // Touch/swipe support for mobile
        let touchStartX = 0;
        let touchEndX = 0;

        if (slideshowContainer) {
            slideshowContainer.addEventListener('touchstart', function (event) {
                touchStartX = event.changedTouches[0].screenX;
            });

            slideshowContainer.addEventListener('touchend', function (event) {
                touchEndX = event.changedTouches[0].screenX;
                handleSwipe();
            });
        }

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next slide
                    changeSlide(1);
                } else {
                    // Swipe right - previous slide
                    changeSlide(-1);
                }
            }
        }
    }
});

// Pause slideshow when page is not visible
document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
        pauseAutoPlay();
    } else {
        resumeAutoPlay();
    }
});
