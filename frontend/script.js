// Backend API URLs
const ANALYZE_URL = "http://127.0.0.1:8000/api/tasks/analyze/";
const SUGGEST_URL = "http://127.0.0.1:8000/api/tasks/suggest/";

// DOM elements
const addTaskBtn = document.getElementById("addTaskBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const suggestBtn = document.getElementById("suggestBtn");
const strategySelect = document.getElementById("strategySelect");
const statusBar = document.getElementById("statusBar");
const resultsContainer = document.getElementById("resultsContainer");
const resultsSummary = document.getElementById("resultsSummary");
const taskList = document.getElementById("taskList");

// Store tasks added from the form
var taskArray = [];
// Store last analyzed/suggested result from backend
var analyzedResults = [];

// Helper: show status message at the bottom of left panel
function setStatus(message, type) {
  statusBar.textContent = message || "";
  statusBar.className = "status-bar";

  if (type === "error") {
    statusBar.classList.add("status-error");
  } else if (type === "success") {
    statusBar.classList.add("status-success");
  }
}

// Render list of tasks user has added (left panel)
function renderTaskList() {
  taskList.innerHTML = "";

  if (taskArray.length === 0) {
    taskList.innerHTML =
      "<p style='color:#6b7280;font-size:12px;'>No tasks added yet.</p>";
    return;
  }

  for (var i = 0; i < taskArray.length; i++) {
    var task = taskArray[i];
    var div = document.createElement("div");
    div.className = "task-list-item";

    var text = document.createElement("span");
    text.textContent = task.title + " — Due: " + task.due_date;

    var btn = document.createElement("button");
    btn.textContent = "Remove";
    btn.setAttribute("data-index", i);
    btn.addEventListener("click", function (e) {
      var index = parseInt(e.target.getAttribute("data-index"));
      removeTask(index);
    });

    div.appendChild(text);
    div.appendChild(btn);
    taskList.appendChild(div);
  }
}

// Remove one task from the list
function removeTask(index) {
  taskArray.splice(index, 1);
  renderTaskList();
}

// Add task from form to taskArray
addTaskBtn.addEventListener("click", function () {
  var title = document.getElementById("title").value.trim();
  var due_date = document.getElementById("due_date").value;
  var importance = parseInt(document.getElementById("importance").value, 10);
  var estimated_hours = parseFloat(
    document.getElementById("estimated_hours").value
  );
  var dependenciesRaw = document.getElementById("dependencies").value.trim();

  if (!title || !due_date || isNaN(importance) || isNaN(estimated_hours)) {
    setStatus("Please fill all required fields (title, due date, importance, hours).", "error");
    return;
  }

  var dependencies = [];
  if (dependenciesRaw) {
    var parts = dependenciesRaw.split(",");
    for (var i = 0; i < parts.length; i++) {
      var d = parts[i].trim();
      if (d) {
        dependencies.push(d);
      }
    }
  }

  var task = {
    title: title,
    due_date: due_date,
    importance: importance,
    estimated_hours: estimated_hours,
    dependencies: dependencies
  };

  taskArray.push(task);
  renderTaskList();
  setStatus("Task added.", "success");

  // reset only some fields
  document.getElementById("title").value = "";
  document.getElementById("dependencies").value = "";
});

// Call backend /tasks/analyze/ with current taskArray
analyzeBtn.addEventListener("click", function () {
  if (taskArray.length === 0) {
    setStatus("Add at least one task before analyzing.", "error");
    return;
  }

  setStatus("Analyzing tasks...");

  fetch(ANALYZE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(taskArray)
  })
    .then(function (res) {
      if (!res.ok) {
        throw new Error("Server returned " + res.status);
      }
      return res.json();
    })
    .then(function (data) {
      analyzedResults = data;
      renderResults();
      setStatus("Analysis complete.", "success");
    })
    .catch(function (error) {
      console.error(error);
      setStatus("Failed to analyze tasks. Check server and CORS settings.", "error");
    });
});

// Call backend /tasks/suggest/
suggestBtn.addEventListener("click", function () {
  setStatus("Fetching suggested tasks...");

  fetch(SUGGEST_URL)
    .then(function (res) {
      if (!res.ok) {
        throw new Error("Server returned " + res.status);
      }
      return res.json();
    })
    .then(function (data) {
      analyzedResults = data;
      renderResults();
      setStatus("Loaded suggested tasks.", "success");
    })
    .catch(function (error) {
      console.error(error);
      setStatus("Failed to fetch suggestions.", "error");
    });
});

// Re-render results when strategy is changed
strategySelect.addEventListener("change", function () {
  if (analyzedResults.length > 0) {
    renderResults();
  }
});

// Decide priority level based on score
function getPriorityLevel(score) {
  if (score >= 120) {
    return "high";
  } else if (score >= 80) {
    return "medium";
  } else {
    return "low";
  }
}

// Sort tasks based on dropdown strategy
function sortTasksByStrategy(tasks, strategy) {
  var arr = tasks.slice(); // copy

  if (strategy === "fastest") {
    arr.sort(function (a, b) {
      return (a.estimated_hours || 0) - (b.estimated_hours || 0);
    });
  } else if (strategy === "impact") {
    arr.sort(function (a, b) {
      return (b.importance || 0) - (a.importance || 0);
    });
  } else if (strategy === "deadline") {
    arr.sort(function (a, b) {
      var da = new Date(a.due_date);
      var db = new Date(b.due_date);
      return da - db;
    });
  } else {
    // smart balance - use backend score
    arr.sort(function (a, b) {
      return (b.priority_score || 0) - (a.priority_score || 0);
    });
  }

  return arr;
}

// Render results on the right side
function renderResults() {
  resultsContainer.innerHTML = "";

  if (!analyzedResults || analyzedResults.length === 0) {
    resultsContainer.innerHTML =
      "<div class='empty-state'><h3>No results yet</h3><p>Analyze tasks or get suggestions.</p></div>";
    resultsSummary.textContent = "";
    return;
  }

  var strategy = strategySelect.value;
  var tasks = sortTasksByStrategy(analyzedResults, strategy);

  resultsSummary.textContent =
    tasks.length + " task(s) · Strategy: " + strategy;

  for (var i = 0; i < tasks.length; i++) {
    var t = tasks[i];
    var score = t.priority_score || 0;
    var level = getPriorityLevel(score);

    var card = document.createElement("div");
    card.className = "task-card " + level;

    var headerDiv = document.createElement("div");
    headerDiv.className = "task-header";

    var titleEl = document.createElement("h3");
    titleEl.className = "task-title";
    titleEl.textContent = t.title || "(No title)";

    var pill = document.createElement("span");
    pill.className = "priority-pill " + level;
    pill.textContent = level.toUpperCase();

    headerDiv.appendChild(titleEl);
    headerDiv.appendChild(pill);

    var scoreDiv = document.createElement("div");
    scoreDiv.className = "task-score";
    scoreDiv.textContent = "Score: " + score;

    var metaDiv = document.createElement("div");
    metaDiv.className = "task-meta";
    metaDiv.innerHTML =
      "<span><strong>Due:</strong> " + (t.due_date || "N/A") + "</span>" +
      "<span><strong>Importance:</strong> " + (t.importance || "N/A") + "</span>" +
      "<span><strong>Effort:</strong> " + (t.estimated_hours || "N/A") + "h</span>";

    var reasonDiv = document.createElement("div");
    reasonDiv.className = "task-reason";
    reasonDiv.textContent = t.reason || "";

    card.appendChild(headerDiv);
    card.appendChild(scoreDiv);
    card.appendChild(metaDiv);
    card.appendChild(reasonDiv);

    resultsContainer.appendChild(card);
  }
}

// Initial left list render
renderTaskList();
