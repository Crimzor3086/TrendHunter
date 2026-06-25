// --- Initialize Page ---
    document.addEventListener("DOMContentLoaded", async () => {
      const registryInput = document.getElementById("registryContractAddress");
      if (registryInput) {
        registryInput.value = localStorage.getItem("trend_hunter_registry_contract") || registryInput.value;
        registryInput.addEventListener("input", () => {
          localStorage.setItem("trend_hunter_registry_contract", registryInput.value.trim());
          validateRegisterButtonState();
        });
      }

      const stored = localStorage.getItem(REGISTRY_STORAGE_KEY) || localStorage.getItem(LEGACY_REGISTRY_STORAGE_KEY);
      if (stored) {
        registeredTrends = JSON.parse(stored);
      }

      // Update total claims count in UI
      updateRegistryUI();

      // Setup Greeting
      setupGreeting();

      // Render feeds
      renderDashboardFeed();
      renderTrendingStrip();
      renderLiveTrendsGrid();

      // Set active trend to first element initially
      const initialTrend = getTrendDataset()[0];
      if (initialTrend) setActiveTrendItem(initialTrend);

      // Upgrade from local fallback to FastAPI data when available.
      await loadBackendBlockchainStatus();
      await loadBackendTrends();
      await loadBackendRegistry();

      // Handle query params or initial view settings
      navigate('dashboard');
    });

    function setupGreeting() {
      const greetingEl = document.getElementById("dashboardGreeting");
      const hour = new Date().getHours();
      let greetingText = "Good evening — here are your priority trends";
      if (hour < 12) {
        greetingText = "Good morning — here are your priority trends";
      } else if (hour < 18) {
        greetingText = "Good afternoon — here are your priority trends";
      }
      greetingEl.textContent = greetingText;
    }

    // --- Navigation System ---
    function navigate(pageId) {
      // Hide all pages
      document.querySelectorAll(".tab-page").forEach(page => {
        page.classList.remove("active");
      });
      // Deactivate all sidebar items
      document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
      });

      // Show requested page
      const pageNode = document.getElementById(`page-${pageId}`);
      if (pageNode) {
        pageNode.classList.add("active");
      }
      // Highlight sidebar
      const navNode = document.getElementById(`nav-${pageId}`);
      if (navNode) {
        navNode.classList.add("active");
      }

      window.scrollTo(0, 0);
    }
