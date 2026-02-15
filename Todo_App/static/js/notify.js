function showFlash(message, type = 'success', duration = 3000) {
    const container = document.getElementById('flash-container');

    let title = '';
    switch (type) {
        case 'success': title = 'Success!'; break;
        case 'danger': title = 'Error!'; break;
        case 'warning': title = 'Warning!'; break;
        case 'info': title = 'Info'; break;
        default: title = '';
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show shadow`;
    alert.role = 'alert';
    alert.style.minWidth = '250px';
    alert.style.borderRadius = '8px';
    alert.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    alert.innerHTML = `
        <strong>${title}</strong> ${message}
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;

    alert.querySelector('button').addEventListener('click', () => {
        alert.classList.remove('show');
        alert.classList.add('hide');
        setTimeout(() => alert.remove(), 500);
    });

    container.appendChild(alert);

    alert.classList.add('show');
    alert.style.transition = 'all 0.5s ease';

    setTimeout(() => {
        alert.classList.remove('show');
        alert.classList.add('hide');
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => alert.remove(), 500);
    }, duration);
}

document.addEventListener('DOMContentLoaded', () => {
   
    const flashItems = document.querySelectorAll('.flash-item');

    flashItems.forEach(item => {
        const msg = item.getAttribute('data-message');
        const cat = item.getAttribute('data-category');

        if (typeof showFlash === 'function') {
            showFlash(msg, cat);
        } else {
            console.error("showFlash function is not defined!");
        }
    });

    const container = document.getElementById('flash-data');
    if (container) container.remove();
});
// Usage examples:
// showFlash("Todo created successfully!", "success");
// showFlash("An error occurred!", "danger", 5000);