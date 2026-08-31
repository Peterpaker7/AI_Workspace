// script.js

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadSection = document.getElementById('upload-section');
    const dashboard = document.getElementById('dashboard');
    const resetBtn = document.getElementById('reset-btn');
    const loading = document.getElementById('loading');

    // UI Elements for Data
    const flirtScoreEl = document.getElementById('flirt-score');
    const flirtProgressEl = document.getElementById('flirt-progress');
    const totalMessagesEl = document.getElementById('total-messages');
    const totalMediaEl = document.getElementById('total-media');
    const totalCallsEl = document.getElementById('total-calls');
    const flirtMessagesListEl = document.getElementById('flirt-messages-list');
    const jsonViewerEl = document.getElementById('json-viewer');

    // API URL
    const API_URL = 'http://127.0.0.1:5000/analyze';

    // Event Listeners for file upload
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag and Drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // Reset workflow
    resetBtn.addEventListener('click', () => {
        dashboard.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    });

    async function handleFileUpload(file) {
        if (!file.name.toLowerCase().endsWith('.txt')) {
            alert('Please upload a valid WhatsApp .txt file.');
            return;
        }

        // Show loading state
        dropzone.classList.add('hidden');
        loading.classList.remove('hidden');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to analyze the chat');
            }

            populateDashboard(data);

            // Hide upload, show dashboard
            uploadSection.classList.add('hidden');
            dashboard.classList.remove('hidden');
        } catch (error) {
            console.error(error);
            alert('Error analyzing chat: ' + error.message);
        } finally {
            // Restore upload state
            dropzone.classList.remove('hidden');
            loading.classList.add('hidden');
        }
    }

    function populateDashboard(data) {
        // Safe access helper
        const getVal = (obj, path, def = 0) => {
            return path.split('.').reduce((o, i) => (o ? o[i] : null), obj) ?? def;
        };

        // Populate basic stats (extracting from the response)
        // Wait, the API returns: statistics, activity, media, calls, flirt

        const totalMessages = getVal(data, 'statistics.total_messages') || getVal(data, 'flirt.messages_analyzed');
        const mediaCount = getVal(data, 'media.total_media') || Object.values(getVal(data, 'media', {})).reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0) || '0';
        const callsCount = getVal(data, 'calls.total_calls') || Object.values(getVal(data, 'calls', {})).reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0) || '0';

        totalMessagesEl.textContent = totalMessages.toLocaleString();
        totalMediaEl.textContent = mediaCount.toLocaleString();
        totalCallsEl.textContent = callsCount.toLocaleString();

        // Populate Flirt Score
        const flirtObj = data.flirt || {};
        let score = flirtObj.conversation_flirt_score || 0;

        // Ensure score is between 0 and 100 for percentage
        if (score <= 1) score = Math.round(score * 100);

        // Animate score counter
        animateValue(flirtScoreEl, 0, score, 2000, '%');

        // Delay progress bar for effect
        setTimeout(() => {
            flirtProgressEl.style.width = `${score}%`;
        }, 300);

        // Flirt Messages List
        const messages = flirtObj.messages || [];
        // Sort by flirt score descending
        const topMessages = [...messages]
            .filter(m => m.flirt_score > 0.1) // Only show somewhat flirty
            .sort((a, b) => b.flirt_score - a.flirt_score)
            .slice(0, 50); // Get top 50

        flirtMessagesListEl.innerHTML = '';

        if (topMessages.length === 0) {
            flirtMessagesListEl.innerHTML = '<div class="error-msg">No flirty messages found in this chat! 🧊</div>';
        } else {
            topMessages.forEach((msg, index) => {
                const s = msg.flirt_score <= 1 ? Math.round(msg.flirt_score * 100) : Math.round(msg.flirt_score);
                const el = document.createElement('div');
                el.className = 'msg-item';
                // stagger animation delay
                el.style.animationDelay = `${index * 0.05}s`;
                el.style.animation = `fadeInDown 0.5s ease forwards`;
                el.style.opacity = '0';

                el.innerHTML = `
                    <div class="msg-header">
                        <span class="msg-sender">${msg.sender || 'Unknown'}</span>
                        <span class="msg-score">🔥 ${s}%</span>
                    </div>
                    <div class="msg-text">${msg.message}</div>
                `;
                flirtMessagesListEl.appendChild(el);
            });
        }

        // Output Raw JSON data minus the big messages array to save space
        const displayData = JSON.parse(JSON.stringify(data));
        if (displayData.flirt && displayData.flirt.messages) {
            displayData.flirt.messages = `[ ${displayData.flirt.messages.length} messages analyzed... ]`;
        }

        jsonViewerEl.textContent = JSON.stringify(displayData, null, 2);
    }

    // Number animation utility
    function animateValue(obj, start, end, duration, suffix = '') {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start) + suffix;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
