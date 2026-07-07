const API_BASE = window.API_BASE;

function formatCurrency(amount) {
  return `₹${Number(amount).toLocaleString("en-IN")}`;
}

function showStatus(el, message, type) {
  el.className = `mt-3 alert alert-${type}`;
  el.textContent = message;
}

function formatAmount(value) {
  return `₹${Number(value || 0).toLocaleString("en-IN")}`;
}

function renderTransactions(transactions) {
  if (!transactions || transactions.length === 0) {
    return '<p class="text-muted mb-0">No transactions parsed.</p>';
  }

  return `
    <div class="table-responsive">
      <table class="table table-sm align-middle mb-0">
        <thead>
          <tr>
            <th>Merchant</th>
            <th>Category</th>
            <th class="text-end">Amount</th>
          </tr>
        </thead>
        <tbody>
          ${transactions
            .map(
              (tx) => `
            <tr>
              <td>${tx.merchant || "—"}</td>
              <td><span class="badge bg-light text-dark">${tx.category || "Unknown"}</span></td>
              <td class="text-end fw-semibold">${formatCurrency(tx.amount || 0)}</td>
            </tr>`,
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

function renderBreakdown(breakdown) {
  const entries = Object.entries(breakdown || {});
  if (entries.length === 0) {
    return '<p class="text-muted mb-0">No breakdown available.</p>';
  }

  const total = entries.reduce((sum, [, amt]) => sum + amt, 0);

  return entries
    .map(([category, amount]) => {
      const pct = total ? Math.round((amount / total) * 100) : 0;
      return `
        <div class="breakdown-row">
          <div class="d-flex justify-content-between mb-1">
            <span>${category}</span>
            <span class="fw-semibold">${formatCurrency(amount)}</span>
          </div>
          <div class="progress" style="height: 6px">
            <div class="progress-bar" style="width: ${pct}%"></div>
          </div>
        </div>`;
    })
    .join("");
}

function renderAllocation(allocation) {
  if (!allocation || Object.keys(allocation).length === 0) {
    return '<p class="text-muted mb-0">No allocation data.</p>';
  }

  return Object.entries(allocation)
    .map(
      ([asset, value]) => `
      <div class="d-flex justify-content-between py-2 border-bottom">
        <span class="text-capitalize">${asset.replace(/_/g, " ")}</span>
        <span class="fw-semibold">${typeof value === "number" ? formatCurrency(value) : value}</span>
      </div>`,
    )
    .join("");
}

function renderRagContext(context) {
  if (!context || context.length === 0) {
    return '<p class="text-muted mb-0">No knowledge retrieved.</p>';
  }

  return context
    .map((item, i) => `<p class="mb-2"><strong>${i + 1}.</strong> ${item}</p>`)
    .join("");
}

async function loadProfile() {
  const statusEl = document.getElementById("profileStatus");

  try {
    const res = await fetch(`${API_BASE}/profile`, {
      headers: auth.authHeaders(),
    });
    if (!res.ok) {
      const error = await res.json();

      showStatus(
        statusEl,
        error.detail || "Unable to load your profile.",
        "warning",
      );

      return;
    }

    const profile = await res.json();
    if (!profile || Object.keys(profile).length === 0) {
      showStatus(
        statusEl,
        "No profile found yet. Save your details to personalize your advice.",
        "info",
      );
      return;
    }

    document.getElementById("name").value = profile.name || "";
    document.getElementById("age").value = profile.age || "";
    document.getElementById("income").value = profile.monthly_income || "";
    document.getElementById("risk").value = profile.risk_appetite || "Medium";
    document.getElementById("goal").value = profile.goal || "";

    const monthlySpend = Number(profile.monthly_spend || 0);
    const monthlyIncome = Number(profile.monthly_income || 0);
    const monthlySavings = Math.max(0, monthlyIncome - monthlySpend);

    document.getElementById("monthlySpend").value = formatAmount(monthlySpend);
    document.getElementById("monthlySavings").value =
      formatAmount(monthlySavings);
    document.getElementById("savingStatus").textContent =
      monthlySavings >= 0
        ? `Estimated monthly savings: ${formatAmount(monthlySavings)}`
        : "Your spending appears higher than your income.";

    const avatar = document.getElementById("profileAvatar");
    if (avatar && profile.name) {
      avatar.textContent = profile.name.charAt(0).toUpperCase();
    }

    showStatus(statusEl, "Your saved profile has been loaded.", "success");
  } catch {
    showStatus(
      statusEl,
      "Backend not running. Start the server with: uvicorn app.main:app --reload",
      "warning",
    );
  }
}

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const statusEl = document.getElementById("profileStatus");
  const profile = {
    name: document.getElementById("name").value,
    age: parseInt(document.getElementById("age").value, 10),
    monthly_income: parseFloat(document.getElementById("income").value) || 0,
    monthly_spend:
      parseFloat(
        document.getElementById("monthlySpend").value.replace(/[₹,]/g, ""),
      ) || 0,
    risk_appetite: document.getElementById("risk").value,
    goal: document.getElementById("goal").value,
  };

  try {
    const res = await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: auth.authHeaders(),
      body: JSON.stringify(profile),
    });

    if (res.ok) {
      showStatus(
        statusEl,
        "Profile saved successfully. You can now analyze your transactions.",
        "success",
      );
      const avatar = document.getElementById("profileAvatar");
      if (avatar && profile.name) {
        avatar.textContent = profile.name.charAt(0).toUpperCase();
      }

      const monthlyIncome = Number(profile.monthly_income || 0);
      const monthlySpend = Number(profile.monthly_spend || 0);
      const monthlySavings = Math.max(0, monthlyIncome - monthlySpend);
      document.getElementById("monthlySpend").value =
        formatAmount(monthlySpend);
      document.getElementById("monthlySavings").value =
        formatAmount(monthlySavings);
      document.getElementById("savingStatus").textContent =
        monthlySavings >= 0
          ? `Estimated monthly savings: ${formatAmount(monthlySavings)}`
          : "Your spending appears higher than your income.";
    } else {
      const error = await res.json();

      showStatus(statusEl, error.detail || "Failed to save profile.", "danger");
    }
  } catch (err) {
    showStatus(
      statusEl,
      err.message ||
        "Backend not running. Start the server with: uvicorn app.main:app --reload",
      "warning",
    );

    console.error(err);
  }
});

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const text = document.getElementById("transactionText").value.trim();
  if (!text) {
    alert("Enter transaction text first.");
    return;
  }

  const loading = document.getElementById("loadingSection");
  const results = document.getElementById("analysisResults");
  const btn = document.getElementById("analyzeBtn");

  loading.style.display = "block";
  results.style.display = "none";
  btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/advisor`, {
      method: "POST",
      headers: auth.authHeaders(),
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      const error = await res.json();

      throw new Error(error.detail || "Request failed");
    }

    const data = await res.json();

    document.getElementById("parsedOutput").innerHTML = renderTransactions(
      data.transactions,
    );
    document.getElementById("breakdownOutput").innerHTML = renderBreakdown(
      data.breakdown,
    );
    document.getElementById("allocationOutput").innerHTML = renderAllocation(
      data.allocation,
    );
    document.getElementById("ragOutput").innerHTML = renderRagContext(
      data.rag_context,
    );
    document.getElementById("adviceOutput").textContent =
      data.final_advice || data.advice || "No advice generated.";

    results.style.display = "block";
  } catch (err) {
    alert(err.message);

    console.error(err);
  } finally {
    loading.style.display = "none";
    btn.disabled = false;
  }
});

loadProfile();
