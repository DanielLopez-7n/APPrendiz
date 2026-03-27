// JavaScript global del proyecto (Alertas + Sidebar + Menús)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Proyecto Django cargado correctamente');

    // =======================================================
    // 1. LÓGICA DE ALERTAS
    // =======================================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Si es bootstrap 5, usamos la API de instancia si es posible, o classes
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

    // En el panel administrativo avanzado (sidebar-smart), el toggle se maneja
    // dentro del template para soportar estados pinned/mobile.
    const usesSmartSidebar = sidebar && sidebar.classList.contains('sidebar-smart');

    if (sidebarToggle && sidebar && !usesSmartSidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            // Alternar clases para esconder/mostrar
            sidebar.classList.toggle('collapsed');
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
