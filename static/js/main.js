// Sidebar toggle (mobile) + shared chart defaults
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("menuToggle");

  let overlay = document.querySelector(".overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.className = "overlay";
    document.body.appendChild(overlay);
  }

  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("show");
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
  }

  if (toggle) {
    toggle.addEventListener("click", () => {
      sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
    });
  }
  overlay.addEventListener("click", closeSidebar);

  // Close sidebar on nav click (mobile)
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", closeSidebar);
  });

  // Chart.js global defaults — black & white theme
  if (window.Chart) {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = "#4a4a4a";
    Chart.defaults.borderColor = "#e4e4e4";
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.font = { size: 11.5, weight: 600 };
  }

  // Live filter form auto-submit on chip click
  document.querySelectorAll("[data-filter-chip]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const url = new URL(window.location.href);
      url.searchParams.set(chip.dataset.filterKey, chip.dataset.filterChip);
      window.location.href = url.toString();
    });
  });

  // Debounced live search
  document.querySelectorAll("[data-live-search]").forEach((input) => {
    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const url = new URL(window.location.href);
        url.searchParams.set("q", input.value);
        window.location.href = url.toString();
      }, 500);
    });
  });
});

// Palette helper for charts
const PALETTE = {
  black: "#0a0a0a",
  charcoal: "#2a2a2a",
  gray700: "#4a4a4a",
  gray500: "#7a7a7a",
  gray300: "#cfcfcf",
  gray200: "#e4e4e4",
  gray100: "#f2f2f2",
  white: "#ffffff",
};
