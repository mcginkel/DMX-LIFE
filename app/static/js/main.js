// Main JavaScript for scene selection interface

document.addEventListener('DOMContentLoaded', function() {
    // Get all scene buttons
    const sceneButtons = document.querySelectorAll('.scene-button');

    // How often an open page reconciles its indication with the server.
    const REFRESH_INTERVAL = 1000;

    // Number of activations currently in flight. While this is above zero a
    // refresh response is ignored: it may have been issued before the
    // operator's press and would carry the older set, visibly flipping the
    // button back and then forward again when the activation lands.
    let pendingActivations = 0;

    // Add click handlers to scene buttons
    sceneButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sceneName = this.getAttribute('data-scene');
            toggleScene(sceneName);
        });
    });

    // The single place the indication is written, so the activation response
    // and the periodic refresh cannot drift apart.
    function showActiveScenes(activeSceneNames) {
        const activeScenes = new Set(activeSceneNames || []);
        sceneButtons.forEach(btn => {
            btn.classList.toggle('active', activeScenes.has(btn.getAttribute('data-scene')));
        });
    }

    // Function to toggle a scene on/off. The server rebuilds the DMX buffer
    // from every currently active scene and returns the full active list, so
    // the UI just mirrors that list rather than guessing locally.
    function toggleScene(sceneName) {
        pendingActivations += 1;
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
                showActiveScenes(data.active_scenes);
            } else {
                alert('Failed to activate scene: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error activating scene:', error);
            alert('Error activating scene. See console for details.');
        })
        .finally(() => {
            pendingActivations -= 1;
        });
    }

    // Another client - a second browser, a tablet in the room - can change
    // what is active. This is a read: it updates what is shown and never
    // activates anything, so refreshing can never alter the lighting.
    //
    // A failure is logged and otherwise ignored. The connection indicator
    // already reports an unreachable server, and an alert every time one poll
    // times out would be worse during a show than the staleness it reports.
    // The next successful refresh converges.
    function refreshActiveScenes() {
        fetch('/api/scenes')
            .then(response => response.json())
            .then(data => {
                if (pendingActivations > 0) {
                    return; // the operator's own action wins
                }
                showActiveScenes(data.active_scenes);
            })
            .catch(error => {
                console.error('Error refreshing active scenes:', error);
            });
    }

    setInterval(refreshActiveScenes, REFRESH_INTERVAL);
});
