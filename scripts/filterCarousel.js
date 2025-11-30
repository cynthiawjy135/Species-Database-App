// Filter Carousel Functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterCarousel = document.getElementById('filter-carousel');
    const filterButtons = filterCarousel.querySelectorAll('.filter-button');
    let activeButton = null;

    // Initialize: Set first button as active by default
    if (filterButtons.length > 0) {
        filterButtons[0].classList.add('active');
        activeButton = filterButtons[0];
    }

    // Handle button clicks
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active state from previously active button
            if (activeButton && activeButton !== this) {
                activeButton.classList.remove('active');
            }

            // Add active state to clicked button
            this.classList.add('active');
            activeButton = this;

            // Get the filter type
            const filterType = this.getAttribute('data-filter');
            console.log('Filter selected:', filterType);

            // TODO: Next week - implement actual filtering logic here
            // For now, this is just the UI placeholder
        });
    });

    // Enhanced carousel scrolling with momentum
    let isScrolling = false;
    let scrollTimeout;

    filterCarousel.addEventListener('scroll', function() {
        if (!isScrolling) {
            isScrolling = true;
        }
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            isScrolling = false;
        }, 150);
    });

    // Optional: Auto-scroll to center active button on mobile
    function scrollToActiveButton() {
        if (activeButton) {
            const carouselRect = filterCarousel.getBoundingClientRect();
            const buttonRect = activeButton.getBoundingClientRect();
            const scrollLeft = filterCarousel.scrollLeft;
            const buttonLeft = buttonRect.left - carouselRect.left + scrollLeft;
            const buttonWidth = buttonRect.width;
            const carouselWidth = carouselRect.width;
            const targetScroll = buttonLeft - (carouselWidth / 2) + (buttonWidth / 2);

            filterCarousel.scrollTo({
                left: targetScroll,
                behavior: 'smooth'
            });
        }
    }

    // Update scroll position when a button is clicked (optional enhancement)
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            setTimeout(scrollToActiveButton, 100);
        });
    });
});
