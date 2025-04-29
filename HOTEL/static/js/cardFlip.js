
function enableCardFlip(selector) {
    // Wait for the DOM to fully load
    document.addEventListener('DOMContentLoaded', function() {
        const items = document.querySelectorAll(selector);
        // Add click event to each menu item
        items.forEach(item => {
            item.addEventListener('click', function() {
            // Toggle the 'flipped' class
            this.classList.toggle('flipped');
        });
      });
    });
  }
  
  // Call it for menu items
  enableCardFlip('.menu-item');
  
  /* examples of calling flipped 
  enableCardFlip('.profile-card');
  enableCardFlip('.event-card');
  */