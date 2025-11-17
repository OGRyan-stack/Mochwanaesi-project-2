/**
 * Announcements filtering functionality
 */

// Store all announcements for filtering
let allAnnouncements = [];

// Filter announcements by category
function filterAnnouncements(category) {
    const startTime = performance.now();

    const announcementCards = document.querySelectorAll('.announcement-card');

    announcementCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');

        if (category === 'all' || cardCategory === category) {
            card.style.display = '';
            // Add fade-in animation
            card.classList.remove('hidden');
            card.classList.add('fade-in');
        } else {
            card.style.display = 'none';
            card.classList.add('hidden');
            card.classList.remove('fade-in');
        }
    });

    const endTime = performance.now();
    const duration = endTime - startTime;

    // Log performance (should be under 300ms as per requirements)
    console.log(`Filtering completed in ${duration.toFixed(2)}ms`);

    // Update empty state message
    updateEmptyState(category);
}

// Update active filter button styling
function setActiveFilter(button) {
    // Remove active class from all filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });

    // Add active class to clicked button
    button.classList.add('active');
    button.setAttribute('aria-pressed', 'true');
}

// Update empty state message when no announcements match filter
function updateEmptyState(category) {
    const visibleCards = document.querySelectorAll('.announcement-card:not(.hidden)');
    let emptyState = document.getElementById('empty-state');

    if (visibleCards.length === 0) {
        // Create empty state if it doesn't exist
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.id = 'empty-state';
            emptyState.className = 'empty-state';

            const announcementsList = document.getElementById('announcements-list');
            if (announcementsList) {
                announcementsList.appendChild(emptyState);
            }
        }

        const categoryName = category === 'all' ? 'this category' : category;
        emptyState.innerHTML = `
            <div class="empty-state-content">
                <i data-lucide="inbox" class="empty-state-icon"></i>
                <h3>No announcements found</h3>
                <p>There are no announcements in ${categoryName} at the moment.</p>
            </div>
        `;
        emptyState.style.display = 'block';

        // Re-initialize Lucide icons if available
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    } else {
        // Hide empty state if announcements are visible
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
}

// Initialize announcements filtering when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get all filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');

    // Add click event listeners to filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            const category = this.getAttribute('data-category');

            // Update active filter button
            setActiveFilter(this);

            // Filter announcements
            filterAnnouncements(category);
        });
    });

    // Store all announcement cards for reference
    const announcementCards = document.querySelectorAll('.announcement-card');
    allAnnouncements = Array.from(announcementCards);

    // Set initial active filter (should be "all")
    const activeButton = document.querySelector('.filter-btn.active');
    if (!activeButton && filterButtons.length > 0) {
        setActiveFilter(filterButtons[0]);
    }

    // Initialize with all announcements visible
    filterAnnouncements('all');
});

// Export functions for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        filterAnnouncements,
        setActiveFilter
    };
}
