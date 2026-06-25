// --- On-Chain Registry Log Actions ---
    async function registerActiveTrendOnChain() {
      if (!activeTrend) return;
      if (!walletConnected) {
        showToast("Wallet Error", "Please connect your wallet first.", "info");
        return;
      }

      const contractAddress = document.getElementById("registryContractAddress").value.trim();
      if (!/^0x[a-fA-F0-9]{40}$/.test(contractAddress)) {
        showToast("Address Error", "Please input a valid contract address.", "info");
        return;
      }

      const contentHash = canonicalTrendHash(activeTrend);

      log(`Initiating registry for "${activeTrend.title}"...`, "pending");

      try {
        const registryContract = new ethers.Contract(contractAddress, contractAbi, signer);

        log(`Submitting on-chain transaction to contract ${contractAddress}...`, "pending");
        const tx = await registryContract.registerTrend(
          activeTrend.title,
          activeTrend.category,
          activeTrend.score,
          contentHash
        );

        log(`Transaction submitted! Hash: ${tx.hash}`, "pending");
        showToast("Submitted", "Transaction submitted to blockchain. Waiting for block confirmation.", "info");

        await tx.wait();

        const returnedTrendId = await registryContract.trendCount();
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        const newReg = {
          trendId: returnedTrendId.toString(),
          title: activeTrend.title,
          category: activeTrend.category,
          score: activeTrend.score,
          hash: tx.hash,
          timestamp: timestamp,
          status: "Success",
          explorerUrl: `https://testnet.snowtrace.io/tx/${tx.hash}`
        };

        registeredTrends.unshift(newReg);
        localStorage.setItem(REGISTRY_STORAGE_KEY, JSON.stringify(registeredTrends));

        updateRegistryUI();
        log(`Registered on Fuji Testnet!`, "success");
        log(`Trend ID: ${returnedTrendId}`);
        log(`Tx Explorer: https://testnet.snowtrace.io/tx/${tx.hash}`);

        showToast("Success!", "Registered on Avalanche blockchain.", "success");
      } catch (err) {
        log(`Registration transaction failed: ${err.message}`, "error");
        showToast("Transaction Failed", err.reason || err.message, "info");
      }
    }

    async function registerActiveTrendViaBackend() {
      if (!activeTrend) return;

      try {
        log(`Requesting backend registry service for "${activeTrend.title}"...`, "pending");
        const response = await fetch(`${API_BASE}/register-trend`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            trend_id: activeTrend.trendId,
            brief_hash: `sha256:${ethers.sha256(ethers.toUtf8Bytes(activeTrend.script.v1))}`
          })
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const record = await response.json();
        const txHash = record.transaction_hash || record.trend_hash;
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        const newReg = {
          trendId: activeTrend.trendId,
          title: activeTrend.title,
          category: activeTrend.category,
          score: activeTrend.score,
          hash: txHash,
          timestamp,
          status: record.status,
          explorerUrl: record.explorer_url || ""
        };

        registeredTrends.unshift(newReg);
        localStorage.setItem(REGISTRY_STORAGE_KEY, JSON.stringify(registeredTrends));
        updateRegistryUI();
        log(`Backend registry status: ${record.status}`, record.transaction_hash ? "success" : "pending");
        if (record.explorer_url) log(`Explorer URL: ${record.explorer_url}`);
        showToast("Backend Registry", record.status, record.transaction_hash ? "success" : "info");
      } catch (error) {
        log(`Backend registry failed: ${error.message}`, "error");
        showToast("Backend Registry Failed", error.message, "info");
      }
    }

    function triggerRegisterFromDetail() {
      if (!activeTrend) return;
      navigate('registry');
      setTimeout(() => {
        registerActiveTrendOnChain();
      }, 300);
    }

    function updateRegistryUI() {
      const tableBody = document.getElementById("registryTableBody");
      tableBody.innerHTML = "";

      if (registeredTrends.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted)">No trends registered on-chain yet.</td></tr>`;
        return;
      }

      registeredTrends.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td><strong>${item.trendId}</strong></td>
          <td>${item.title}</td>
          <td><span class="badge ${getCategoryBadgeClass(item.category)}">${item.category}</span></td>
          <td>${item.score}/100</td>
          <td class="registry-hash" title="${item.hash}">${item.hash.slice(0, 8)}...${item.hash.slice(-6)}</td>
          <td><span style="color:var(--success); font-weight:700">● ${item.status}</span></td>
          <td class="registry-actions-col">
            <a class="btn btn-secondary" style="padding:4px 8px; font-size:0.75rem" href="${item.explorerUrl}" target="_blank">Explorer</a>
            <button class="btn btn-secondary" style="padding:4px 8px; font-size:0.75rem" onclick="copyTextHash('${item.hash}')">Copy Hash</button>
          </td>
        `;
        tableBody.appendChild(row);
      });

      document.getElementById("registryTotalClaims").textContent = registeredTrends.length;
      document.getElementById("settingsReputation").textContent = `${registeredTrends.length * 3} points`;
    }

    function copyTextHash(hash) {
      navigator.clipboard.writeText(hash).then(() => {
        showToast("Hash Copied", "Transaction hash copied to clipboard.", "success");
      });
    }

    function resetAppDatabase() {
      if (confirm("Are you sure you want to reset the registry database? This will clear all transactions.")) {
        localStorage.removeItem(REGISTRY_STORAGE_KEY);
        localStorage.removeItem(LEGACY_REGISTRY_STORAGE_KEY);
        registeredTrends = [];
        updateRegistryUI();
        showToast("Database Reset", "Local registry cache has been cleared.", "info");
      }
    }
