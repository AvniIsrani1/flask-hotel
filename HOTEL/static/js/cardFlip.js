// Wait for the DOM to fully load
document.addEventListener('DOMContentLoaded', function() {
    // Find all menu items on the page
    const menuItems = document.querySelectorAll('.menu-item');

    // Add click event to each menu item
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Toggle the 'flipped' class
            this.classList.toggle('flipped');
        });
    });
});