/**
 * Toast Notification System
 */

const toast = {
    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - The type of toast (success, error, info, warning)
     * @param {number} duration - How long to show the toast in milliseconds (default: 5000)
     */
    show: function (message, type = 'info', duration = 5000) {
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        // Create toast element
        const toastEl = document.createElement('div');
        toastEl.className = `toast toast-${type}`;

        // Determine icon based on type
        let iconName = 'info';
        if (type === 'success') iconName = 'check-circle';
        else if (type === 'error') iconName = 'x-circle';
        else if (type === 'warning') iconName = 'alert-triangle';

        // Build toast HTML
        toastEl.innerHTML = `
            <div class="toast-icon">
                <i data-lucide="${iconName}"></i>
            </div>
            <div class="toast-content">
                <p class="toast-message">${message}</p>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        `;

        // Add to container
        container.appendChild(toastEl);

        // Initialize Lucide icons for the toast
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Show toast with animation
        setTimeout(() => {
            toastEl.classList.add('toast-show');
        }, 10);

        // Auto-remove after duration
        setTimeout(() => {
            toastEl.classList.remove('toast-show');
            toastEl.classList.add('toast-hide');
            setTimeout(() => {
                toastEl.remove();
            }, 300);
        }, duration);
    },

    /**
     * Show a success toast
     * @param {string} message - The message to display
     * @param {number} duration - How long to show the toast in milliseconds
     */
    success: function (message, duration = 5000) {
        this.show(message, 'success', duration);
    },

    /**
     * Show an error toast
     * @param {string} message - The message to display
     * @param {number} duration - How long to show the toast in milliseconds
     */
    error: function (message, duration = 5000) {
        this.show(message, 'error', duration);
    },

    /**
     * Show an info toast
     * @param {string} message - The message to display
     * @param {number} duration - How long to show the toast in milliseconds
     */
    info: function (message, duration = 5000) {
        this.show(message, 'info', duration);
    },

    /**
     * Show a warning toast
     * @param {string} message - The message to display
     * @param {number} duration - How long to show the toast in milliseconds
     */
    warning: function (message, duration = 5000) {
        this.show(message, 'warning', duration);
    }
};
