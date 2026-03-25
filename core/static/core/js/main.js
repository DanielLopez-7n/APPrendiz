// JavaScript global del proyecto (Alertas + Sidebar + Menús)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Proyecto Django cargado correctamente');

    // =======================================================
    // 1. LÓGICA DE ALERTAS
    // =======================================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // =======================================================
    // 2. LÓGICA DEL SIDEBAR (Menú Lateral)
    // =======================================================
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            // Alternar clase para esconder/mostrar en escritorio
            sidebar.classList.toggle('collapsed');
            
            // AGREGADO: Alternar clase para mostrar en teléfonos
            sidebar.classList.toggle('show'); 
            
            if (mainContent) {
                mainContent.classList.toggle('expanded');
            }
        });
    }

    // =======================================================
    // 3. INICIALIZACIÓN DE DROPDOWNS (Menú de Usuario)
    // =======================================================
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
});