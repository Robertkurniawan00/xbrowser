// XBrowser Real High-Performance Universal Dark Mode Engine
(function() {
    'use strict';
    function applyDarkMode() {
        if (!document.documentElement) return;
        document.documentElement.setAttribute('data-theme', 'dark');
        document.documentElement.setAttribute('data-color-mode', 'dark');
        document.documentElement.style.colorScheme = 'dark';
        
        // Ensure body background is dark
        if (document.body) {
            const bodyBg = window.getComputedStyle(document.body).backgroundColor;
            if (bodyBg === 'rgba(0, 0, 0, 0)' || bodyBg === 'rgb(255, 255, 255)' || bodyBg === 'white') {
                document.body.style.backgroundColor = '#12161f';
                document.body.style.color = '#e2e8f0';
            }
        }

        // Apply dark styling to bright containers
        const nodes = document.querySelectorAll('div, section, article, header, nav, footer, main');
        for (let i = 0; i < Math.min(nodes.length, 300); i++) {
            const el = nodes[i];
            const bg = el.style.backgroundColor;
            if (bg && (bg === 'white' || bg === '#fff' || bg === '#ffffff' || bg.indexOf('255, 255, 255') !== -1)) {
                el.style.backgroundColor = '#182030';
                el.style.color = '#f1f5f9';
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyDarkMode);
    } else {
        applyDarkMode();
    }
})();
