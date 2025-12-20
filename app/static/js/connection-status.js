// Connection status monitoring
// Can be included on any page that needs to show Art-Net connection status

document.addEventListener('DOMContentLoaded', function() {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    // Only initialize if the status elements exist on this page
    if (!statusIndicator || !statusText) {
        return;
    }
    
    function checkConnectionStatus() {
        fetch('/api/connection/status')
            .then(response => response.json())
            .then(data => {
                if (data.connected) {
                    statusIndicator.className = 'status-indicator connected';
                    statusText.textContent = 'Art-Net Connected';
                } else {
                    statusIndicator.className = 'status-indicator disconnected';
                    statusText.textContent = 'Art-Net Host Down';
                }
            })
            .catch(error => {
                console.error('Error checking connection status:', error);
                statusIndicator.className = 'status-indicator disconnected';
                statusText.textContent = 'Connection Status Unknown';
            });
    }
    
    // Check connection status immediately and then every 5 seconds
    checkConnectionStatus();
    setInterval(checkConnectionStatus, 5000);
});
