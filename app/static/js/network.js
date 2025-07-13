// DMX Interface setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get interface selection elements
    const interfaceRadios = document.querySelectorAll('input[name="interface_type"]');
    const artnetConfig = document.getElementById('artnet-config');
    const usbConfig = document.getElementById('usb-config');
    const saveButton = document.getElementById('save-settings');
    const testButton = document.getElementById('test-connection');
    const refreshPortsButton = document.getElementById('refresh-ports');
    const usbPortSelect = document.getElementById('usb-port');
    
    // Interface type change handler
    interfaceRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'artnet') {
                artnetConfig.style.display = 'block';
                usbConfig.style.display = 'none';
            } else if (this.value === 'usb_dmx') {
                artnetConfig.style.display = 'none';
                usbConfig.style.display = 'block';
                loadUSBPorts(); // Load ports when switching to USB
            }
        });
    });
    
    // Save settings handler
    saveButton.addEventListener('click', function() {
        const selectedInterface = document.querySelector('input[name="interface_type"]:checked').value;
        
        if (selectedInterface === 'artnet') {
            saveArtNetSettings();
        } else if (selectedInterface === 'usb_dmx') {
            saveUSBSettings();
        }
    });
    
    // Test connection handler
    testButton.addEventListener('click', function() {
        testConnection();
    });
    
    // Refresh USB ports handler
    refreshPortsButton.addEventListener('click', function() {
        loadUSBPorts();
    });
    
    // Load USB ports on page load if USB interface is selected
    if (document.querySelector('input[name="interface_type"]:checked').value === 'usb_dmx') {
        loadUSBPorts();
    }
    
    // Function to save Art-Net settings
    function saveArtNetSettings() {
        const data = {
            artnet_ip: document.getElementById('artnet-ip').value,
            artnet_port: parseInt(document.getElementById('artnet-port').value),
            universe: parseInt(document.getElementById('artnet-universe').value),
            refresh_rate: parseInt(document.getElementById('refresh-rate').value)
        };
        
        // Validate form data
        if (!data.artnet_ip) {
            alert('IP address is required');
            return;
        }
        
        saveNetworkSettings(data);
    }
    
    // Function to save USB-DMX settings
    function saveUSBSettings() {
        const data = {
            usb_port: document.getElementById('usb-port').value,
            usb_baud_rate: parseInt(document.getElementById('usb-baud-rate').value),
            usb_data_bits: parseInt(document.getElementById('usb-data-bits').value),
            usb_stop_bits: parseInt(document.getElementById('usb-stop-bits').value),
            usb_parity: document.getElementById('usb-parity').value,
            usb_timeout: parseFloat(document.getElementById('usb-timeout').value)
        };
        
        saveNetworkSettings(data);
    }
    
    // Function to save network settings
    function saveNetworkSettings(data) {
        // Show loading state
        const originalText = saveButton.textContent;
        saveButton.textContent = 'Saving...';
        saveButton.disabled = true;
        
        // Include interface type switch if it has changed
        const selectedInterface = document.querySelector('input[name="interface_type"]:checked').value;
        const currentInterface = document.getElementById('current-interface').textContent.toLowerCase();
        
        if (selectedInterface !== currentInterface) {
            // Switch interface type first
            switchInterface(selectedInterface, data);
        } else {
            // Just update configuration
            updateConfiguration(data);
        }
    }
    
    // Function to switch interface type
    function switchInterface(interfaceType, config) {
        fetch('/setup/api/interface/switch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                interface_type: interfaceType,
                config: config
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Interface switched and settings saved successfully!');
                updateInterfaceStatus(data.status);
            } else {
                alert('Failed to switch interface: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error switching interface:', error);
            alert('Error switching interface. See console for details.');
        })
        .finally(() => {
            // Reset button state
            saveButton.textContent = 'Save Settings';
            saveButton.disabled = false;
        });
    }
    
    // Function to update configuration
    function updateConfiguration(data) {
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
                alert('Settings saved successfully!');
                if (data.status) {
                    updateInterfaceStatus(data.status);
                }
            } else {
                alert('Failed to save settings: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error saving settings:', error);
            alert('Error saving settings. See console for details.');
        })
        .finally(() => {
            // Reset button state
            saveButton.textContent = 'Save Settings';
            saveButton.disabled = false;
        });
    }
    
    // Function to test connection
    function testConnection() {
        const originalText = testButton.textContent;
        testButton.textContent = 'Testing...';
        testButton.disabled = true;
        
        fetch('/setup/api/interface/status')
        .then(response => response.json())
        .then(data => {
            updateInterfaceStatus(data);
            
            if (data.is_available) {
                alert('Connection test successful!');
            } else {
                alert('Connection test failed. Check your settings and connections.');
            }
        })
        .catch(error => {
            console.error('Error testing connection:', error);
            alert('Error testing connection. See console for details.');
        })
        .finally(() => {
            testButton.textContent = originalText;
            testButton.disabled = false;
        });
    }
    
    // Function to load USB ports
    function loadUSBPorts() {
        const originalText = refreshPortsButton.textContent;
        refreshPortsButton.textContent = 'Loading...';
        refreshPortsButton.disabled = true;
        
        fetch('/setup/api/interface/usb-ports')
        .then(response => response.json())
        .then(data => {
            // Clear existing options (except auto)
            while (usbPortSelect.children.length > 1) {
                usbPortSelect.removeChild(usbPortSelect.lastChild);
            }
            
            if (data.error) {
                console.warn('USB port detection error:', data.error);
                return;
            }
            
            // Add available ports
            data.ports.forEach(port => {
                const option = document.createElement('option');
                option.value = port.device;
                option.textContent = `${port.device} - ${port.description}`;
                
                // Mark DMX devices
                if (port.is_dmx_device) {
                    option.textContent += ' (DMX Device)';
                    option.style.fontWeight = 'bold';
                }
                
                usbPortSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading USB ports:', error);
        })
        .finally(() => {
            refreshPortsButton.textContent = originalText;
            refreshPortsButton.disabled = false;
        });
    }
    
    // Function to update interface status display
    function updateInterfaceStatus(status) {
        const currentInterface = document.getElementById('current-interface');
        const interfaceStatus = document.getElementById('interface-status');
        
        currentInterface.textContent = status.type.charAt(0).toUpperCase() + status.type.slice(1);
        interfaceStatus.textContent = status.is_started ? 'Active' : 'Inactive';
        interfaceStatus.className = 'status-' + (status.is_started ? 'active' : 'inactive');
    }
});
