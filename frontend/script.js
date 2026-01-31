document.addEventListener('DOMContentLoaded', () => {
    // If we are on the dashboard, load the plan
    if (document.getElementById('plan-container')) {
        fetchPlan();
    }
});

async function fetchPlan() {
    const container = document.getElementById('plan-container');
    try {
        const response = await fetch('/generate-plan', { 
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<p class="text-accent">Error: ${data.error}</p>`;
            return;
        }

        let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">';
        
        // Render Workout
        html += '<div class="card"><h3>🏋️ Workout Plan</h3><div class="mt-4">';
        data.workout.forEach(day => {
            html += `<div class="mb-4">
                <h4 class="text-accent">${day.day}</h4>
                <ul style="padding-left: 20px; margin-top: 5px;">
                    ${day.exercises.map(ex => `<li>${ex}</li>`).join('')}
                </ul>
            </div>`;
        });
        html += '</div></div>';

        // Render Diet
        html += '<div class="card"><h3>🥗 Diet Plan</h3><div class="mt-4">';
        html += `
            <div class="mb-4"><strong>Breakfast:</strong> ${data.diet.breakfast}</div>
            <div class="mb-4"><strong>Lunch:</strong> ${data.diet.lunch}</div>
            <div class="mb-4"><strong>Dinner:</strong> ${data.diet.dinner}</div>
        `;
        html += '</div></div>';
        
        html += '</div>';
        container.innerHTML = html;

    } catch (e) {
        container.innerHTML = '<p>Something went wrong generating your plan. Please try again.</p>';
        console.error(e);
    }
}

// Chat Functions
function toggleChat() {
    const modal = document.getElementById('chat-modal');
    modal.style.display = modal.style.display === 'none' || modal.style.display === '' ? 'flex' : 'none';
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const messagesDiv = document.getElementById('chat-messages');
    
    // Add User Message
    messagesDiv.innerHTML += `
        <div style="background: var(--accent); color: white; padding: 10px; border-radius: 8px; align-self: flex-end; max-width: 80%;">
            ${message}
        </div>
    `;
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Call API
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: message }) // In real app, send history too
        });
        const data = await response.json();
        
        // Add AI Message
        messagesDiv.innerHTML += `
            <div style="background: #334155; padding: 10px; border-radius: 8px; align-self: flex-start; max-width: 80%;">
                ${data.reply || data.error}
            </div>
        `;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (e) {
        console.error(e);
    }
}

// Allow Enter key to send
document.getElementById('chat-input')?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});