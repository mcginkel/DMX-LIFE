// Fixtures setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const fixtureList = document.getElementById('fixture-list');
    const fixtureForm = document.getElementById('fixture-form');
    const fixtureIndexInput = document.getElementById('fixture-index');
    const fixtureNameInput = document.getElementById('fixture-name');
    const fixtureTypeSelect = document.getElementById('fixture-type');
    const fixtureChannelInput = document.getElementById('fixture-channel');
    const fixtureLinkSelect = document.getElementById('fixture-link');
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
    fixtureTypeSelect.addEventListener('change', function() {
        updateChannelList();
        updateLinkOptions();
    });
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
                // Ensure all fixtures have the linked_to field for backward compatibility
                fixtures.forEach(fixture => {
                    if (fixture.linked_to === undefined) {
                        fixture.linked_to = null;
                    }
                });
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
            
            // Add visual indicator for linked fixtures
            let displayText = fixture.name;
            if (fixture.linked_to !== undefined && fixture.linked_to !== null) {
                const linkedFixture = fixtures[fixture.linked_to];
                if (linkedFixture) {
                    displayText += ` (→ ${linkedFixture.name})`;
                }
            }
            
            // Check if this fixture has others linked to it
            const hasLinkedFixtures = fixtures.some((f, i) => f.linked_to === index && i !== index);
            if (hasLinkedFixtures) {
                displayText += ' [Master]';
            }
            
            fixtureEl.textContent = displayText;
            fixtureEl.setAttribute('data-index', index);
            fixtureEl.addEventListener('click', () => editFixture(index));
            fixtureList.appendChild(fixtureEl);
        });
    }
    
    function updateLinkOptions() {
        fixtureLinkSelect.innerHTML = '<option value="">Not linked</option>';
        
        const currentType = fixtureTypeSelect.value;
        
        fixtures.forEach((fixture, index) => {
            // Only show fixtures of the same type
            if (fixture.type === currentType && index !== editingFixtureIndex) {
                // Don't show fixtures that are already linked to someone else
                // (to prevent chaining) or that would create a loop
                if ((fixture.linked_to === null || fixture.linked_to === undefined)) {
                    // Also check that this fixture isn't linked to the current one (prevent loops)
                    if (editingFixtureIndex === -1 || fixture.linked_to !== editingFixtureIndex) {
                        // Check if this fixture has others linked to it (making it a master)
                        const hasLinkedFixtures = fixtures.some((f, i) => f.linked_to === index && i !== index && i !== editingFixtureIndex);
                        if (!hasLinkedFixtures) {
                            const option = document.createElement('option');
                            option.value = index;
                            option.textContent = fixture.name;
                            fixtureLinkSelect.appendChild(option);
                        }
                    }
                }
            }
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
        fixtureLinkSelect.value = '';
        updateChannelList();
        updateLinkOptions();
        
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
        updateLinkOptions();
        
        // Set the link selection
        fixtureLinkSelect.value = fixture.linked_to !== undefined && fixture.linked_to !== null ? fixture.linked_to : '';
        
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
                const linkedToValue = fixtureLinkSelect.value;
                const linkedTo = linkedToValue === '' ? null : parseInt(linkedToValue);
                
                const fixture = {
                    name: fixtureNameInput.value,
                    type: fixtureTypeSelect.value,
                    start_channel: parseInt(fixtureChannelInput.value),
                    channel_count: channelCount,
                    linked_to: linkedTo
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
                
                // Validate linking logic
                if (linkedTo !== null) {
                    // Check if target fixture exists and is same type
                    if (linkedTo >= fixtures.length || fixtures[linkedTo].type !== fixture.type) {
                        alert('Invalid link target: fixture must exist and be of the same type');
                        return;
                    }
                    
                    // Check if target fixture is itself linked to someone (prevent chaining)
                    if (fixtures[linkedTo].linked_to !== null && fixtures[linkedTo].linked_to !== undefined) {
                        alert('Cannot link to a fixture that is already linked to another fixture');
                        return;
                    }
                    
                    // Check if this would create a loop
                    if (linkedTo === editingFixtureIndex) {
                        alert('Cannot link fixture to itself');
                        return;
                    }
                    
                    // Check if the target fixture has others linked to it
                    const hasLinkedFixtures = fixtures.some((f, i) => f.linked_to === linkedTo && i !== editingFixtureIndex);
                    if (hasLinkedFixtures) {
                        alert('Cannot link to a fixture that already has other fixtures linked to it');
                        return;
                    }
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
                    const oldFixture = fixtures[editingFixtureIndex];
                    fixtures[editingFixtureIndex] = fixture;
                    
                    // If this is a master fixture (others are linked to it), 
                    // propagate changes to linked fixtures
                    propagateChangesToLinkedFixtures(editingFixtureIndex, oldFixture, fixture);
                }
                
                // Save fixtures to server
                saveFixtures();
            })
            .catch(error => {
                console.error('Error getting fixture type details:', error);
                alert('Error saving fixture. See console for details.');
            });
    }
    
    function propagateChangesToLinkedFixtures(masterIndex, oldFixture, newFixture) {
        // Find all fixtures linked to this master fixture
        fixtures.forEach((fixture, index) => {
            if (fixture.linked_to === masterIndex && index !== masterIndex) {
                // Update linked fixture with changes from master
                // Only propagate type, start_channel if they changed
                if (oldFixture.type !== newFixture.type) {
                    fixtures[index].type = newFixture.type;
                    fixtures[index].channel_count = newFixture.channel_count;
                }
                
                // Optionally propagate channel changes - this depends on requirements
                // For now, we'll only propagate type and channel count, not start_channel
                // as each fixture needs its own channel assignment
            }
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
        
        // Check if other fixtures are linked to this one
        const linkedFixtures = fixtures.filter((f, i) => f.linked_to === editingFixtureIndex && i !== editingFixtureIndex);
        if (linkedFixtures.length > 0) {
            const linkedNames = linkedFixtures.map(f => f.name).join(', ');
            if (!confirm(`Warning: The following fixtures are linked to "${fixture.name}": ${linkedNames}\n\nDeleting this fixture will unlink them. Continue?`)) {
                return;
            }
        }
        
        if (!confirm(`Are you sure you want to delete fixture "${fixture.name}"?`)) {
            return;
        }
        
        // Unlink any fixtures that were linked to this one
        fixtures.forEach((f, i) => {
            if (f.linked_to === editingFixtureIndex) {
                f.linked_to = null;
            } else if (f.linked_to > editingFixtureIndex) {
                // Adjust indices for fixtures linked to ones after the deleted fixture
                f.linked_to--;
            }
        });
        
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
    updateLinkOptions();
    
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
