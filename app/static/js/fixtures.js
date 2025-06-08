// Fixtures setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const fixtureList = document.getElementById('fixture-list');
    const fixtureForm = document.getElementById('fixture-form');
    const fixtureIndexInput = document.getElementById('fixture-index');
    const fixtureNameInput = document.getElementById('fixture-name');
    const fixtureTypeSelect = document.getElementById('fixture-type');
    const fixtureChannelInput = document.getElementById('fixture-channel');
    const channelList = document.getElementById('channel-list');
    const addFixtureBtn = document.getElementById('add-fixture');
    const deleteFixtureBtn = document.getElementById('delete-fixture');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const dmxMap = document.getElementById('dmx-map');
    
    // State
    let fixtures = [];
    let editingFixtureIndex = -1;
    
    // Initialize
    loadFixtures();
    renderDmxMap();
    
    // Event listeners
    fixtureTypeSelect.addEventListener('change', updateChannelList);
    addFixtureBtn.addEventListener('click', createNewFixture);
    deleteFixtureBtn.addEventListener('click', deleteFixture);
    cancelEditBtn.addEventListener('click', cancelEdit);
    fixtureForm.addEventListener('submit', saveFixture);
    
    // Functions
    function loadFixtures() {
        fetch('/setup/api/config')
            .then(response => response.json())
            .then(data => {
                fixtures = data.fixtures || [];
                renderFixtureList();
                renderDmxMap();
            })
            .catch(error => {
                console.error('Error loading fixtures:', error);
                alert('Error loading fixtures. See console for details.');
            });
    }
    
    function renderFixtureList() {
        fixtureList.innerHTML = '';
        
        if (fixtures.length === 0) {
            fixtureList.innerHTML = '<p class="no-fixtures">No fixtures configured yet.</p>';
            return;
        }
        
        fixtures.forEach((fixture, index) => {
            const fixtureEl = document.createElement('div');
            fixtureEl.className = 'fixture-item';
            fixtureEl.textContent = fixture.name;
            fixtureEl.setAttribute('data-index', index);
            fixtureEl.addEventListener('click', () => editFixture(index));
            fixtureList.appendChild(fixtureEl);
        });
    }
    
    function updateChannelList() {
        const fixtureType = fixtureTypeSelect.value;
        
        // Get channel configuration for this fixture type
        fetch(`/setup/api/fixture-types/${fixtureType}`)
            .then(response => response.json())
            .then(data => {
                renderChannelList(data.channels);
            })
            .catch(error => {
                console.error('Error loading fixture type details:', error);
            });
    }
    
    function renderChannelList(channels) {
        channelList.innerHTML = '';
        
        channels.forEach((channel, index) => {
            // if (!channel.visible) return
            const channelEl = document.createElement('div');
            channelEl.className = 'channel-item';
            
            const startChannel = parseInt(fixtureChannelInput.value) || 1;
            const channelNumber = document.createElement('div');
            channelNumber.className = 'channel-number';
            channelNumber.textContent = startChannel + index;
            
            const channelName = document.createElement('div');
            channelName.className = 'channel-name';
            channelName.textContent = channel.name;
            
            channelEl.appendChild(channelNumber);
            channelEl.appendChild(channelName);
            channelList.appendChild(channelEl);
        });
    }
    
    function createNewFixture() {
        editingFixtureIndex = -1;
        fixtureIndexInput.value = -1;
        fixtureForm.reset();
        fixtureNameInput.value = '';
        fixtureTypeSelect.value = 'Generic';
        fixtureChannelInput.value = '1';
        updateChannelList();
        
        // Clear active state from fixture list
        const activeFixture = fixtureList.querySelector('.fixture-item.active');
        if (activeFixture) {
            activeFixture.classList.remove('active');
        }
    }
    
    function editFixture(index) {
        editingFixtureIndex = index;
        fixtureIndexInput.value = index;
        
        const fixture = fixtures[index];
        fixtureNameInput.value = fixture.name;
        fixtureTypeSelect.value = fixture.type;
        fixtureChannelInput.value = fixture.start_channel;
        
        updateChannelList();
        
        // Set active state in fixture list
        const activeFixture = fixtureList.querySelector('.fixture-item.active');
        if (activeFixture) {
            activeFixture.classList.remove('active');
        }
        
        const fixtureEl = fixtureList.querySelector(`[data-index="${index}"]`);
        if (fixtureEl) {
            fixtureEl.classList.add('active');
        }
    }
    
    function saveFixture(e) {
        e.preventDefault();
        
        const fixtureType = fixtureTypeSelect.value;
        
        // Get channel count for this fixture type
        fetch(`/setup/api/fixture-types/${fixtureType}`)
            .then(response => response.json())
            .then(data => {
                const channelCount = data.channels.length;
                
                // Create fixture data
                const fixture = {
                    name: fixtureNameInput.value,
                    type: fixtureTypeSelect.value,
                    start_channel: parseInt(fixtureChannelInput.value),
                    channel_count: channelCount
                };
                
                // Validate fixture data
                if (!fixture.name) {
                    alert('Fixture name is required');
                    return;
                }
                
                if (fixture.start_channel < 1 || fixture.start_channel > 512) {
                    alert('DMX channel must be between 1 and 512');
                    return;
                }
                
                // Check for channel conflicts
                const conflicts = checkChannelConflicts(fixture);
                if (conflicts.length > 0 && editingFixtureIndex === -1) {
                    const proceed = confirm(`Warning: This fixture overlaps with channels used by: ${conflicts.join(', ')}\n\nProceed anyway?`);
                    if (!proceed) {
                        return;
                    }
                }
                
                // Update fixtures array
                if (editingFixtureIndex === -1) {
                    fixtures.push(fixture);
                } else {
                    fixtures[editingFixtureIndex] = fixture;
                }
                
                // Save fixtures to server
                saveFixtures();
            })
            .catch(error => {
                console.error('Error getting fixture type details:', error);
                alert('Error saving fixture. See console for details.');
            });
    }
    
    function checkChannelConflicts(newFixture) {
        const conflicts = [];
        const newStart = newFixture.start_channel;
        const newEnd = newStart + newFixture.channel_count - 1;
        
        fixtures.forEach((fixture, index) => {
            // Skip comparing with itself if editing
            if (index === editingFixtureIndex) {
                return;
            }
            
            const fixtureStart = fixture.start_channel;
            const fixtureEnd = fixtureStart + fixture.channel_count - 1;
            
            // Check for overlap
            if ((newStart >= fixtureStart && newStart <= fixtureEnd) || 
                (newEnd >= fixtureStart && newEnd <= fixtureEnd) ||
                (fixtureStart >= newStart && fixtureStart <= newEnd)) {
                conflicts.push(fixture.name);
            }
        });
        
        return conflicts;
    }
    
    function saveFixtures() {
        fetch('/setup/api/config/fixtures', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fixtures: fixtures })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reset form and refresh fixtures
                createNewFixture();
                renderFixtureList();
                renderDmxMap();
                alert('Fixture saved successfully!');
            } else {
                alert('Failed to save fixture: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error saving fixtures:', error);
            alert('Error saving fixture. See console for details.');
        });
    }
    
    function deleteFixture() {
        if (editingFixtureIndex === -1) {
            // Nothing to delete
            return;
        }
        
        const fixture = fixtures[editingFixtureIndex];
        if (!confirm(`Are you sure you want to delete fixture "${fixture.name}"?`)) {
            return;
        }
        
        // Remove from array
        fixtures.splice(editingFixtureIndex, 1);
        
        // Save fixtures to server
        saveFixtures();
    }
    
    function cancelEdit() {
        createNewFixture();
    }
    
    function renderDmxMap() {
        dmxMap.innerHTML = '';
        
        // Create DMX channel map (512 channels)
        for (let i = 1; i <= 512; i++) {
            const channel = document.createElement('div');
            channel.className = 'dmx-channel';
            channel.textContent = i;
            
            // Check if this channel is used by a fixture
            fixtures.forEach(fixture => {
                const startChannel = fixture.start_channel;
                const endChannel = startChannel + fixture.channel_count - 1;
                
                if (i >= startChannel && i <= endChannel) {
                    channel.classList.add('used');
                    channel.setAttribute('data-fixture', `${fixture.name} (${fixture.type})`);
                }
            });
            
            dmxMap.appendChild(channel);
        }
    }
    
    // Initialize channel list based on default selected type
    updateChannelList();
    
    // Update channel numbers when start channel changes
    fixtureChannelInput.addEventListener('input', function() {
        const channels = channelList.querySelectorAll('.channel-item');
        const startChannel = parseInt(this.value) || 1;
        
        channels.forEach((channel, index) => {
            const channelNumber = channel.querySelector('.channel-number');
            channelNumber.textContent = startChannel + index;
        });
    });
});
