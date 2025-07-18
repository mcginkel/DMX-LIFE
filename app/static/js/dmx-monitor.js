// DMX Channel Monitor - Visualizes all 512 DMX channel values
// This script creates a visual representation of DMX values
// Optimized for performance with batched DOM updates and throttled API calls

let dmxMonitorInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    // Get screen info
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    
    // Check if this is a large screen (iPad+) - min-width 768px is commonly used for tablets
    const isLargeScreen = window.matchMedia('(min-width: 768px)').matches;
    const monitorContainer = document.querySelector('.dmx-monitor-container');
    const showMonitorBtn = document.getElementById('showMonitorBtn');
    const hideMonitorBtn = document.getElementById('hideMonitorBtn');
    const showMonitorContainer = document.querySelector('.show-monitor-container');
    
    // Set up button event listeners
    if (showMonitorBtn) {
        showMonitorBtn.addEventListener('click', function() {
            showDmxMonitor();
        });
    }
    
    if (hideMonitorBtn) {
        hideMonitorBtn.addEventListener('click', function() {
            hideDmxMonitor();
        });
    }
    
    // Function to show the DMX monitor
    function showDmxMonitor() {
        if (monitorContainer && showMonitorContainer) {
            // Hide the show button and show the monitor
            showMonitorContainer.style.display = 'none';
            monitorContainer.style.display = 'block';
            
            // Initialize the monitor if not already done
            if (!dmxMonitorInstance) {
                try {
                    dmxMonitorInstance = initDmxMonitor();
                } catch (error) {
                    console.error('Error initializing DMX monitor:', error);
                }
            }
        }
    }
    
    // Function to hide the DMX monitor
    function hideDmxMonitor() {
        if (monitorContainer && showMonitorContainer) {
            // Show the show button and hide the monitor
            const isLargeScreenNow = window.matchMedia('(min-width: 768px)').matches;
            if (isLargeScreenNow) {
                showMonitorContainer.style.display = 'block';
            }
            monitorContainer.style.display = 'none';
            
            // Stop the monitor polling if it exists
            if (dmxMonitorInstance && dmxMonitorInstance.cleanup) {
                dmxMonitorInstance.cleanup();
                dmxMonitorInstance = null;
            }
        }
    }
    
    // Add resize listener to manage button visibility
    window.addEventListener('resize', function() {
        const isLargeScreenNow = window.matchMedia('(min-width: 768px)').matches;
        
        if (showMonitorContainer) {
            if (isLargeScreenNow) {
                // Only show the button if monitor is not currently visible
                if (!monitorContainer || monitorContainer.style.display === 'none') {
                    showMonitorContainer.style.display = 'block';
                }
            } else {
                // Hide both button and monitor on small screens
                showMonitorContainer.style.display = 'none';
                if (monitorContainer) {
                    monitorContainer.style.display = 'none';
                }
                // Stop monitor if running
                if (dmxMonitorInstance && dmxMonitorInstance.cleanup) {
                    dmxMonitorInstance.cleanup();
                    dmxMonitorInstance = null;
                }
            }
        }
    });
});

function initDmxMonitor() {
    console.log('Initializing DMX Monitor to show active channels only');
    
    const monitorElement = document.getElementById('dmxMonitor');
    if (!monitorElement) {
        console.error('DMX Monitor element not found');
        return null;
    }
    const activeSceneElement = document.getElementById('active_scene');
    // Clear any existing content
    monitorElement.innerHTML = '<div class="dmx-loading">Loading channel data...</div>';
    
    let dmxValues = new Array(512).fill(0);
    let dmxBars = [];
    let updateQueue = [];
    let updatePending = false;
    
    console.log('Creating DMX channel bars...');
    
    // Create all 512 channel bars
    createChannelBars();
    
    console.log('Starting DMX polling...');
    
    // Start the polling at 1fps (1000ms)
    const pollInterval = setInterval(fetchDmxValues, 1000);
    
    // Cleanup function
    function cleanup() {
        console.log('Cleaning up DMX monitor...');
        clearInterval(pollInterval);
        // Clear the monitor content
        if (monitorElement) {
            monitorElement.innerHTML = '<div class="dmx-loading">Loading channel data...</div>';
        }
        // Reset state
        dmxBars = [];
        updateQueue = [];
        updatePending = false;
    }
    
    // Set up cleanup when page is unloaded
    window.addEventListener('beforeunload', cleanup);
    
    // Create the channel visualization bars
    function createChannelBars() {
        // Use document fragment for better performance
        const fragment = document.createDocumentFragment();
        monitorElement.innerHTML = ''; // Clear loading message
        
        // Create a legend for the channels
        const legend = document.createElement('div');
        legend.className = 'dmx-legend';
        legend.innerHTML = '<span>Channel</span><span>Value</span>';
        fragment.appendChild(legend);
        
        monitorElement.appendChild(fragment);
        
        // We'll create channel bars on demand as they become active
        ensureChannelBarsExist(0);
    }
    
    // Ensure channel bars exist up to the specified index
    function ensureChannelBarsExist(highestActiveChannel) {
        // Use document fragment for better performance
        const fragment = document.createDocumentFragment();
        
        // Calculate the range of channels
        const startChannel = 0;
        const endChannel = Math.min(512, highestActiveChannel + 1);
        
        // Create channels if needed
        for (let i = startChannel; i < endChannel; i++) {
            const channelNum = i + 1; // DMX channels are 1-based
            
            // Skip if we already have this channel
            if (dmxBars[i] && dmxBars[i].container) {
                continue;
            }
            
            // Create container for this channel
            const channelContainer = document.createElement('div');
            channelContainer.className = 'dmx-monitor-channel';
            channelContainer.setAttribute('data-channel', channelNum);
            
            // Channel label
            const channelLabel = document.createElement('div');
            channelLabel.className = 'dmx-channel-label';
            channelLabel.textContent = channelNum;
            
            // Bar container and value bar
            const barContainer = document.createElement('div');
            barContainer.className = 'dmx-bar-container';
            
            const valueBar = document.createElement('div');
            valueBar.className = 'dmx-value-bar';
            valueBar.style.width = '0%';
            
            // Value display
            const valueDisplay = document.createElement('div');
            valueDisplay.className = 'dmx-value-display';
            valueDisplay.textContent = '0';
            
            // Add everything to the DOM
            barContainer.appendChild(valueBar);
            channelContainer.appendChild(channelLabel);
            channelContainer.appendChild(barContainer);
            channelContainer.appendChild(valueDisplay);
            fragment.appendChild(channelContainer);
            
            // Store reference to elements we'll update
            dmxBars[i] = {
                bar: valueBar,
                display: valueDisplay,
                container: channelContainer
            };
        }
        
        // Add all new elements to the DOM at once
        if (fragment.childNodes.length > 0) {
            monitorElement.appendChild(fragment);
        }
    }
    
    // Fetch current DMX values from API
    function fetchDmxValues() {
        // Add loading class to monitor
        //monitorElement.classList.add('loading');
        
        fetch('/api/dmx/values')
            .then(response => response.json())
            .then(data => {
                if (data.values && Array.isArray(data.values)) {                    
                    // Find the highest channel with a non-zero value
                    let highestActive = 0;
                    for (let i = data.values.length - 1; i >= 0; i--) {
                        if (data.values[i] > 0) {
                            highestActive = i;
                            break;
                        }
                    }
                    
                    // Check if we need to create channel bars based on the highest active channel
                    ensureChannelBarsExist(highestActive);
                    
                    updateDmxVisualizer(data.values);
                    
                    activeSceneElement.textContent = data.active_scene || 'None';
                    // Remove loading class after first successful load
                    monitorElement.classList.remove('loading');
                }
            })
            .catch(error => {
                console.error('Error fetching DMX values:', error);
                // Show error state in monitor
                monitorElement.classList.add('error');
                setTimeout(() => {
                    monitorElement.classList.remove('error');
                }, 2000);
            });
    }
    
    // Update the visualizer with new values using batched updates
    function updateDmxVisualizer(values) {
        // Clear update queue
        updateQueue = [];
        
        // Check each channel value and queue updates only for changed values
        for (let i = 0; i < Math.min(values.length, 512); i++) {
            const newValue = values[i] || 0;
            
            // Only update if the value has changed
            if (dmxValues[i] !== newValue) {
                updateQueue.push({
                    index: i,
                    value: newValue
                });
                
                // Update stored value
                dmxValues[i] = newValue;
            }
        }
        
        // If there are updates, schedule them
        if (updateQueue.length > 0 && !updatePending) {
            updatePending = true;
            requestAnimationFrame(processBatchedUpdates);
        }
    }
    
    // Process batched DOM updates for better performance
    function processBatchedUpdates() {
        // Process in batches of 32 for smoother rendering
        const batchSize = 32;
        const currentBatch = updateQueue.splice(0, batchSize);
        
        // Apply the updates
        currentBatch.forEach(update => {
            const i = update.index;
            const value = update.value;
            const percentage = (value / 255) * 100;
            
            // Make sure we have a reference to the elements
            if (dmxBars[i] && dmxBars[i].bar && dmxBars[i].display) {
                dmxBars[i].bar.style.width = percentage + '%';
                dmxBars[i].display.textContent = value;
                
                // Show/hide based on activity (always using 'active' view mode)
                if (dmxBars[i].container) {
                    // Toggle both active class and visibility
                    dmxBars[i].container.classList.toggle('active', value > 0);
                    //dmxBars[i].container.style.display = value > 0 ? '' : 'none';
                }
            }
        });
        
        // If there are more updates, schedule the next batch
        if (updateQueue.length > 0) {
            requestAnimationFrame(processBatchedUpdates);
        } else {
            updatePending = false;
        }
    }
    
    // Return object with cleanup method
    return {
        cleanup: cleanup
    };
}
