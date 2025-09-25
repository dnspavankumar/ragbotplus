// Theme management
const THEME_STORAGE_KEY = 'app-theme-preference';
const DARK_THEME = 'dark';
const LIGHT_THEME = 'light';

// Function to set theme
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    
    // Update button icon if it exists
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
    if (themeToggleIcon) {
        themeToggleIcon.className = theme === DARK_THEME ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Function to toggle theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || DARK_THEME;
    const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    setTheme(newTheme);
}

// Initialize theme
function initializeTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || DARK_THEME;
    setTheme(savedTheme);
    
    // Add theme toggle button if it doesn't exist
    if (!document.getElementById('theme-toggle')) {
        const header = document.querySelector('.chat-header') || document.querySelector('header');
        if (header) {
            const themeToggle = document.createElement('button');
            themeToggle.id = 'theme-toggle';
            themeToggle.className = 'theme-toggle hover-scale';
            themeToggle.setAttribute('aria-label', 'Toggle theme');
            themeToggle.innerHTML = `<i id="theme-toggle-icon" class="${savedTheme === DARK_THEME ? 'fas fa-sun' : 'fas fa-moon'}"></i>`;
            themeToggle.onclick = toggleTheme;
            header.appendChild(themeToggle);
        }
    }
}

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const systemTheme = e.matches ? DARK_THEME : LIGHT_THEME;
    setTheme(systemTheme);
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeTheme);