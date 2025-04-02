//  JS functions for the 3D model viewer
function showModel(roomId) {
    document.getElementById(`thumbnail-${roomId}`).style.display = 'none';
    document.getElementById(`model-container-${roomId}`).style.display = 'block';
}

function hideModel(roomId) {
    document.getElementById(`model-container-${roomId}`).style.display = 'none';
    document.getElementById(`thumbnail-${roomId}`).style.display = 'block';
} 