// Network setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get network form
    const networkForm = document.getElementById('network-form');
    
    // Add submit handler
    networkForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            artnet_ip: document.getElementById('artnet-ip').value,
            artnet_port: parseInt(document.getElementById('artnet-port').value),
            universe: parseInt(document.getElementById('artnet-universe').value),
            refresh_rate: parseInt(document.getElementById('refresh-rate').value)
        };
        
        // Validate form data
        if (!formData.artnet_ip) {
            alert('IP address is required');
            return;
        }
        
        // Send data to server
        saveNetworkSettings(formData);
    });
    
    // Function to save network settings
    function saveNetworkSettings(data) {
        // Show loading state
        const submitBtn = networkForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;
        
        // Call the API
        fetch('/setup/api/config/network', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                alert('Network settings saved successfully!');
            } else {
                alert('Failed to save network settings: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error saving network settings:', error);
            alert('Error saving network settings. See console for details.');
        })
        .finally(() => {
            // Reset button state
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
});
