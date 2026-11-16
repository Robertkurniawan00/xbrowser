(function() {
    // Strip common tracking query params
    const trackingParams = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid', 'msclkid'];
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
        console.log('[Privacy Shield Helper] Parameter pelacak berhasil dibersihkan dari URL!');
    }
})();