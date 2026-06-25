function getTrendDataset() {
      return liveTrends;
    }

    function timeAgo(timestamp) {
      if (!timestamp) return "recently";
      const then = new Date(timestamp).getTime();
      const diffMs = Date.now() - then;
      const hours = Math.max(1, Math.round(diffMs / 3600000));
      if (hours < 24) return `${hours} hours ago`;
      return `${Math.round(hours / 24)} days ago`;
    }

    function estimateLifespan(stage) {
      const normalized = String(stage || "").toLowerCase();
      if (normalized === "emerging") return "24-72 hours";
      if (normalized === "growing") return "3-5 days";
      if (normalized === "peak") return "1-2 days";
      return "<24 hours";
    }

    function titleCaseStage(stage) {
      const value = String(stage || "emerging").toLowerCase();
      return value.charAt(0).toUpperCase() + value.slice(1);
    }

    function signalPreviewHtml(trend) {
      const signal = trend.raw_signals?.[0];
      if (!signal) return `<div class="mock-news"><span class="news-tag">Live</span><h4 class="news-title">${trend.title}</h4><div class="news-source"><span>Backend API</span><span>${trend.stage}</span></div></div>`;

      if (signal.source === "reddit") {
        return `<div class="mock-reddit"><div class="reddit-header"><div class="reddit-logo">r</div><span>Reddit · ${timeAgo(signal.timestamp)}</span></div><div class="reddit-body">${signal.text}</div><div class="reddit-footer"><span>🔺 ${signal.metrics.likes}</span><span>💬 ${signal.metrics.comments}</span></div></div>`;
      }
      if (signal.source === "x") {
        return `<div class="mock-tweet"><div class="tweet-header"><div class="tweet-avatar">X</div><div class="tweet-userinfo"><span class="tweet-name">Live signal</span><span class="tweet-handle">X · ${timeAgo(signal.timestamp)}</span></div></div><div class="tweet-body">${signal.text}</div><div class="tweet-footer"><span>💬 ${signal.metrics.comments}</span><span>🔄 ${signal.metrics.shares}</span><span>❤️ ${signal.metrics.likes}</span></div></div>`;
      }
      return `<div class="mock-news"><span class="news-tag">${signal.source}</span><h4 class="news-title">${signal.text}</h4><div class="news-source"><span>Live source</span><span>${timeAgo(signal.timestamp)}</span></div></div>`;
    }

    function backendTrendToUi(trend) {
      const relevance = Math.round((trend.classification?.kenya_relevance || 0.82) * 100);
      const summary = trend.raw_signals?.[0]?.text || `${trend.title} is moving across founder-focused channels.`;
      const why = trend.classification?.reasoning || "The trend is gaining attention because it connects to founder decisions, money and startup execution.";
      return {
        trendId: trend.trend_id,
        title: trend.title,
        category: trend.category,
        score: trend.score,
        lifespan: estimateLifespan(trend.stage),
        velocity: `Score ${trend.score} live`,
        stage: titleCaseStage(trend.stage),
        platforms: trend.platforms || [],
        shortSummary: summary,
        firstSeen: timeAgo(trend.first_seen),
        firstSeenIso: trend.first_seen,
        relevance,
        happeningText: summary,
        whyTrending: why,
        emotionalTrigger: "Founder urgency, opportunity timing, and fear of missing the viral window.",
        socialTrigger: "Cross-platform debate among founders, creators and operators.",
        kuzanaAngle: "Turn the trend into one practical action a Kenyan founder can take today.",
        previewHtml: signalPreviewHtml(trend),
        carouselSlides: (trend.raw_signals || []).slice(0, 4).map(signal => ({
          type: signal.source,
          title: `${signal.source.toUpperCase()} signal`,
          content: signalPreviewHtml({ ...trend, raw_signals: [signal] })
        })),
        hooks: [
          `Kenyan founders should pay attention to this: ${trend.title}.`,
          `This trend is moving fast, but the founder lesson is simple.`,
          `If you run a Kenyan startup, do not ignore this shift.`
        ],
        script: {
          v1: `[Hook] ${trend.title} is moving fast.\n[Context] The signal is spreading across ${trend.platforms?.join(", ") || "social platforms"}.\n[Insight] For Kenyan founders, the opportunity is to turn the conversation into a practical operating lesson.\n[Takeaway] Explain what changes, what to ignore, and what action a small team can take today.\n[CTA] Save this and share it with a founder who needs to move faster.`,
          v2: `[Hook] This is not just another online debate.\n[Context] ${summary}\n[Insight] The creators who win will localize the trend before it peaks.\n[Takeaway] Tie it to Kenyan customer behavior, SME constraints and founder execution.\n[CTA] Comment with the business model you want analyzed next.`
        },
        remix: {
          format: trend.title,
          interpretation: "Kenyan founder operating lesson",
          lesson: "Move from trend commentary to practical execution"
        }
      };
    }

    function canonicalTrendHash(trend) {
      const firstSeen = trend.firstSeenIso || trend.firstSeen || "";
      const payload = `${trend.title}|${firstSeen}|${trend.category}|${trend.score}`;
      return ethers.sha256(ethers.toUtf8Bytes(payload));
    }

    function applyBriefToActiveTrend(brief) {
      activeTrend.kuzanaAngle = brief.angle || activeTrend.kuzanaAngle;
      activeTrend.whyTrending = brief.why_it_is_spreading || activeTrend.whyTrending;
      activeTrend.hooks = [brief.hook, ...activeTrend.hooks.filter(hook => hook !== brief.hook)].filter(Boolean).slice(0, 5);
      activeTrend.script = {
        v1: brief.script_30_60s || activeTrend.script.v1,
        v2: activeTrend.script.v2
      };
      activeTrend.remix = {
        format: activeTrend.title,
        interpretation: brief.remix_template || activeTrend.remix.interpretation,
        lesson: brief.kenyan_context || activeTrend.remix.lesson
      };
    }

    async function loadBackendTrends({ refreshLive = false } = {}) {
      try {
        const response = await fetch(`${API_BASE}/trends${refreshLive ? "?refresh_live=true" : ""}`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const trends = await response.json();
        liveTrends = trends.map(backendTrendToUi);
        renderDashboardFeed();
        renderTrendingStrip();
        renderLiveTrendsGrid();
        if (liveTrends.length) setActiveTrendItem(liveTrends[0]);
        showToast("Backend Connected", `Loaded ${liveTrends.length} live backend trends.`, "success");
      } catch (error) {
        liveTrends = [];
        showToast("Offline Fallback", "Backend not reachable; connect the API to load trends.", "info");
      }
    }

    async function loadBackendBlockchainStatus() {
      try {
        const response = await fetch(`${API_BASE}/blockchain/status`);
        if (!response.ok) return;
        const status = await response.json();
        const registryInput = document.getElementById("registryContractAddress");
        if (registryInput && status.contract_address && !registryInput.value.trim()) {
          registryInput.value = status.contract_address;
          localStorage.setItem("trend_hunter_registry_contract", status.contract_address);
          validateRegisterButtonState();
        }
      } catch (_error) {
        // Backend may be offline during local-only wallet testing.
      }
    }

    async function loadBackendRegistry() {
      try {
        const response = await fetch(`${API_BASE}/registry`);
        if (!response.ok) return;
        const records = await response.json();
        if (!records.length) return;

        const merged = records.map(record => ({
          trendId: record.on_chain_trend_id ? String(record.on_chain_trend_id) : record.trend_id,
          title: record.payload?.title || record.trend_id,
          category: record.category,
          score: record.score,
          hash: record.transaction_hash || record.trend_hash,
          timestamp: record.first_seen,
          status: record.status,
          explorerUrl: record.explorer_url || ""
        }));

        registeredTrends = merged;
        localStorage.setItem(REGISTRY_STORAGE_KEY, JSON.stringify(registeredTrends));
        updateRegistryUI();
      } catch (_error) {
        // Keep local registry cache when backend is unavailable.
      }
    }
