const API = "http://127.0.0.1:8000";

async function loadHealth() {
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();

    updateStatus("fastapiStatus", data.fastapi);
    updateStatus("mongoStatus", data.mongodb);
    updateStatus("langgraphStatus", data.langgraph);
    updateStatus("llmStatus", data.llm);

    const allOk = ["fastapi", "mongodb", "langgraph", "llm"].every(
      (k) => data[k] === "ok"
    );
    const badge = document.getElementById("systemBadge");
    if (badge) {
      badge.className = allOk
        ? "badge bg-success fs-6 px-3 py-2"
        : "badge bg-warning fs-6 px-3 py-2";
      badge.textContent = allOk ? "● System Online" : "● Partially Online";
    }
  } catch {
    ["fastapiStatus", "mongoStatus", "langgraphStatus", "llmStatus"].forEach(
      (id) => updateStatus(id, "down")
    );
    const badge = document.getElementById("systemBadge");
    if (badge) {
      badge.className = "badge bg-danger fs-6 px-3 py-2";
      badge.textContent = "● System Offline";
    }
  }
}

function updateStatus(id, status) {
  const el = document.getElementById(id);
  if (!el) return;

  const isOk = status === "ok";
  el.textContent = isOk
    ? id === "langgraphStatus"
      ? "Active"
      : id === "mongoStatus"
        ? "Connected"
        : id === "llmStatus"
          ? "Ready"
          : "Online"
    : "Offline";
  el.className = isOk ? "status-online" : "status-offline";
}

loadHealth();
