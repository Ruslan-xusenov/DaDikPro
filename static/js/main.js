// Dadik Pro Global Scripts v1.1
console.log('Dadik Pro Platform Initialized');

// Global Language Dropdown Logic
window.toggleLangDropdown = function() {
    const dropdown = document.getElementById('langDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
        console.log('Language dropdown toggled');
    }
};

window.submitLang = function(val) {
    const form = document.getElementById('langForm');
    if (form) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'language';
        input.value = val;
        form.appendChild(input);
        form.submit();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Theme Logic
    const themeBtn = document.getElementById('themeBtn');
    const body = document.body;
    
    if (themeBtn) {
        if (localStorage.getItem('theme') === 'dark') {
            body.classList.add('dark');
            themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
        }

        themeBtn.addEventListener('click', () => {
            body.classList.toggle('dark');
            if (body.classList.contains('dark')) {
                localStorage.setItem('theme', 'dark');
                themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                localStorage.setItem('theme', 'light');
                themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }
        });
    }

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('langDropdown');
        const switcher = document.querySelector('.lang-switcher');
        if (dropdown && dropdown.classList.contains('show') && !dropdown.contains(e.target) && !switcher.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });

    // Mobile Menu Toggle
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
            body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : 'auto';
        });

        // Close menu when a link is clicked
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                body.style.overflow = 'auto';
            });
        });
    }

    // Mobile Sidebar Toggle (Dashboard)
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (toggle && sidebar) {
        if (window.innerWidth <= 1024) {
            toggle.style.display = 'block';
        }
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || targetId === '') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});