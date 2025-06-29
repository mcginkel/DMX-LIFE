// Scenes setup JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const sceneList = document.getElementById('scene-list');
    const sceneForm = document.getElementById('scene-form');
    const sceneNameInput = document.getElementById('scene-name');
    const addSceneBtn = document.getElementById('add-scene');
    const deleteSceneBtn = document.getElementById('delete-scene');
    const testSceneBtn = document.getElementById('test-scene');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const fixtureControls = document.getElementById('fixture-controls');
    const sceneCounter = document.getElementById('scene-counter');
    
    // State
    let scenes = [];
    let fixtures = [];
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
                
                renderSceneList();
                updateSceneCounter();
                createNewScene();
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
        renderFixtureControls([], fixtures.map(f => f.name));
    }
    
    function editScene(sceneName) {
        editingSceneName = sceneName;
        
        // Find scene in array
        const scene = scenes.find(s => s.name === sceneName);
        if (!scene) return;
        
        sceneNameInput.value = scene.name;
        
        // Set active state in scene list
        const activeScene = sceneList.querySelector('.scene-item.active');
        if (activeScene) {
            activeScene.classList.remove('active');
        }
        
        const sceneEl = sceneList.querySelector(`[data-scene="${sceneName}"]`);
        if (sceneEl) {
            sceneEl.classList.add('active');
        }
        
        // Get enabled fixtures (default to all if not specified in the scene)
        const enabledFixtures = scene.enabledFixtures || [];
        
        renderFixtureControls(scene.channels, enabledFixtures);
        testScene();

    }
    
    function renderFixtureControls(channelValues = [], enabledFixtures = []) {
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
            fixtureEnableCheckbox.checked = editingSceneName ? 
                (enabledFixtures.includes(fixture.name)) : true; // Default enabled for new scenes
            fixtureEnableCheckbox.setAttribute('data-fixture-name', fixture.name);
            
            fixtureEnableLabel.appendChild(fixtureEnableCheckbox);
            fixtureEnableLabel.appendChild(document.createTextNode(' Enable'));
            
            // Fixture name
            const fixtureHeader = document.createElement('h4');
            fixtureHeader.textContent = `${fixture.name} (${fixture.type})`;
            
            fixtureHeaderContainer.appendChild(fixtureHeader);
            fixtureHeaderContainer.appendChild(fixtureEnableLabel);
            fixtureEl.appendChild(fixtureHeaderContainer);
            
            // Create channel controls
            const channelsContainer = document.createElement('div');
            channelsContainer.className = 'channel-controls';
            
            // Toggle channel controls visibility based on enable state
            fixtureEnableCheckbox.addEventListener('change', function() {
                channelsContainer.style.opacity = this.checked ? '1' : '0.5';
                testScene(); // Update preview
            });
            
            // Set initial state
            channelsContainer.style.opacity = fixtureEnableCheckbox.checked ? '1' : '0.5';
            
            for (let i = 0; i < fixture.channel_count; i++) {
                const channelIndex = fixture.start_channel + i - 1; // 0-based index
                const channelValue = channelValues[channelIndex] || 0;
                
                const channelEl = createChannelControl(fixture, i, channelIndex, channelValue);
                channelsContainer.appendChild(channelEl);
            }
            
            fixtureEl.appendChild(channelsContainer);
            fixtureControls.appendChild(fixtureEl);
        });
    }
    
    function createChannelControl(fixture, channelOffset, dmxIndex, value = 0) {
        // Get channel type information
        const channelContainer = document.createElement('div');
        channelContainer.className = 'channel-control';
        
        // Get channel name from fixture type
        let channelName = `Channel ${channelOffset + 1}`;
        fetch(`/setup/api/fixture-types/${fixture.type}`)
            .then(response => response.json())
            .then(data => {
                const channelInfo = data.channels[channelOffset];
                if (channelInfo) {
                    channelLabel.textContent = channelInfo.name;
                }
            })
            .catch(error => {
                console.error('Error loading fixture type details:', error);
            });
        
        // Label
        const channelLabel = document.createElement('label');
        channelLabel.textContent = channelName;
        channelLabel.setAttribute('for', `channel-${dmxIndex}`);
        
        // Range input
        const channelInput = document.createElement('input');
        channelInput.type = 'range';
        channelInput.min = 0;
        channelInput.max = 255;
        channelInput.value = value;
        channelInput.id = `channel-${dmxIndex}`;
        channelInput.setAttribute('data-dmx-index', dmxIndex);
         
        // Value display
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'value';
        valueDisplay.textContent = value;
        
        // Update value display when slider changes
        channelInput.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
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
        
        // Collect channel values from form
        const channels = [];
        const sliders = fixtureControls.querySelectorAll('input[type="range"]');
        
        // Initialize all channels to 0
        for (let i = 0; i < 512; i++) {
            channels[i] = 0;
        }
        
        // Set channel values from sliders
        sliders.forEach(slider => {
            const dmxIndex = parseInt(slider.getAttribute('data-dmx-index'));
            channels[dmxIndex] = parseInt(slider.value);
        });
        
        // Get enabled fixtures
        const enabledFixtures = [];
        const fixtureCheckboxes = fixtureControls.querySelectorAll('.fixture-enable');
        fixtureCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                enabledFixtures.push(checkbox.getAttribute('data-fixture-name'));
            }
        });
        
        // Create scene data
        const sceneData = {
            name: sceneName,
            channels: channels,
            enabledFixtures: enabledFixtures
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
        // Collect channel values from form
        const channels = [];
        
        // Initialize all channels to 0
        for (let i = 0; i < 512; i++) {
            channels[i] = 0;
        }
        
        // Get enabled fixtures
        const enabledFixtureNames = [];
        const fixtureCheckboxes = fixtureControls.querySelectorAll('.fixture-enable');
        fixtureCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                enabledFixtureNames.push(checkbox.getAttribute('data-fixture-name'));
            }
        });
        
        // Set channel values from sliders, but only for enabled fixtures
        fixtures.forEach(fixture => {
            // Skip disabled fixtures
            if (!enabledFixtureNames.includes(fixture.name)) {
                return;
            }
            
            // Find the fixture's channel sliders
            const fixtureEl = Array.from(fixtureControls.querySelectorAll('.fixture-control')).find(el => 
                el.querySelector('h4').textContent.startsWith(fixture.name)
            );
            
            if (fixtureEl) {
                const sliders = fixtureEl.querySelectorAll('input[type="range"]');
                sliders.forEach(slider => {
                    const dmxIndex = parseInt(slider.getAttribute('data-dmx-index'));
                    channels[dmxIndex] = parseInt(slider.value);
                });
            }
        });
        
        // Test scene
        fetch('/setup/api/config/scenes/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                channels: channels
            })
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error testing scene:', error);
            alert('Error testing scene. See console for details.');
        });
    }

    function testSceneOld() {
        const sceneName = sceneNameInput.value;
        
        // Validate scene name
        if (!sceneName) {
            alert('Scene name is required');
            return;
        }
        
        // Collect channel values from form
        const channels = [];
        const sliders = fixtureControls.querySelectorAll('input[type="range"]');
        
        // Initialize all channels to 0
        for (let i = 0; i < 512; i++) {
            channels[i] = 0;
        }
        
        // Set channel values from sliders
        sliders.forEach(slider => {
            const dmxIndex = parseInt(slider.getAttribute('data-dmx-index'));
            channels[dmxIndex] = parseInt(slider.value);
        });
        
        // Create temporary scene
        const tempSceneName = `__test_${Date.now()}`;
        
        // Save temporary scene and activate it
        fetch('/setup/api/config/scenes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: tempSceneName,
                channels: channels
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Activate the temporary scene
                return fetch('/api/scenes/activate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ scene: tempSceneName })
                });
            }
            throw new Error('Failed to create temporary scene');
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
});
