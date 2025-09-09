let currentJobId = null;
let pollTimer = null;

async function startScrape() {
  const username = document.getElementById("username").value.trim();
  const ig_user = document.getElementById("ig_user").value.trim();
  const ig_pass = document.getElementById("ig_pass").value.trim();
  const max_posts = parseInt(document.getElementById("max_posts").value, 10) || 50;
  const only_videos = document.getElementById("only_videos").checked;

  if (!username) {
    alert("Username wajib diisi.");
    return;
  }

  document.getElementById("startBtn").disabled = true;
  setStatus("Mengajukan job…", "running");

  const resp = await fetch("/api/scrape", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, ig_user, ig_pass, max_posts, only_videos })
  });

  const data = await resp.json();
  if (!resp.ok) {
    setStatus(data.error || "Gagal membuat job", "error");
    document.getElementById("startBtn").disabled = false;
    return;
  }

  currentJobId = data.job_id;
  pollStatus();
}

async function pollStatus() {
  if (!currentJobId) return;
  clearTimeout(pollTimer);

  const resp = await fetch(`/api/status/${currentJobId}`);
  const data = await resp.json();
  const status = data.status || "-";
  const detail = data.detail || {};
  setStatus(detail.message || "", status);

  if (status === "finished") {
    await loadResults();
    showDownload();
    document.getElementById("startBtn").disabled = false;
  } else if (status === "running") {
    pollTimer = setTimeout(pollStatus, 2000);
  } else if (status === "error") {
    document.getElementById("startBtn").disabled = false;
  }
}

async function loadResults() {
  const resp = await fetch(`/api/results/${currentJobId}`);
  const data = await resp.json();
  const items = data.items || [];
  const tbody = document.getElementById("resultRows");
  tbody.innerHTML = "";
  for (const it of items) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${it.date_utc || ""}</td>
      <td><span class="pill">${it.shortcode || ""}</span></td>
      <td>${it.is_video ? "✅" : "❌"}</td>
      <td><a href="${it.url}" target="_blank" rel="noopener">Buka</a></td>
    `;
    tbody.appendChild(tr);
  }
  document.getElementById("resultBox").style.display = "block";
}

function setStatus(msg, status) {
  document.getElementById("status").textContent = status || "-";
  document.getElementById("statusMessage").textContent = msg || "";
}

function showDownload() {
  const box = document.getElementById("downloadArea");
  box.innerHTML = `<a class="btn" href="/download/${currentJobId}.zip">Unduh ZIP</a>`;
}

document.getElementById("startBtn").addEventListener("click", startScrape);
