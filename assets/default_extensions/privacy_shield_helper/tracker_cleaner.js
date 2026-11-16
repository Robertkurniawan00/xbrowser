// XBrowser Privacy Shield Helper - Real-Time Tracker Sanitizer
(function() {
    'use strict';
    const trackingParams = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id',
        'fbclid', 'gclid', 'gclsrc', 'dclid', 'msclkid', 'twclid', 'zanpid',
        'igshid', '_hsenc', '_hsmi', 'mc_cid', 'mc_eid', 'vero_id', 'yclid'
    ];
    
    function sanitizeUrl() {
        try {
            const url = new URL(window.location.href);
            let modified = false;
            trackingParams.forEach(p => {
                if (url.searchParams.has(p)) {
                    url.searchParams.delete(p);
                    modified = true;
                }
            });
            if (modified) {
                window.history.replaceState({}, document.title, url.toString());
            }
        } catch(e) {}
    }

    function removeTrackingElements() {
        // Remove common hidden tracker beacons and telemetry elements
        const selectors = [
            'iframe[src*="doubleclick.net"]',
            'iframe[src*="googletagmanager.com"]',
            'iframe[src*="adnxs.com"]',
            'img[width="1"][height="1"]',
            'img[width="0"][height="0"]'
        ];
        try {
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });
        } catch(e) {}
    }

    sanitizeUrl();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeTrackingElements);
    } else {
        removeTrackingElements();
    }
})();
