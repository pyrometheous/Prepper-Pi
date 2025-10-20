// Custom Prepper Pi Homepage JavaScript

// Add WiFi info banner to the top of the page
function addWiFiInfoBanner() {
    const banner = document.createElement('div');
    banner.className = 'wifi-info-banner';
    banner.innerHTML = `
        <h2>📡 Prepper Pi Network</h2>
        <div class="wifi-details">
            <div class="wifi-ssid" id="wifi-ssid">SSID: Prepper Pi</div>
            <div class="wifi-password" id="wifi-password">Password: ChangeMeNow!</div>
        </div>
        <div style="margin-top: 10px; font-size: 14px; opacity: 0.9;">
            <span class="wifi-pulse">🔒</span> WPA2-PSK Secured Network
        </div>
    `;
    
    // Insert at the top of the main content area
    const mainContent = document.querySelector('[class*="page"]') || document.body.firstChild;
    if (mainContent && mainContent.parentNode) {
        mainContent.parentNode.insertBefore(banner, mainContent);
    }
}

// Fetch WiFi credentials from RaspAP API (if available)
async function fetchWiFiCredentials() {
    try {
        // Try to fetch from RaspAP's hostapd configuration
        const response = await fetch('/api/system/wifi-info');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('wifi-ssid').textContent = `SSID: ${data.ssid || 'Prepper Pi'}`;
            document.getElementById('wifi-password').textContent = `Password: ${data.password || 'ChangeMeNow!'}`;
        }
    } catch (error) {
        // If API not available, keep default values
        console.log('Using default WiFi credentials');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addWiFiInfoBanner();
        fetchWiFiCredentials();
    });
} else {
    addWiFiInfoBanner();
    fetchWiFiCredentials();
}

// Refresh WiFi info every 5 minutes
setInterval(fetchWiFiCredentials, 300000);
