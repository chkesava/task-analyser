// script.js
let tasks = [];
let analyzedResults = [];
let currentSortStrategy = 'smart';

const API_BASE = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    updateTaskList();
    updateResults();
});

function initEventListeners() {
    document.getElementById('addTaskBtn').addEventListener('click', addTask);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeTasks);
    document.getElementById('suggestBtn').addEventListener('click', getSuggestions);
    document.getElementById('sortStrategy').addEventListener('change', function() {
        currentSortStrategy = this.value;
        updateResults();
    });
}

function addTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const dueDate = document.getElementById('dueDate').value;
    const importance = parseInt(document.getElementById('importance').value);
    const estimatedHours = parseInt(document.getElementById('estimatedHours').value);
    const dependenciesInput = document.getElementById('dependencies').value.trim();

    if (!title || !dueDate || !importance || !estimatedHours) {
        showStatus('Please fill all required fields.', 'error');
        return;
    }

    const dependencies = dependenciesInput 
        ? dependenciesInput.split(',').map(d => d.trim()).filter(d => d)
        : [];

    const task = {
        title,
        due_date: dueDate,
        importance,
        estimated_hours: estimatedHours,
        dependencies
    };

    tasks.push(task);
    updateTaskList();
    clearInputs();
    showStatus('Task added.', 'success');
}

function analyzeTasks() {
    if (tasks.length === 0) {
        showStatus('Please add some tasks first.', 'error');
        return;
    }

    showStatus('Analyzing tasks...', 'success');

    fetch(`${API_BASE}/tasks/analyze/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tasks)
    })
    .then(response => response.json())
    .then(data => {
        analyzedResults = data;
        updateResults();
        showStatus('Analysis complete.', 'success');
    })
    .catch(error => {
        showStatus('Analysis failed. Check if backend is running.', 'error');
        console.error('Analysis error:', error);
    });
}

function getSuggestions() {
    showStatus('Fetching suggestions...', 'success');

    fetch(`${API_BASE}/tasks/suggest/`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showStatus(data.error, 'error');
            return;
        }
        analyzedResults = data;
        updateResults();
        showStatus('Suggestions loaded.', 'success');
    })
    .catch(error => {
        showStatus('Failed to fetch suggestions.', 'error');
        console.error('Suggestions error:', error);
    });
}

function updateTaskList() {
    const taskCount = document.getElementById('taskCount');
    const tasksList = document.getElementById('tasksList');
    
    taskCount.textContent = tasks.length;
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<div style="color: #9ca3af; padding: 20px;">No tasks added yet.</div>';
        return;
    }

    tasksList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <span>${task.title} — Due: ${task.due_date}</span>
            <button class="remove-btn" onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

function removeTask(index) {
    tasks.splice(index, 1);
    updateTaskList();
    showStatus('Task removed.', 'success');
}

function updateResults() {
    const summary = document.getElementById('resultsSummary');
    const content = document.getElementById('resultsContent');
    const strategyNames = {
        smart: 'Smart Balance',
        fastest: 'Fastest Wins',
        impact: 'High Impact',
        deadline: 'Deadline Driven'
    };

    if (analyzedResults.length === 0) {
        summary.innerHTML = '';
        content.innerHTML = '<div class="empty-state">No tasks analyzed yet. Add tasks or fetch suggestions to see results.</div>';
        return;
    }

    // Sort results based on strategy
    let sortedResults = [...analyzedResults];
    switch(currentSortStrategy) {
        case 'fastest':
            sortedResults.sort((a, b) => a.estimated_hours - b.estimated_hours);
            break;
        case 'impact':
            sortedResults.sort((a, b) => b.importance - a.importance);
            break;
        case 'deadline':
            sortedResults.sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
            break;
        default:
            sortedResults.sort((a, b) => b.priority_score - a.priority_score);
    }

    summary.innerHTML = `${sortedResults.length} tasks · Strategy: ${strategyNames[currentSortStrategy]}`;

    content.innerHTML = sortedResults.map(task => {
        const priority = getPriorityLevel(task.priority_score);
        return `
            <div class="priority-card ${priority}">
                <h4>${task.title}</h4>
                <span class="priority-pill pill-${priority}">${priority.toUpperCase()}</span>
                <div class="score">Score: ${task.priority_score}</div>
                <div class="metadata">
                    <span>Due: ${task.due_date}</span>
                    <span>Importance: ${task.importance}</span>
                    <span>${task.estimated_hours}h</span>
                </div>
                <div class="reason">${task.reason}</div>
            </div>
        `;
    }).join('');
}

function getPriorityLevel(score) {
    if (score >= 90) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function clearInputs() {
    document.getElementById('taskTitle').value = '';
    document.getElementById('dueDate').value = '';
    document.getElementById('importance').value = 5;
    document.getElementById('estimatedHours').value = 1;
    document.getElementById('dependencies').value = '';
}

function showStatus(message, type) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    
    setTimeout(() => {
        statusEl.textContent = '';
        statusEl.className = 'status';
    }, 5000);
}
