// Main JavaScript for scene selection interface

document.addEventListener('DOMContentLoaded', function() {
    // Get all scene buttons
    const sceneButtons = document.querySelectorAll('.scene-button');

    // Add click handlers to scene buttons
    sceneButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sceneName = this.getAttribute('data-scene');
            toggleScene(sceneName);
        });
    });

    // Function to toggle a scene on/off. The server rebuilds the DMX buffer
    // from every currently active scene and returns the full active list, so
    // the UI just mirrors that list rather than guessing locally.
    function toggleScene(sceneName) {
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
                const activeScenes = new Set(data.active_scenes || []);
                sceneButtons.forEach(btn => {
                    btn.classList.toggle('active', activeScenes.has(btn.getAttribute('data-scene')));
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
