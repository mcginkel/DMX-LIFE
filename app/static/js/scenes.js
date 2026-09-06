// Scenes setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const sceneList = document.getElementById('scene-list');
    const sceneForm = document.getElementById('scene-form');
    const sceneNameInput = document.getElementById('scene-name');
    const sceneGroupSelect = document.getElementById('scene-group');
    const addSceneBtn = document.getElementById('add-scene');
    const deleteSceneBtn = document.getElementById('delete-scene');
    const testSceneBtn = document.getElementById('test-scene');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const fixtureControls = document.getElementById('fixture-controls');
    const sceneCounter = document.getElementById('scene-counter');
    
    // State
    let scenes = [];
    let fixtures = [];
    let fixtureTypes = {}; // Cache for fixture types
    let editingSceneName = null;
    let maxScenes = 10;
    
    // Initialize
    loadData();
    
    // Event listeners
    addSceneBtn.addEventListener('click', createNewScene);
    deleteSceneBtn.addEventListener('click', deleteScene);
    testSceneBtn.addEventListener('click', testScene);
    cancelEditBtn.addEventListener('click', cancelEdit);
    sceneForm.addEventListener('submit', saveScene);
    
    // Functions
    function loadData() {
        fetch('/setup/api/config')
            .then(response => response.json())
            .then(data => {
                scenes = data.scenes || [];
                fixtures = data.fixtures || [];
                maxScenes = data.MAX_SCENES || 10;
                
                // Preload fixture types for better performance
                preloadFixtureTypes();
                
                renderSceneList();
                updateSceneCounter();
                
                // Auto-select first scene if available, otherwise create new scene
                if (scenes.length > 0) {
                    editScene(scenes[0].name);
                } else {
                    createNewScene();
                }
            })
            .catch(error => {
                console.error('Error loading data:', error);
                alert('Error loading data. See console for details.');
            });
    }
    
    function updateSceneCounter() {
        sceneCounter.textContent = `(${scenes.length}/${maxScenes})`;
        
        // Disable add button if max scenes reached
        addSceneBtn.disabled = scenes.length >= maxScenes;
    }
    
    function renderSceneList() {
        sceneList.innerHTML = '';
        
        if (scenes.length === 0) {
            sceneList.innerHTML = '<p class="no-scenes">No scenes configured yet.</p>';
            return;
        }
        
        scenes.forEach(scene => {
            const sceneEl = document.createElement('div');
            sceneEl.className = 'scene-item';
            sceneEl.textContent = scene.name;
            sceneEl.setAttribute('data-scene', scene.name);
            sceneEl.addEventListener('click', () => editScene(scene.name));
            sceneList.appendChild(sceneEl);
        });
    }
    
    function createNewScene() {
        editingSceneName = null;
        sceneForm.reset();
        sceneNameInput.value = '';
        
        // Clear active state from scene list
        const activeScene = sceneList.querySelector('.scene-item.active');
        if (activeScene) {
            activeScene.classList.remove('active');
        }
        
        // Initialize controls with all fixtures enabled by default for new scenes
        renderFixtureControls({}, true);
    }
    
    function editScene(sceneName) {
        editingSceneName = sceneName;
        
        // Find scene in array
        const scene = scenes.find(s => s.name === sceneName);
        if (!scene) return;
        
        sceneNameInput.value = scene.name;
        sceneGroupSelect.value = scene.group || '';
        
        // Set active state in scene list
        const activeScene = sceneList.querySelector('.scene-item.active');
        if (activeScene) {
            activeScene.classList.remove('active');
        }
        
        const sceneEl = sceneList.querySelector(`[data-scene="${sceneName}"]`);
        if (sceneEl) {
            sceneEl.classList.add('active');
        }
        
        // Which fixtures participate is derived from which channels the
        // scene's map contains - there is no stored enabledFixtures list.
        renderFixtureControls(scene.channels || {}, false);
        testScene();

    }
    
    // A fixture's DMX channel numbers, 1-based, as stored in a scene map.
    function fixtureChannels(fixture) {
        const channels = [];
        for (let i = 0; i < fixture.channel_count; i++) {
            channels.push(fixture.start_channel + i);
        }
        return channels;
    }

    // Whether a scene claims a channel is now tracked per row. A claimed
    // channel is written to the map on save - including one holding zero,
    // which is how the "Uit" scenes force fixtures dark. An unclaimed
    // channel is absent from the map entirely and is left to other layers.
    function isChannelClaimed(row) {
        return row.classList.contains('claimed');
    }

    // An unclaimed channel shows no value rather than 0: a deliberate zero
    // and an unclaimed channel mean different things, and showing 0 for both
    // would hide exactly the distinction this is here to make.
    function setChannelClaimed(row, claimed) {
        row.classList.toggle('claimed', claimed);
        const slider = row.querySelector('input[type="range"]');
        const display = row.querySelector('.value');
        if (slider && display) {
            display.textContent = claimed ? slider.value : '\u2013';
        }
    }

    // The fixture control is a summary of its channels: all, none, or some.
    // "Some" is reported but cannot be selected directly - it arises from
    // claiming individual rows.
    function updateFixtureSummary(fixtureEl) {
        const rows = [...fixtureEl.querySelectorAll('.channel-control')];
        const claimed = rows.filter(isChannelClaimed).length;
        const checkbox = fixtureEl.querySelector('.fixture-enable');
        if (!checkbox) return;
        checkbox.checked = rows.length > 0 && claimed === rows.length;
        checkbox.indeterminate = claimed > 0 && claimed < rows.length;
    }

    // The fixture type's declared default for one of its channels, used for
    // channels absent from a scene's map.
    function channelDefault(fixture, channelOffset) {
        const type = fixtureTypes[fixture.type];
        const channelInfo = type && type.channels && type.channels[channelOffset];
        return channelInfo && typeof channelInfo.default === 'number'
            ? channelInfo.default
            : 0;
    }

    // The payload is exactly the claimed channels with their current values,
    // including zeros. No widening to whole fixtures: a scene that claims
    // five channels claims five after a round trip, because the editor has
    // no opinion about the channels it was not asked to touch.
    function collectChannelMap() {
        const channelMap = {};
        fixtureControls.querySelectorAll('.channel-control.claimed').forEach(row => {
            const slider = row.querySelector('input[type="range"]');
            if (!slider) return;
            const channel = parseInt(slider.getAttribute('data-channel'), 10);
            channelMap[channel] = parseInt(slider.value, 10);
        });
        return channelMap;
    }

    function renderFixtureControls(channelMap = {}, allEnabled = false) {
        fixtureControls.innerHTML = '';
        
        if (fixtures.length === 0) {
            fixtureControls.innerHTML = '<p class="no-fixtures">No fixtures configured yet. Go to <a href="/setup/fixtures">Fixture Setup</a> first.</p>';
            return;
        }
        
        fixtures.forEach(fixture => {
            const fixtureEl = document.createElement('div');
            fixtureEl.className = 'fixture-control';
            
            // Create header container for fixture name and enable checkbox
            const fixtureHeaderContainer = document.createElement('div');
            fixtureHeaderContainer.className = 'fixture-header';
            
            // Create fixture enable/disable checkbox
            const fixtureEnableLabel = document.createElement('label');
            fixtureEnableLabel.className = 'fixture-enable-label';
            
            const fixtureEnableCheckbox = document.createElement('input');
            fixtureEnableCheckbox.type = 'checkbox';
            fixtureEnableCheckbox.className = 'fixture-enable';
            fixtureEnableCheckbox.setAttribute('data-fixture-name', fixture.name);
            
            fixtureEnableLabel.appendChild(fixtureEnableCheckbox);
            fixtureEnableLabel.appendChild(document.createTextNode(' Enable'));
            
            // Fixture name
            const fixtureHeader = document.createElement('h4');            // Add visual indicator for linked fixtures
            let displayText = fixture.name;
            if (fixture.linked_to) {
                displayText += ` (→ ${fixture.linked_to})`;
            }
            fixtureHeader.textContent = `${displayText} (${fixture.type})`;
            
            fixtureHeaderContainer.appendChild(fixtureHeader);
            fixtureHeaderContainer.appendChild(fixtureEnableLabel);
            fixtureEl.appendChild(fixtureHeaderContainer);
            
            // Create channel controls
            const channelsContainer = document.createElement('div');
            channelsContainer.className = 'channel-controls';
            
            // Selecting or releasing a whole fixture stays one action - which
            // is how every existing scene is authored.
            fixtureEnableCheckbox.addEventListener('change', function() {
                channelsContainer.querySelectorAll('.channel-control').forEach(row => {
                    setChannelClaimed(row, this.checked);
                });
                updateFixtureSummary(fixtureEl);
                testScene(); // Update preview
            });

            for (let i = 0; i < fixture.channel_count; i++) {
                const channel = fixture.start_channel + i; // 1-based DMX channel
                // A stored 0 is a real value, so test for presence rather
                // than truthiness; absent channels fall back to the type default.
                const isClaimed = allEnabled
                    ? true // New scenes start with every channel claimed
                    : Object.prototype.hasOwnProperty.call(channelMap, channel);
                const channelValue = isClaimed && Object.prototype.hasOwnProperty.call(channelMap, channel)
                    ? channelMap[channel]
                    : channelDefault(fixture, i);

                const channelEl = createChannelControl(fixture, i, channel, channelValue);
                setChannelClaimed(channelEl, isClaimed);

                // Clicking the row claims or releases the channel. The slider
                // owns its own clicks and drags: adjusting a value must never
                // be read as a change of participation.
                channelEl.addEventListener('click', function(event) {
                    if (event.target.closest('input[type="range"]')) return;
                    if (channelEl.dataset.sliderDrag === 'true') return;
                    setChannelClaimed(channelEl, !isChannelClaimed(channelEl));
                    updateFixtureSummary(fixtureEl);
                    testScene();
                });

                channelsContainer.appendChild(channelEl);
            }

            fixtureEl.appendChild(channelsContainer);
            updateFixtureSummary(fixtureEl);
            fixtureControls.appendChild(fixtureEl);
        });
    }
    
    function createChannelControl(fixture, channelOffset, channel, value = 0) {
        // Get channel type information
        const channelContainer = document.createElement('div');
        channelContainer.className = 'channel-control';
        
        // Get channel name from fixture type (with caching)
        let channelName = `Channel ${channelOffset + 1}`;
        
        // Check cache first
        if (fixtureTypes[fixture.type]) {
            const channelInfo = fixtureTypes[fixture.type].channels[channelOffset];
            if (channelInfo) {
                channelName = channelInfo.name;
            }
        } else {
            // Fetch and cache fixture type data
            fetch(`/setup/api/fixture-types/${fixture.type}`)
                .then(response => response.json())
                .then(data => {
                    // Cache the fixture type data
                    fixtureTypes[fixture.type] = data;
                    
                    const channelInfo = data.channels[channelOffset];
                    if (channelInfo) {
                        channelLabel.textContent = channelInfo.name;
                    }
                })
                .catch(error => {
                    console.error('Error loading fixture type details:', error);
                });
        }
        
        // Label
        const channelLabel = document.createElement('label');
        channelLabel.textContent = channelName;
        channelLabel.setAttribute('for', `channel-${channel}`);
        
        // Range input
        const channelInput = document.createElement('input');
        channelInput.type = 'range';
        channelInput.min = 0;
        channelInput.max = 255;
        channelInput.value = value;
        channelInput.id = `channel-${channel}`;
        channelInput.setAttribute('data-channel', channel);
         
        // Value display
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'value';
        valueDisplay.textContent = value;
        
        // A drag that starts on the slider can end anywhere, and the click
        // that follows fires on a common ancestor - which would be read as a
        // claim toggle. Mark the row for the duration so the row's own
        // handler ignores it.
        channelInput.addEventListener('pointerdown', function() {
            channelContainer.dataset.sliderDrag = 'true';
        });
        window.addEventListener('pointerup', function() {
            if (channelContainer.dataset.sliderDrag === 'true') {
                // Cleared after the click has been dispatched and ignored.
                setTimeout(() => { delete channelContainer.dataset.sliderDrag; }, 0);
            }
        });

        // Update value display when slider changes. An unclaimed channel
        // keeps showing no value - its slider position is remembered for if
        // it is claimed later, but the scene does not carry it.
        channelInput.addEventListener('input', function() {
            if (channelContainer.classList.contains('claimed')) {
                valueDisplay.textContent = this.value;
            }

            // Copy value to linked fixtures
            copyValueToLinkedFixtures(fixture, channelOffset, this.value);

            testScene();
        });
        
        channelContainer.appendChild(channelLabel);
        channelContainer.appendChild(channelInput);
        channelContainer.appendChild(valueDisplay);
        
        return channelContainer;
    }
    
    function saveScene(e) {
        e.preventDefault();
        
        const sceneName = sceneNameInput.value;
        
        // Validate scene name
        if (!sceneName) {
            alert('Scene name is required');
            return;
        }
        
        // Check if editing or creating new
        if (!editingSceneName && scenes.some(s => s.name === sceneName)) {
            alert('A scene with this name already exists');
            return;
        }
        
        // Check max scenes limit for new scenes
        if (!editingSceneName && scenes.length >= maxScenes) {
            alert(`Maximum ${maxScenes} scenes allowed`);
            return;
        }
        
        // Create scene data. The group has to be sent explicitly: the server
        // rewrites the whole scene record on save, so omitting it would clear
        // the scene's group rather than leave it alone.
        const sceneData = {
            name: sceneName,
            channels: collectChannelMap(),
            group: sceneGroupSelect.value || null
        };
        
        // Send to server
        fetch('/setup/api/config/scenes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sceneData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update local data and refresh UI
                if (editingSceneName) {
                    // Update existing scene
                    const index = scenes.findIndex(s => s.name === editingSceneName);
                    if (index !== -1) {
                        scenes[index] = sceneData;
                    }
                } else {
                    // Add new scene
                    scenes.push(sceneData);
                }
                
                renderSceneList();
                updateSceneCounter();
                createNewScene();
                alert('Scene saved successfully!');
            } else {
                alert('Failed to save scene: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error saving scene:', error);
            alert('Error saving scene. See console for details.');
        });
    }
    
    function deleteScene() {
        if (!editingSceneName) {
            // Nothing to delete
            return;
        }
        
        if (!confirm(`Are you sure you want to delete scene "${editingSceneName}"?`)) {
            return;
        }
        
        // Remove from scenes array
        const index = scenes.findIndex(s => s.name === editingSceneName);
        if (index !== -1) {
            scenes.splice(index, 1);
        }
        
        // Update scenes list on server
        fetch('/setup/api/config/scenes', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: editingSceneName
            })
        })
        .then(response => response.json())
        .then(data => {
            renderSceneList();
            updateSceneCounter();
            createNewScene();
        })
        .catch(error => {
            console.error('Error deleting scene:', error);
            alert('Error deleting scene. See console for details.');
        });
    }
    
    function testScene() {
        // Preview exactly what would be saved: the same enabled-fixture map.
        fetch('/setup/api/config/scenes/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                channels: collectChannelMap()
            })
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error testing scene:', error);
            alert('Error testing scene. See console for details.');
        });
    }
    
    function cancelEdit() {
        createNewScene();
    }
    
    function copyValueToLinkedFixtures(sourceFixture, channelOffset, value) {
        // Find fixtures linked to the source fixture by name
        fixtures.forEach((fixture) => {
            // Skip if this is the source fixture or if it's not linked to the source
            if (fixture.name === sourceFixture.name || fixture.linked_to !== sourceFixture.name) {
                return;
            }
            
            // Only copy if fixtures are of the same type
            if (fixture.type !== sourceFixture.type) {
                return;
            }
            
            // Calculate the corresponding DMX channel in the linked fixture
            const linkedChannel = fixture.start_channel + channelOffset; // 1-based
            
            // Find the corresponding slider for this channel
            const linkedSlider = fixtureControls.querySelector(`input[data-channel="${linkedChannel}"]`);
            if (linkedSlider) {
                linkedSlider.value = value;
                // Update the value display, unless that channel is unclaimed -
                // it must keep reading as "no value", not as a number the
                // scene does not actually carry.
                const linkedRow = linkedSlider.closest('.channel-control');
                const valueDisplay = linkedSlider.parentNode.querySelector('.value');
                if (valueDisplay && linkedRow && linkedRow.classList.contains('claimed')) {
                    valueDisplay.textContent = value;
                }
            }
        });
    }
    
    function preloadFixtureTypes() {
        // Get unique fixture types
        const uniqueTypes = [...new Set(fixtures.map(f => f.type))];
        
        // Preload fixture type data for all unique types
        uniqueTypes.forEach(type => {
            if (!fixtureTypes[type]) {
                fetch(`/setup/api/fixture-types/${type}`)
                    .then(response => response.json())
                    .then(data => {
                        fixtureTypes[type] = data;
                    })
                    .catch(error => {
                        console.error(`Error preloading fixture type ${type}:`, error);
                    });
            }
        });
    }
});
