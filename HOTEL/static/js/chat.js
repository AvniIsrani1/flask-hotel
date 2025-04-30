// chat.js - Updated to ensure proper functionality

// Store chat state in session storage to persist across pages
function openChat() {
    document.getElementById("myForm").style.display = "block";
    sessionStorage.setItem('chatOpen', 'true');
}

function closeChat() {
    document.getElementById("myForm").style.display = "none";
    sessionStorage.setItem('chatOpen', 'false');
}

function sendMessage() {
    let userInput = document.getElementById("userInput").value.trim();
    if (userInput === "") return;

    // Append user message to chat
    let chatBox = document.getElementById("chatBox");
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerText = "You: " + userInput;
    chatBox.appendChild(userMessage);

    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Clear input field
    document.getElementById("userInput").value = "";

    // Send user input to Flask backend
    fetch("/get_response", {
        method: "POST",
        body: JSON.stringify({ message: userInput }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        // Append AI response to chat
        let botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.innerText = "Ocean Vista: " + data.response;
        chatBox.appendChild(botMessage);

        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Store chat messages in session storage
        storeChatHistory();
    })
    .catch(error => console.error("Error:", error));
}

// Store chat history in session storage
function storeChatHistory() {
    const chatBox = document.getElementById("chatBox");
    sessionStorage.setItem('chatHistory', chatBox.innerHTML);
}

// Load chat history from session storage
function loadChatHistory() {
    const chatBox = document.getElementById("chatBox");
    const chatHistory = sessionStorage.getItem('chatHistory');
    if (chatHistory) {
        chatBox.innerHTML = chatHistory;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Check if chat was open
    const chatOpen = sessionStorage.getItem('chatOpen');
    if (chatOpen === 'true') {
        document.getElementById("myForm").style.display = "block";
    }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", function() {
    loadChatHistory();
    
    // Add event listener for Enter key in textarea
    document.getElementById("userInput").addEventListener("keypress", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // Prevent default behavior (newline)
            sendMessage();
        }
    });
});