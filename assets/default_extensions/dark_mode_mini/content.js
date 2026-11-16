// XBrowser Native Dark Mode Engine
(function() {
    'use strict';
    try {
        if (document.documentElement) {
            document.documentElement.style.colorScheme = 'dark';
        }
    } catch(e) {}
})();
