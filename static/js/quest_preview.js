document.addEventListener('DOMContentLoaded', () => {
    const dropdowns = document.querySelectorAll('.dropdown-wrapper');

    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');

        // Toggle dropdown
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other dropdowns first
            dropdowns.forEach(d => {
                if (d !== dropdown) d.querySelector('.dropdown-menu').classList.remove('show');
            });
            menu.classList.toggle('show');
        });

        // Handle item selection
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                trigger.textContent = item.textContent + ' ▾';
                trigger.style.color = '#333'; // Active color
                menu.classList.remove('show');
                // You can store the value somewhere if needed, e.g. dropdown.dataset.value = item.dataset.value;
            });
        });
    });

    // Close when clicking outside
    document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
            dropdown.querySelector('.dropdown-menu').classList.remove('show');
        });
    });
});
