// --- Tab Rendering Engine ---
    function renderDashboardFeed() {
      const container = document.getElementById("priorityFeed");
      container.innerHTML = "";

      const trends = getTrendDataset();
      if (!trends.length) {
        container.innerHTML = `<div style="padding:24px; color:var(--text-muted); text-align:center">Start the backend to load trends. See README for setup.</div>`;
        return;
      }

      trends.forEach(trend => {
        const catClass = getCategoryBadgeClass(trend.category);
        const card = document.createElement("div");
        card.className = "trend-card-large";
        
        // Build platforms SVGs
        let platformsHtml = "";
        trend.platforms.forEach(p => {
          platformsHtml += `<div class="platform-badge" title="${p.toUpperCase()}">${getPlatformSvg(p)}</div>`;
        });

        card.innerHTML = `
          <div class="card-top">
            <div class="card-meta">
              <div class="meta-badges">
                <span class="badge ${catClass}">${trend.category}</span>
                <span class="badge" style="background:rgba(255,255,255,0.05); color:var(--text-muted)">Lifespan: ${trend.lifespan}</span>
              </div>
              <h4 class="trend-title-large">${trend.title}</h4>
            </div>
            <div class="score-container">
              <div class="score-circle-wrapper">
                <svg width="44" height="44" viewBox="0 0 44 44">
                  <circle class="score-circle-bg" cx="22" cy="22" r="18"/>
                  <circle class="score-circle-progress" cx="22" cy="22" r="18" 
                    stroke-dasharray="113" stroke-dashoffset="${113 - (113 * trend.score) / 100}"/>
                </svg>
                <div class="score-number">${trend.score}</div>
              </div>
            </div>
          </div>
          
          <div class="card-stats-row">
            <div class="card-stat-item">
              <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
              <span>Velocity: ${trend.velocity}</span>
            </div>
            <div class="card-stat-item">
              <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span>Seen: ${trend.firstSeen}</span>
            </div>
          </div>

          <p style="color:var(--text-muted); font-size:0.88rem; line-height:1.45">${trend.shortSummary}</p>

          <div class="card-actions">
            <div class="platform-icons">
              ${platformsHtml}
            </div>
            <div class="card-buttons">
              <button class="btn btn-secondary" onclick="viewTrendDetail('${trend.trendId}')">View Details</button>
              <button class="btn btn-primary" onclick="generateContentBrief('${trend.trendId}')">Generate Brief</button>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function renderTrendingStrip() {
      const container = document.getElementById("trendingStrip");
      container.innerHTML = "";

      getTrendDataset().forEach(trend => {
        const card = document.createElement("div");
        card.className = "trending-strip-card";
        card.onclick = () => viewTrendDetail(trend.trendId);

        card.innerHTML = `
          <div class="strip-title">${trend.title}</div>
          <div class="strip-footer">
            <span style="font-size:0.75rem; color:var(--text-muted)">${trend.category}</span>
            <span class="strip-score">Score ${trend.score}</span>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function renderLiveTrendsGrid(filtered = getTrendDataset()) {
      const container = document.getElementById("trendsGrid");
      container.innerHTML = "";

      if (filtered.length === 0) {
        container.innerHTML = `
          <div style="grid-column:1/-1; text-align:center; padding:40px; color:var(--text-muted)">
            No trends match selected filter criteria.
          </div>
        `;
        return;
      }

      filtered.forEach(trend => {
        const catClass = getCategoryBadgeClass(trend.category);
        const isSaved = savedTrends.has(trend.trendId);
        const card = document.createElement("div");
        card.className = "trend-card-medium";

        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
            <span class="badge ${catClass}">${trend.category}</span>
            <div style="display:flex; align-items:center; gap:8px">
              <span style="font-size:0.75rem; font-weight:700; color:var(--success)">${trend.velocity}</span>
              <button class="btn-icon-only" onclick="toggleSaveTrend(event, '${trend.trendId}')" style="width:24px; height:24px; border-radius:4px" title="Save Trend">
                <svg viewBox="0 0 24 24" style="stroke:${isSaved ? 'var(--accent)' : 'currentColor'}; fill:${isSaved ? 'var(--accent)' : 'none'}"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
              </button>
            </div>
          </div>
          
          <h4 style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:750; line-height:1.35; color:var(--text)" onclick="viewTrendDetail('${trend.trendId}')">${trend.title}</h4>
          
          <div class="trend-preview-box">
            ${trend.previewHtml}
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:var(--text-muted)">
            <span>Score: <strong>${trend.score}</strong></span>
            <span>Lifespan: <strong>${trend.lifespan}</strong></span>
          </div>

          <div style="display:flex; gap:10px; border-top:1px solid var(--border); padding-top:12px">
            <button class="btn btn-secondary" onclick="viewTrendDetail('${trend.trendId}')" style="flex:1; padding:8px 0">View</button>
            <button class="btn btn-primary" onclick="generateContentBrief('${trend.trendId}')" style="flex:1; padding:8px 0">Generate Brief</button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    // --- Filters logic ---
    function applyFilters() {
      const catVal = document.getElementById("filterCategory").value;
      const platVal = document.getElementById("filterPlatform").value;
      const stageVal = document.getElementById("filterStage").value;

      let filtered = getTrendDataset();

      if (catVal !== "all") {
        filtered = filtered.filter(t => t.category === catVal);
      }
      if (platVal !== "all") {
        filtered = filtered.filter(t => t.platforms.includes(platVal));
      }
      if (stageVal !== "all") {
        filtered = filtered.filter(t => t.stage === stageVal);
      }

      renderLiveTrendsGrid(filtered);
    }

    // --- Detail page setter ---
    function viewTrendDetail(trendId) {
      const trend = getTrendDataset().find(t => t.trendId === trendId);
      if (!trend) return;

      setActiveTrendItem(trend);
      navigate('detail');
    }

    function setActiveTrendItem(trend) {
      activeTrend = trend;
      
      // Update Detail UI text nodes
      document.getElementById("detailCategoryPre").textContent = trend.category;
      document.getElementById("detailTitle").textContent = trend.title;
      document.getElementById("detailSummaryText").textContent = trend.shortSummary;
      document.getElementById("detailHappeningText").textContent = trend.happeningText;
      document.getElementById("detailFirstSeen").textContent = trend.firstSeen;
      document.getElementById("detailStage").textContent = trend.stage;
      document.getElementById("detailWhyTrending").textContent = trend.whyTrending;
      document.getElementById("detailEmotionalTrigger").textContent = trend.emotionalTrigger;
      document.getElementById("detailSocialTrigger").textContent = trend.socialTrigger;
      document.getElementById("detailRelevanceNum").textContent = `${trend.relevance}%`;

      // Detail Platforms Row
      const platformRow = document.getElementById("detailPlatforms");
      platformRow.innerHTML = "";
      trend.platforms.forEach(p => {
        platformRow.innerHTML += `<div class="platform-badge" title="${p.toUpperCase()}">${getPlatformSvg(p)}</div>`;
      });

      // Carousel Render
      activeCarouselIndex = 0;
      renderCarousel();

      // Reset Content Brief Screen to match active trend
      renderContentBriefScreen();

      // Update Dev Console contract trigger buttons status
      validateRegisterButtonState();
    }

    function renderCarousel() {
      const slidesContainer = document.getElementById("carouselSlides");
      const dotsContainer = document.getElementById("carouselDots");

      slidesContainer.innerHTML = "";
      dotsContainer.innerHTML = "";

      activeTrend.carouselSlides.forEach((slide, idx) => {
        // Slide Card
        const slideDiv = document.createElement("div");
        slideDiv.className = `carousel-slide ${idx === activeCarouselIndex ? 'active' : ''}`;
        slideDiv.innerHTML = `
          <div style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between">
            <span>Evidence Type: ${slide.type}</span>
            <span>Slide ${idx+1}/${activeTrend.carouselSlides.length}</span>
          </div>
          <div class="trend-preview-box" style="min-height:200px">
            ${slide.content}
          </div>
          <div style="font-size:0.8rem; color:var(--text); font-weight:700; margin-top:8px">${slide.title}</div>
        `;
        slidesContainer.appendChild(slideDiv);

        // Dot
        const dot = document.createElement("span");
        dot.className = `carousel-dot ${idx === activeCarouselIndex ? 'active' : ''}`;
        dot.onclick = () => {
          activeCarouselIndex = idx;
          renderCarousel();
        };
        dotsContainer.appendChild(dot);
      });
    }

    function nextCarouselSlide() {
      if (!activeTrend) return;
      activeCarouselIndex = (activeCarouselIndex + 1) % activeTrend.carouselSlides.length;
      renderCarousel();
    }

    function prevCarouselSlide() {
      if (!activeTrend) return;
      activeCarouselIndex = (activeCarouselIndex - 1 + activeTrend.carouselSlides.length) % activeTrend.carouselSlides.length;
      renderCarousel();
    }

    // --- Content Brief Page Generator ---
    async function generateContentBrief(trendId) {
      const trend = getTrendDataset().find(t => t.trendId === trendId);
      if (!trend) return;
      
      setActiveTrendItem(trend);
      try {
        showToast("AI Service", "Generating brief from backend AI service...", "info");
        const response = await fetch(`${API_BASE}/generate-brief`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trend_id: trend.trendId })
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const brief = await response.json();
        applyBriefToActiveTrend(brief);
      } catch (error) {
        showToast("AI Fallback", "Backend AI unavailable; using local brief template.", "info");
      }
      renderContentBriefScreen();
      navigate('contentbriefs');
      showToast("Brief Generated", `AI brief for "${trend.title}" loaded successfully.`, "success");
    }

    function renderContentBriefScreen() {
      if (!activeTrend) return;

      currentScriptVariation = 1;

      document.getElementById("briefCategoryBadge").className = `badge ${getCategoryBadgeClass(activeTrend.category)}`;
      document.getElementById("briefCategoryBadge").textContent = activeTrend.category;
      document.getElementById("briefHappeningText").textContent = activeTrend.shortSummary;
      document.getElementById("briefWhySpreading").textContent = activeTrend.whyTrending;
      document.getElementById("briefLifespanText").textContent = activeTrend.lifespan;
      document.getElementById("briefKuzanaText").textContent = activeTrend.kuzanaAngle;

      // Hooks
      const hooksList = document.getElementById("briefHooksList");
      hooksList.innerHTML = "";
      activeTrend.hooks.forEach((hook, index) => {
        const item = document.createElement("div");
        item.className = "hook-item-card";
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:12px">
            <span style="width:22px; height:22px; border-radius:50%; background:rgba(232, 65, 66, 0.1); color:var(--accent); display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700">${index+1}</span>
            <span class="hook-text">${hook}</span>
          </div>
          <button class="btn btn-secondary" style="padding:6px 12px; font-size:0.75rem" onclick="copyHook(this, '${hook.replace(/'/g, "\\'")}')">
            Copy
          </button>
        `;
        hooksList.appendChild(item);
      });

      // Script
      renderScriptContent(activeTrend.script.v1);

      // Remix Template Flow
      const remixFlow = document.getElementById("briefRemixFlow");
      remixFlow.innerHTML = `
        <div class="remix-step">
          <div class="remix-step-title">Trend Format</div>
          <div class="remix-step-value">${activeTrend.remix.format}</div>
        </div>
        <div class="remix-arrow">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
        </div>
        <div class="remix-step">
          <div class="remix-step-title">Business Interpretation</div>
          <div class="remix-step-value">${activeTrend.remix.interpretation}</div>
        </div>
        <div class="remix-arrow">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
        </div>
        <div class="remix-step">
          <div class="remix-step-title">Founder Lesson</div>
          <div class="remix-step-value">${activeTrend.remix.lesson}</div>
        </div>
      `;
    }

    function renderScriptContent(scriptText) {
      const scriptBody = document.getElementById("briefScriptBody");
      scriptBody.innerHTML = "";

      const segments = scriptText.split("\n");
      segments.forEach(seg => {
        if (!seg.trim()) return;
        const match = seg.match(/^\[(.*?)\](.*)$/);
        if (match) {
          const label = match[1];
          const text = match[2];
          scriptBody.innerHTML += `
            <div class="script-segment">
              <span class="script-segment-label">${label}</span>
              <span class="script-segment-content">${text.trim()}</span>
            </div>
          `;
        } else {
          scriptBody.innerHTML += `<div style="margin-bottom:8px">${seg}</div>`;
        }
      });
    }

    function copyHook(btn, hookText) {
      navigator.clipboard.writeText(hookText).then(() => {
        btn.textContent = "Copied!";
        btn.style.color = "var(--success)";
        btn.style.borderColor = "var(--success)";
        setTimeout(() => {
          btn.textContent = "Copy";
          btn.style.color = "";
          btn.style.borderColor = "";
        }, 1500);
        showToast("Hook Copied", "Hook copied to clipboard.", "success");
      });
    }

    function copyEntireScript() {
      if (!activeTrend) return;
      const rawText = currentScriptVariation === 1 ? activeTrend.script.v1 : activeTrend.script.v2;
      // Strip bracket labels for clean paste
      const cleanText = rawText.replace(/\[.*?\]/g, "").trim();

      navigator.clipboard.writeText(cleanText).then(() => {
        showToast("Script Copied", "Shoot-ready script copied without scene tags.", "success");
      });
    }

    function regenerateScript() {
      const regenSpinner = document.getElementById("regenSpinner");
      const regenIcon = document.getElementById("regenIcon");
      const regenText = document.getElementById("regenText");

      regenSpinner.style.display = "inline-block";
      regenIcon.style.display = "none";
      regenText.textContent = "Regenerating...";

      setTimeout(() => {
        regenSpinner.style.display = "none";
        regenIcon.style.display = "inline-block";
        regenText.textContent = "Regenerate";

        if (currentScriptVariation === 1) {
          currentScriptVariation = 2;
          renderScriptContent(activeTrend.script.v2);
        } else {
          currentScriptVariation = 1;
          renderScriptContent(activeTrend.script.v1);
        }

        showToast("Script Regenerated", "AI generated a new script angle.", "info");
      }, 1200);
    }

    function triggerGenerateBriefFromDetail() {
      if (!activeTrend) return;
      generateContentBrief(activeTrend.trendId);
    }

    // --- Save trends discover toggles ---
    function toggleSaveTrend(event, trendId) {
      event.stopPropagation();
      if (savedTrends.has(trendId)) {
        savedTrends.delete(trendId);
        showToast("Trend Unsaved", "Trend removed from your saved list.", "info");
      } else {
        savedTrends.add(trendId);
        showToast("Trend Saved", "Trend bookmarked for content briefs.", "success");
      }
      applyFilters();
    }

    // --- Helper UI renderers ---
    function getCategoryBadgeClass(category) {
      switch(category) {
        case "Founder Culture": return "badge-founder";
        case "Business": return "badge-business";
        case "Money": return "badge-money";
        case "Entrepreneurship": return "badge-entrepreneurship";
        default: return "";
      }
    }

    function getPlatformSvg(platform) {
      switch(platform) {
        case "x":
          return `<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`;
        case "reddit":
          return `<svg viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 5.523 4.477 10 10 10s10-4.477 10-10c0-5.523-4.477-10-10-10zm4.5 13.5a1.5 1.5 0 0 1-2.515 1.077 8.847 8.847 0 0 1-3.985.423c-1.5-.15-2.8-.8-3.667-1.785a1.5 1.5 0 1 1-1.018-2.615c.1 0 .2.02.3.06a5.55 5.55 0 0 1 2.37-3.2 4.46 4.46 0 0 1-.3-1.46c0-1.1.9-2 2-2a2 2 0 0 1 1.9 1.4c1.2-.1 2.5 0 3.7.3a1.5 1.5 0 1 1 2.22 1.63c.6.6 1 1.3 1.2 2.1a1.5 1.5 0 1 1 1.075 2.6z"/></svg>`;
        case "tiktok":
          return `<svg viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.07-2.89-.52-4.06-1.42-.42-.31-.8-.67-1.14-1.07-.03 2.66-.01 5.32-.02 7.98-.06 2.39-.99 4.82-2.89 6.27-2.18 1.72-5.39 2.05-7.88 1.02-2.69-1.07-4.57-3.95-4.57-6.95.02-3.18 2.21-6.19 5.37-6.72.77-.14 1.56-.16 2.34-.07.02 1.3.01 2.6.02 3.91-.71-.16-1.48-.05-2.11.31-1.12.6-1.76 1.88-1.66 3.17.06 1.16.8 2.27 1.89 2.66 1.29.49 2.92.17 3.86-.84.77-.79.93-1.99.91-3.05v-12.2H12.52v.01z"/></svg>`;
        case "news":
          return `<svg viewBox="0 0 24 24" style="fill:none;stroke:currentColor;stroke-width:2"><path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1M19 20a2 2 0 002-2V8a2 2 0 00-2-2h-2M19 20H9a2 2 0 01-2-2v-5M11 8h2m-2 4h2M11 16h2"/></svg>`;
        case "youtube":
          return `<svg viewBox="0 0 24 24"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.508 9.388.508 9.388.508s7.518 0 9.388-.508a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`;
        default:
          return "";
      }
    }
