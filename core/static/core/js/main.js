// JavaScript global del proyecto
document.addEventListener('DOMContentLoaded', function() {
    console.log('Proyecto Django cargado correctamente');
    
    // Cerrar alertas automáticamente después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });
});