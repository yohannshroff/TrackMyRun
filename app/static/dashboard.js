const token = localStorage.getItem("token");
const USER_ID = "me";

if (!token) {
    window.location.href = "/";
    throw new Error("Missing authentication token");
}

function redirectToLogin() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function authFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...(options.headers || {})
        }
    });

    if (response.status === 401) {
        redirectToLogin();
        throw new Error("Authentication required");
    }

    return response;
}

async function loadQuote() {
    const res = await authFetch("/quotes/random");
    const data = await res.json();

    document.getElementById("quote").innerText = data.quote;
}

async function loadStats() {
    const res = await authFetch(`/users/${USER_ID}/stats`);
    const stats = await res.json();

    document.getElementById("stats").innerHTML = `
        <p>Total Runs: ${stats.total_runs || 0}</p>
        <p>Total Distance: ${stats.total_distance || 0}</p>
        <p>Total Duration: ${stats.total_duration || 0}</p>
        <p>Average Pace: ${(stats.avg_pace || 0).toFixed(2)}</p>
        <p>Consistency: ${stats.consistency || 0}%</p>
        <p>Max Pace: ${(stats.max_pace || 0).toFixed(2)}</p>
        <p>Max Distance: ${stats.max_distance || 0}</p>
        <p>Max Duration: ${stats.max_duration || 0}</p>
    `;
}

async function loadLogs() {
    const res = await authFetch(`/users/${USER_ID}/logs`);
    const logs = await res.json();

    const tbody = document.querySelector("#logsTable tbody");

    tbody.innerHTML = "";

    logs.forEach(log => {
        tbody.innerHTML += `
        <tr>
            <td>${log.date}</td>
            <td>${log.place}</td>
            <td>${log.pace}</td>
            <td>${log.distance}</td>
            <td>${log.duration}</td>
            <td>
                <button onclick="deleteLog('${log.logid}')">
                    Delete
                </button>
            </td>
        </tr>
        `;
    });
}

async function deleteLog(logid) {
    const res = await authFetch(`/users/${USER_ID}/logs/${logid}`, {
        method: "DELETE"
    });

    if (!res.ok) return;

    loadLogs();
    loadStats();
}

document.getElementById("logForm")
.addEventListener("submit", async (e) => {

    e.preventDefault();

    const res = await authFetch(`/users/${USER_ID}/logs`, {
        method: "POST",
        body: JSON.stringify({
            distance: document.getElementById("distance").value,
            duration: document.getElementById("duration").value,
            place: document.getElementById("place").value,
            date: document.getElementById("date").value
        })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("message").innerText =
            data.detail || "Could not save workout";
        return;
    }

    document.getElementById("message").innerText =
        data.message;

    loadLogs();
    loadStats();
});

loadQuote();
loadStats();
loadLogs();
