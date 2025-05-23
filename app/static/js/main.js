// Main JavaScript for scene selection interface

document.addEventListener('DOMContentLoaded', function() {
    // Get all scene buttons
    const sceneButtons = document.querySelectorAll('.scene-button');
    
    // Add click handlers to scene buttons
    sceneButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sceneName = this.getAttribute('data-scene');
            activateScene(sceneName);
        });
    });
    
    // Function to activate a scene
    function activateScene(sceneName) {
        // Call the API to activate the scene
        fetch('/api/scenes/activate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ scene: sceneName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI to show active scene
                sceneButtons.forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.getAttribute('data-scene') === sceneName) {
                        btn.classList.add('active');
                    }
                });
            } else {
                alert('Failed to activate scene: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error activating scene:', error);
            alert('Error activating scene. See console for details.');
        });
    }
});
