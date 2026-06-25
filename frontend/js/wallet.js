// --- Web3 / Avalanche Fuji logic ---
    function log(message, type = "success") {
      const logsEl = document.getElementById("consoleLogs");
      let prefix = "[SYSTEM]";
      if (type === "error") prefix = "[ERROR]❌";
      if (type === "pending") prefix = "[PENDING]⏳";

      logsEl.innerHTML = `${prefix} ${message}<br/>${logsEl.innerHTML}`;
    }

    function clearLogs() {
      document.getElementById("consoleLogs").innerHTML = "[SYSTEM] Logs cleared.";
    }

    function updateWalletUI() {
      const dot = document.getElementById("walletDot");
      const statusText = document.getElementById("walletStatusText");
      const addressText = document.getElementById("walletAddressText");
      const connectBtn = document.getElementById("connectWalletBtn");

      if (walletConnected) {
        dot.className = "wallet-status-dot connected";
        statusText.textContent = "Connected";
        addressText.textContent = shortenAddress(signer.address);
        connectBtn.innerHTML = `<span>Disconnect</span>`;
        connectBtn.style.background = "linear-gradient(135deg, #10b981 0%, #047857 100%)";
      } else {
        dot.className = "wallet-status-dot";
        statusText.textContent = "Disconnected";
        addressText.textContent = "—";
        connectBtn.innerHTML = `
          <svg style="width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24"><path d="M20 12V8H6a2 2 0 013.5-1.5M20 12v4H6a2 2 0 003.5 1.5M20 12H8m12 0H4a2 2 0 01-2-2V6a2 2 0 012-2h16a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2v-4a2 2 0 012-2h16"/></svg>
          <span>Connect Core</span>
        `;
        connectBtn.style.background = "";
      }
    }

    function shortenAddress(addr) {
      if (!addr) return "—";
      return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
    }

    async function connectWallet() {
      if (walletConnected) {
        // Disconnect
        walletConnected = false;
        signer = null;
        rawProvider = null;
        updateWalletUI();
        validateRegisterButtonState();
        log("Wallet disconnected.");
        return;
      }

      // Core Wallet / injected provider
      const injected = window.avalanche || window.ethereum;
      if (!injected) {
        log("No injected Web3 Wallet detected. Please install Core Wallet browser extension.", "error");
        showToast("Connection Error", "Core Wallet extension not found.", "info");
        return;
      }

      try {
        log("Requesting account connection...", "pending");
        await injected.request({ method: "eth_requestAccounts" });
        const chainId = Number.parseInt(await injected.request({ method: "eth_chainId" }), 16);

        if (chainId !== FUJI_CHAIN_ID) {
          log(`Wrong network (Chain ID: ${chainId}). Switch your Core Wallet to Avalanche Fuji Testnet (43113).`, "error");
          showToast("Network Error", "Switch to Fuji Testnet (43113)", "info");
          return;
        }

        rawProvider = new ethers.BrowserProvider(injected);
        signer = await rawProvider.getSigner();
        walletConnected = true;

        updateWalletUI();
        validateRegisterButtonState();
        log(`Connected successfully: ${signer.address}`);
        showToast("Connected", `Core Wallet connected on Fuji!`, "success");
      } catch (err) {
        log(`Connection failed: ${err.message}`, "error");
      }
    }

    function validateRegisterButtonState() {
      const contractInput = document.getElementById("registryContractAddress").value.trim();
      const hasContract = /^0x[a-fA-F0-9]{40}$/.test(contractInput);
      const isReady = walletConnected && hasContract && activeTrend;

      document.getElementById("btnRegisterActive").disabled = !isReady;
    }

    function verifyContractConnection() {
      const contractInput = document.getElementById("registryContractAddress").value.trim();
      const hasContract = /^0x[a-fA-F0-9]{40}$/.test(contractInput);

      if (hasContract) {
        log(`Contract address validated: ${contractInput}`);
        showToast("Verified", "Contract address format is correct.", "success");
      } else {
        log(`Invalid contract address: ${contractInput}`, "error");
        showToast("Error", "Please input a valid 40-character Ethereum/AVAX address.", "info");
      }
      validateRegisterButtonState();
    }
