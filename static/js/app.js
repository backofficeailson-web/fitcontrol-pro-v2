/* ===========================================================
   FitControl Pro 2.0 — Application JS
   =========================================================== */

(function () {
  "use strict";

  // ---------- Sidebar mobile toggle ----------
  const sidebar = document.querySelector(".sidebar");
  const toggleBtn = document.querySelector("[data-sidebar-toggle]");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => sidebar.classList.toggle("is-open"));
    document.addEventListener("click", (e) => {
      if (window.innerWidth > 1024) return;
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove("is-open");
      }
    });
  }

  // ---------- Modal ----------
  document.querySelectorAll("[data-modal-open]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const target = document.querySelector(trigger.dataset.modalOpen);
      if (target) target.classList.add("is-open");
    });
  });
  document.querySelectorAll("[data-modal-close]").forEach((closer) => {
    closer.addEventListener("click", () => {
      const modal = closer.closest(".modal-backdrop");
      if (modal) modal.classList.remove("is-open");
    });
  });
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) backdrop.classList.remove("is-open");
    });
  });

  // ---------- Confirm delete ----------
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const message = form.dataset.confirm || "Tem certeza?";
      if (!window.confirm(message)) e.preventDefault();
    });
  });

  // ---------- Auto-dismiss flash ----------
  document.querySelectorAll(".alert.auto-dismiss").forEach((el) => {
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity 400ms ease";
      setTimeout(() => el.remove(), 450);
    }, 5000);
  });

  // ---------- Tabs ----------
  document.querySelectorAll("[data-tabs]").forEach((root) => {
    const tabs = root.querySelectorAll(".tab");
    const panels = root.querySelectorAll("[data-tab-panel]");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        panels.forEach((p) => p.classList.add("hidden"));
        tab.classList.add("active");
        const target = root.querySelector(`[data-tab-panel="${tab.dataset.tab}"]`);
        if (target) target.classList.remove("hidden");
      });
    });
  });

  // ---------- Protocol selector filter ----------
  const protoSearch = document.querySelector("[data-proto-search]");
  if (protoSearch) {
    protoSearch.addEventListener("input", () => {
      const term = protoSearch.value.trim().toLowerCase();
      document.querySelectorAll("[data-proto-card]").forEach((card) => {
        const haystack = (card.dataset.protoSearchable || card.textContent).toLowerCase();
        card.style.display = haystack.includes(term) ? "" : "none";
      });
    });
  }

  // ---------- Apply protocol -> form fields helper ----------
  document.querySelectorAll("[data-apply-protocol]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const chave = btn.dataset.applyProtocol;
      const targetForm = document.querySelector(btn.dataset.targetForm || "form");
      if (!targetForm || !chave) return;
      const hidden = targetForm.querySelector('input[name="protocolo_chave"]');
      if (hidden) hidden.value = chave;
      const select = targetForm.querySelector('select[name="protocolo_chave"]');
      if (select) select.value = chave;
      const modal = btn.closest(".modal-backdrop");
      if (modal) modal.classList.remove("is-open");
      const banner = document.querySelector("[data-protocol-banner]");
      if (banner) {
        banner.textContent = "Protocolo selecionado: " + (btn.dataset.applyName || chave);
        banner.classList.remove("hidden");
      }
    });
  });

  // ---------- Aluno evolução chart loader ----------
  document.querySelectorAll("[data-evolucao-chart]").forEach(async (canvas) => {
    const alunoId = canvas.dataset.evolucaoChart;
    if (!alunoId || !window.Chart) return;
    try {
      const r = await fetch(`/api/alunos/${alunoId}/evolucao`);
      if (!r.ok) return;
      const data = await r.json();
      drawLineChart(canvas, {
        labels: data.labels,
        datasets: [
          { label: "Peso (kg)", data: data.peso, color: "#2dffb3" },
          { label: "% Gordura", data: data.gordura, color: "#22d3ee" },
        ],
      });
    } catch (err) {
      console.warn("Evolução chart falhou:", err);
    }
  });

  // ---------- Number inputs: replace comma with dot ----------
  document.querySelectorAll('input[type="number"], input[step]').forEach((input) => {
    input.addEventListener("blur", () => {
      if (input.value && input.value.includes(",")) {
        input.value = input.value.replace(",", ".");
      }
    });
  });

  // ---------- Set active nav based on current path ----------
  const path = window.location.pathname;
  document.querySelectorAll(".sidebar-nav .nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (!href || href === "/") {
      if (path === "/") link.classList.add("active");
    } else if (path.startsWith(href)) {
      link.classList.add("active");
    }
  });
})();

// ---------- Lightweight Chart helper (no external dep needed beyond Chart.js if present) ----------
function drawLineChart(canvas, { labels, datasets }) {
  if (!window.Chart) {
    canvas.parentElement.innerHTML =
      '<div class="empty-state"><p>Gráficos indisponíveis no momento.</p></div>';
    return;
  }
  const ctx = canvas.getContext("2d");
  return new window.Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: datasets.map((d) => ({
        label: d.label,
        data: d.data,
        borderColor: d.color,
        backgroundColor: d.color + "22",
        borderWidth: 2.5,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: d.color,
        fill: true,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#a5b9d4", font: { family: "Inter", size: 12 } },
        },
        tooltip: {
          backgroundColor: "rgba(7,16,30,0.95)",
          borderColor: "rgba(45,255,179,0.3)",
          borderWidth: 1,
          titleColor: "#2dffb3",
          bodyColor: "#e6f1ff",
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(120,180,230,0.06)" },
          ticks: { color: "#6f829e", font: { size: 11 } },
        },
        y: {
          grid: { color: "rgba(120,180,230,0.06)" },
          ticks: { color: "#6f829e", font: { size: 11 } },
        },
      },
    },
  });
}

function drawBarChart(canvas, { labels, datasets }) {
  if (!window.Chart) return;
  const ctx = canvas.getContext("2d");
  return new window.Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: datasets.map((d) => ({
        label: d.label,
        data: d.data,
        backgroundColor: d.color,
        borderRadius: 8,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#a5b9d4" } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#6f829e" } },
        y: {
          grid: { color: "rgba(120,180,230,0.06)" },
          ticks: { color: "#6f829e" },
        },
      },
    },
  });
}

window.FitControl = { drawLineChart, drawBarChart };

// ---------- PWA registration + install prompt ----------
(function () {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/static/sw.js').catch((err) => {
        console.warn('Service worker não registrado:', err);
      });
    });
  }

  let deferredInstallPrompt = null;
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    document.querySelectorAll('[data-install-app]').forEach((btn) => btn.classList.remove('hidden'));
  });

  document.querySelectorAll('[data-install-app]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      btn.classList.add('hidden');
    });
  });
})();
