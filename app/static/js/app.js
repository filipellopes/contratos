document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    const toggle = document.getElementById("sidebar-toggle");

    function closeSidebar() {
        sidebar?.classList.remove("open");
        overlay?.classList.remove("open");
    }

    function openSidebar() {
        sidebar?.classList.add("open");
        overlay?.classList.add("open");
    }

    toggle?.addEventListener("click", () => {
        if (sidebar?.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay?.addEventListener("click", closeSidebar);

    sidebar?.querySelectorAll(".sidebar-link").forEach((link) => {
        link.addEventListener("click", () => {
            if (window.innerWidth < 992) closeSidebar();
        });
    });
});
