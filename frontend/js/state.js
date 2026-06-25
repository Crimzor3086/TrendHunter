// --- Global State ---
    const FUJI_CHAIN_ID = 43113;
    const contractAbi = [
      "function registerTrend(string title, string category, uint256 score, string contentHash) external returns (uint256)",
      "function getTrend(uint256 trendId) external view returns (tuple(uint256 id, string title, string category, uint256 score, uint256 firstSeen, string contentHash, address creator, bool verified))",
      "function creatorReputation(address) public view returns (uint256)",
      "function trendCount() public view returns (uint256)"
    ];

    let rawProvider = null;
    let signer = null;
    let walletConnected = false;
    let activeTrend = null;
    let activeCarouselIndex = 0;
    let savedTrends = new Set();
    let currentScriptVariation = 1; // 1 or 2
    let liveTrends = [];
    const API_BASE = localStorage.getItem("trend_hunter_api_base")
      || `${window.location.protocol}//${window.location.hostname}:8000`;
    const REGISTRY_STORAGE_KEY = "trend_hunter_registry";
    const LEGACY_REGISTRY_STORAGE_KEY = "trendjack_registry";

// --- On-Chain Registry Log State ---
let registeredTrends = [];
