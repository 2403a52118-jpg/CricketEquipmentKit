// Form validation
document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", function(event) {
        if (!this.checkValidity()) {
            event.preventDefault();
            alert("Please enter valid details!");
        }
    });
});

// Auto-hide alert notifications after 4 seconds
window.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "opacity 0.6s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 600);
            });
        }, 4000);
    }
});
