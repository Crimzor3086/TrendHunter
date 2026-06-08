# Mini Hack Cohort 1 — Starter Template
## Payments on Avalanche | Team1 Kenya | 2026

This is the official starter template for Mini Hack Cohort 1. Fork this repo to your personal GitHub account at the start of the cohort. Do not clone it directly — fork it.

Every weekly deliverable is a pull request on your fork. The template gives you a working project structure so you spend your time building, not setting up.

---

## What is inside

```
minihack-cohort1-template/
  contracts/          Solidity smart contracts go here
  scripts/            Hardhat deployment scripts
  test/               Contract unit tests
  frontend/           Basic frontend scaffold
  .env.example        Environment variable reference — copy to .env and fill in your values
  hardhat.config.js   Pre-configured for Fuji testnet
  package.json        All dependencies pre-listed
  README.md           This file — replace the top section with your project details by Week 4
```

---

## Getting started

### 1. Fork this repository

Click **Fork** at the top right of this page. Fork to your personal GitHub account, not to an organisation.

### 2. Clone your fork

```bash
git clone https://github.com/YOUR-GITHUB-HANDLE/minihack-cohort1-template.git
cd minihack-cohort1-template
```

### 3. Install dependencies

```bash
npm install
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values. Never commit this file. It is already in `.gitignore`.

### 5. Verify your Hardhat config

```bash
npx hardhat compile
```

If this runs without errors, your environment is set up correctly.

### 6. Get Fuji testnet AVAX

Visit the faucet at [core.app/tools/testnet-faucet](https://core.app/tools/testnet-faucet) and request AVAX to your Core Wallet Fuji address.

---

## Weekly workflow

At the start of each week, create a new branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b week-{N}-{your-github-handle}
```

Example:
```bash
git checkout -b week-2-scotch
```

Do all your work for that week on that branch. When you are done, open a pull request against the `main` branch of your own fork.

PR title format:
```
[Cohort 1 Week N] Your Name - Deliverable title
```

Example:
```
[Cohort 1 Week 2] Joseph Njoroge - ERC-20 token with unit tests
```

Fill in every section of the PR template. Submit the PR link in `#submissions` on Discord before Sunday midnight EAT.

---

## Network configuration

This template is pre-configured for Fuji testnet. Do not change the network configuration unless instructed to.

| Setting | Value |
|---------|-------|
| Network name | Avalanche Fuji Testnet |
| RPC URL | `https://api.avax-test.network/ext/bc/C/rpc` |
| Chain ID | 43113 |
| Currency symbol | AVAX |
| Block explorer | `https://testnet.snowtrace.io` |

---

## Deliverables by week

| Week | Deliverable | Key requirement |
|------|-------------|-----------------|
| 1 | Hello Avalanche transaction | Both wallet addresses + Snowtrace links |
| 2 | ERC-20 token | Deployed contract + 3 passing unit tests |
| 3 | STK Push integration | Working M-Pesa callback + Core Wallet connected frontend |
| 4 | Final payment product | Deployed frontend + contract + 5-minute demo video |

Full deliverable specs are in the programme handbook at [team1-kenya-mini-hack.vercel.app](https://team1-kenya-mini-hack.vercel.app).

---

## Resources

- Avalanche documentation: [docs.avax.network](https://docs.avax.network)
- Avalanche Builders Hub: [core.app/builders-hub](https://core.app/builders-hub)
- Core Wallet: [core.app](https://core.app)
- Fuji faucet: [core.app/tools/testnet-faucet](https://core.app/tools/testnet-faucet)
- Snowtrace Fuji explorer: [testnet.snowtrace.io](https://testnet.snowtrace.io)
- Hardhat docs: [hardhat.org/docs](https://hardhat.org/docs)
- ethers.js docs: [docs.ethers.org](https://docs.ethers.org)
- OpenZeppelin Contracts: [docs.openzeppelin.com/contracts](https://docs.openzeppelin.com/contracts)
- Daraja API: [developer.safaricom.co.ke/docs](https://developer.safaricom.co.ke/docs)
- Programme handbook: [team1-kenya-mini-hack.vercel.app](https://team1-kenya-mini-hack.vercel.app)

---

## If you already started your own repo

If you started building before this template was available, you do not need to migrate. Do three things to your existing repo:

1. Copy `.env.example` from this template into your repo root
2. Copy `hardhat.config.js` from this template if you have not already configured Fuji
3. Add these topics to your repo on GitHub: `avalanche`, `mini-hack`, `web3-kenya`, `fuji-testnet`

Submit your weekly PRs on your existing repo using the same branch naming and PR title format above.

---

## Help

Post in `#help` on Discord with: what you are trying to do, what you tried, and the exact error message.

Office hours: Thursdays 6:00 PM to 7:00 PM EAT on Discord voice.

Tag `@scotch` on Discord only for unresolved blockers after trying `#help` first.
