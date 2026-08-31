// Network setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const networkForm = document.getElementById('network-form');
    const backendSelect = document.getElementById('output-backend');

    // Only the active backend's own connection fields are shown; the others
    // stay in the form (and keep their stored values) but out of the way.
    function showActiveBackendSettings() {
        document.querySelectorAll('.backend-settings').forEach(section => {
            const isActive = section.id === `settings-${backendSelect.value}`;
            section.style.display = isActive ? '' : 'none';
        });
    }

    backendSelect.addEventListener('change', showActiveBackendSettings);
    showActiveBackendSettings();

    networkForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const backend = backendSelect.value;

        // Both backends' settings are sent so switching away and back does
        // not discard the one not currently selected.
        const formData = {
            backend: backend,
            artnet: {
                ip: document.getElementById('artnet-ip').value,
                port: parseInt(document.getElementById('artnet-port').value, 10),
                universe: parseInt(document.getElementById('artnet-universe').value, 10)
            },
            enttec_usb: {
                port: document.getElementById('enttec-port').value
            },
            refresh_rate: parseInt(document.getElementById('refresh-rate').value, 10)
        };

        // Only the backend being made active has to be fully filled in;
        // the server enforces the same rule.
        if (backend === 'artnet' && !formData.artnet.ip.trim()) {
            alert('Art-Net IP address is required');
            return;
        }
        if (backend === 'enttec_usb' && !formData.enttec_usb.port.trim()) {
            alert('A serial port is required to use the Enttec DMX USB Pro');
            return;
        }

        saveNetworkSettings(formData);
    });

    function saveNetworkSettings(data) {
        const submitBtn = networkForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

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
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
});
