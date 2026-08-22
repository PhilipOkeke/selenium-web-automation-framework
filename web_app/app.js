const TASKS_ENDPOINT = "/api/v1/tasks";
const AUTH_REGISTER_ENDPOINT = "/api/v1/auth/register";
const AUTH_TOKEN_ENDPOINT = "/api/v1/auth/token";
const AUTOMATION_EMAIL = "selenium@example.com";
const AUTOMATION_PASSWORD = "AutomationTest123!";

let accessToken = null;

const elements = {
  apiStatus: document.querySelector("#api-status"),
  form: document.querySelector("#task-form"),
  title: document.querySelector("#task-title"),
  description: document.querySelector("#task-description"),
  priority: document.querySelector("#task-priority"),
  search: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  priorityFilter: document.querySelector("#priority-filter"),
  list: document.querySelector("#task-list"),
  emptyState: document.querySelector("#empty-state"),
  count: document.querySelector("#task-count"),
  toast: document.querySelector("#toast"),
};

document.addEventListener("DOMContentLoaded", initialize);

async function initialize() {
  elements.form.addEventListener("submit", createTask);
  elements.search.addEventListener("input", loadTasks);
  elements.statusFilter.addEventListener("change", loadTasks);
  elements.priorityFilter.addEventListener("change", loadTasks);

  await authenticate();
  await checkApiHealth();
  await loadTasks();
}

async function authenticate() {
  const registration = await fetch(AUTH_REGISTER_ENDPOINT, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      email: AUTOMATION_EMAIL,
      password: AUTOMATION_PASSWORD,
      full_name: "Selenium Browser User",
    }),
  });

  if (!registration.ok && ![400, 409].includes(registration.status)) {
    const body = await registration.json();
    throw new Error(errorMessage(body));
  }

  const tokenBody = new URLSearchParams({
    username: AUTOMATION_EMAIL,
    password: AUTOMATION_PASSWORD,
  });
  const response = await fetch(AUTH_TOKEN_ENDPOINT, {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: tokenBody,
  });

  if (!response.ok) {
    const body = await response.json();
    throw new Error(errorMessage(body));
  }

  accessToken = (await response.json()).access_token;
}

function authHeaders(headers = {}) {
  return {
    ...headers,
    ...(accessToken ? {Authorization: "Bearer " + accessToken} : {}),
  };
}

async function checkApiHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Health check failed");
    elements.apiStatus.textContent = "API connected";
    elements.apiStatus.classList.remove("error");
  } catch (error) {
    elements.apiStatus.textContent = "API unavailable";
    elements.apiStatus.classList.add("error");
    showToast(error.message, true);
  }
}

async function loadTasks() {
  elements.list.setAttribute("aria-busy", "true");
  const query = new URLSearchParams();
  if (elements.search.value.trim()) query.set("search", elements.search.value.trim());
  if (elements.statusFilter.value) query.set("status", elements.statusFilter.value);
  if (elements.priorityFilter.value) query.set("priority", elements.priorityFilter.value);
  query.set("limit", "100");

  try {
    const response = await fetch(`${TASKS_ENDPOINT}?${query}`, {
      headers: authHeaders(),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(errorMessage(body));
    renderTasks(body.items);
    elements.count.textContent = String(body.total);
  } catch (error) {
    renderTasks([]);
    elements.count.textContent = "0";
    showToast(error.message, true);
  } finally {
    elements.list.setAttribute("aria-busy", "false");
  }
}

async function createTask(event) {
  event.preventDefault();
  if (!elements.form.reportValidity()) return;

  const payload = {
    title: elements.title.value.trim(),
    description: elements.description.value.trim() || null,
    priority: elements.priority.value,
    status: "todo",
  };

  try {
    await apiRequest(TASKS_ENDPOINT, {method: "POST", body: JSON.stringify(payload)});
    elements.form.reset();
    showToast("Task created");
    await loadTasks();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function updateTask(taskId, status) {
  try {
    await apiRequest(`${TASKS_ENDPOINT}/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({status}),
    });
    showToast("Task updated");
    await loadTasks();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function deleteTask(taskId, title) {
  if (!window.confirm(`Delete “${title}”?`)) return;

  try {
    await apiRequest(`${TASKS_ENDPOINT}/${taskId}`, {method: "DELETE"});
    showToast("Task deleted");
    await loadTasks();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: authHeaders({
      "Content-Type": "application/json",
      ...(options.headers || {}),
    }),
  });

  if (!response.ok) {
    const body = await response.json();
    throw new Error(errorMessage(body));
  }

  return response.status === 204 ? null : response.json();
}

function renderTasks(tasks) {
  elements.list.replaceChildren();
  elements.emptyState.hidden = tasks.length !== 0;

  for (const task of tasks) {
    const card = document.createElement("article");
    card.className = "task-card";
    card.dataset.taskId = String(task.id);

    const content = document.createElement("div");
    const title = document.createElement("h3");
    title.className = "task-title";
    title.textContent = task.title;
    const description = document.createElement("p");
    description.className = "task-description";
    description.textContent = task.description || "No description";
    content.append(title, description);

    const meta = document.createElement("div");
    meta.className = "task-meta";
    const priority = document.createElement("span");
    priority.className = `task-priority ${task.priority}`;
    priority.textContent = task.priority;

    const status = document.createElement("select");
    status.className = "task-status-select";
    status.setAttribute("aria-label", `Status for ${task.title}`);
    for (const [value, label] of [
      ["todo", "To do"],
      ["in_progress", "In progress"],
      ["done", "Done"],
    ]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      option.selected = task.status === value;
      status.append(option);
    }
    status.addEventListener("change", () => updateTask(task.id, status.value));
    meta.append(priority, status);

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-task";
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("aria-label", `Delete ${task.title}`);
    deleteButton.addEventListener("click", () => deleteTask(task.id, task.title));

    card.append(content, meta, deleteButton);
    elements.list.append(card);
  }
}

function errorMessage(body) {
  if (typeof body.detail === "string") return body.detail;
  return "The request could not be completed";
}

let toastTimer;
function showToast(message, isError = false) {
  window.clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", isError);
  elements.toast.hidden = false;
  toastTimer = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 3000);
}
