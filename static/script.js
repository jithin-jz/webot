document.addEventListener('DOMContentLoaded', function() {
    // Login form validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="loading"></div>';
        });
    }

    // Task management
    let currentTaskInterval = null;

    function startTask(endpoint, form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loading"></div>';
        
        fetch(`/api/${endpoint}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                startStatusUpdates();
            }
        })
        .catch(error => {
            showError('Failed to start task');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Start';
        });
        
        return false;
    }

    function stopTask() {
        fetch('/api/stop_task', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            }
        })
        .catch(error => {
            showError('Failed to stop task');
        });
    }

    function startStatusUpdates() {
        if (currentTaskInterval) {
            clearInterval(currentTaskInterval);
        }
        
        updateTaskStatus();
        currentTaskInterval = setInterval(updateTaskStatus, 2000);
    }

    function updateTaskStatus() {
        fetch('/api/task_status')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                const statusDiv = document.getElementById('taskStatus');
                if (data.status === 'no_task') {
                    statusDiv.innerHTML = '<p class="status-item">No task running</p>';
                    clearInterval(currentTaskInterval);
                    currentTaskInterval = null;
                } else {
                    let html = `<p class="status-item font-bold ${data.status === 'running' ? 'text-blue-600' : 'text-green-600'}">
                        Status: ${data.status}</p>`;
                    
                    if (data.results) {
                        html += '<div class="status-content">';
                        data.results.forEach(result => {
                            html += `<p class="status-item">${result}</p>`;
                        });
                        html += '</div>';
                    }
                    
                    statusDiv.innerHTML = html;
                    
                    if (data.status !== 'running') {
                        clearInterval(currentTaskInterval);
                        currentTaskInterval = null;
                    }
                }
            })
            .catch(error => {
                showError('Failed to get task status');
                clearInterval(currentTaskInterval);
                currentTaskInterval = null;
            });
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.textContent = message;
        
        const container = document.querySelector('.main-content') || document.body;
        container.insertBefore(errorDiv, container.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Attach event listeners to all task forms
    document.querySelectorAll('[data-task-form]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            startTask(this.dataset.taskEndpoint, this);
        });
    });

    // Attach event listener to stop button
    const stopButton = document.getElementById('stopTask');
    if (stopButton) {
        stopButton.addEventListener('click', stopTask);
    }

    // Start status updates if we're on the dashboard
    if (document.getElementById('taskStatus')) {
        startStatusUpdates();
    }
});
