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
      sidebar.classList.contains("open")
        ? closeSidebar()
        : openSidebar();
    });
  }

  overlay.addEventListener("click", closeSidebar);

  // Close sidebar on nav click (mobile)
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", closeSidebar);
  });

  // Chart.js global defaults — Agricultural Blue, Red & Green theme
  if (window.Chart) {

    Chart.defaults.font.family = "'Inter', sans-serif";

    // Default text color
    Chart.defaults.color = "#3f4a3f";

    // Default grid/border color
    Chart.defaults.borderColor = "#dfe4dc";

    // Legend styling
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.font = {
      size: 11.5,
      weight: 600
    };
  }

  // Live filter form auto-submit on chip click
  document.querySelectorAll("[data-filter-chip]").forEach((chip) => {

    chip.addEventListener("click", () => {

      const url = new URL(window.location.href);

      url.searchParams.set(
        chip.dataset.filterKey,
        chip.dataset.filterChip
      );

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


// =====================================================
// Chart Palette — Agricultural Blue, Red & Green Theme
// =====================================================

const PALETTE = {

  // Primary agricultural green
  green: "#52b788",

  // Dark forest green
  greenDark: "#1b4332",

  // Light agricultural green
  greenLight: "#95d5b2",

  // Highlight/lime green
  lime: "#a7c957",

  // Blue — water / market / information
  blue: "#3b82f6",

  // Dark blue
  blueDark: "#1d4ed8",

  // Light blue
  blueLight: "#93c5fd",

  // Red — price increase / warning
  red: "#dc2626",

  // Dark red
  redDark: "#991b1b",

  // Light red
  redLight: "#fca5a5",

  // Neutral colors
  gray700: "#596359",
  gray500: "#7c857c",
  gray300: "#c8cec5",
  gray200: "#dfe4dc",
  gray100: "#eef2eb",

  // Background
  white: "#ffffff",

  // Earth tone
  earth: "#8b5e3c",

  earthLight: "#c9a66b"

};