const API_BASE = window.location.origin || "http://127.0.0.1:8000";

const CHART_COLORS = [
  "#4F46E5",
  "#6366F1",
  "#818CF8",
  "#F59E0B",
  "#10B981",
  "#EF4444",
  "#8B5CF6",
  "#EC4899",
];

function formatCurrency(amount) {
  return `₹${Number(amount).toLocaleString("en-IN")}`;
}

let categoryChart = null;

function renderBreakdownList(breakdown) {
  const entries = Object.entries(breakdown).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((sum, [, amt]) => sum + amt, 0);

  return entries
    .map(([category, amount], i) => {
      const pct = total ? Math.round((amount / total) * 100) : 0;
      const color = CHART_COLORS[i % CHART_COLORS.length];
      return `
        <div class="breakdown-row mb-3">
          <div class="d-flex justify-content-between mb-1">
            <span>
              <span class="color-dot" style="background:${color}"></span>
              ${category}
            </span>
            <span class="fw-semibold">${formatCurrency(amount)} <small class="text-muted">(${pct}%)</small></span>
          </div>
          <div class="progress" style="height: 6px">
            <div class="progress-bar" style="width:${pct}%; background:${color}"></div>
          </div>
        </div>`;
    })
    .join("");
}

function renderChart(breakdown) {
  const labels = Object.keys(breakdown);
  const values = Object.values(breakdown);
  const ctx = document.getElementById("categoryChart");

  if (categoryChart) categoryChart.destroy();

  categoryChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: CHART_COLORS.slice(0, labels.length),
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

function renderTable(transactions) {
  return transactions
    .map(
      (tx, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${tx.merchant || "—"}</td>
      <td><span class="badge bg-light text-dark">${tx.category || "Unknown"}</span></td>
      <td class="text-end fw-semibold">${formatCurrency(tx.amount || 0)}</td>
    </tr>`
    )
    .join("");
}

async function loadHistory() {
  const loading = document.getElementById("loadingState");
  const empty = document.getElementById("emptyState");
  const content = document.getElementById("historyContent");

  try {
    const [txRes, summaryRes] = await Promise.all([
      fetch(`${API_BASE}/transactions`),
      fetch(`${API_BASE}/history-summary`),
    ]);

    const transactions = txRes.ok ? await txRes.json() : [];
    const breakdown = summaryRes.ok ? await summaryRes.json() : {};

    loading.style.display = "none";

    if (!transactions.length) {
      empty.style.display = "block";
      return;
    }

    const totalSpent = Object.values(breakdown).reduce((s, v) => s + v, 0);

    document.getElementById("totalCount").textContent = transactions.length;
    document.getElementById("categoryCount").textContent = Object.keys(breakdown).length;
    document.getElementById("totalSpent").textContent = formatCurrency(totalSpent);
    document.getElementById("breakdownList").innerHTML = renderBreakdownList(breakdown);
    document.getElementById("transactionTable").innerHTML = renderTable(transactions);

    if (Object.keys(breakdown).length > 0) {
      renderChart(breakdown);
    }

    content.style.display = "block";
  } catch {
    loading.style.display = "none";
    empty.style.display = "block";
    empty.querySelector("p").textContent =
      "Could not load history. Make sure the backend is running.";
  }
}

loadHistory();
