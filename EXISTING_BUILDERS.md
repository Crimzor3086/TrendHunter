# Guide for Builders Who Already Started

If you started building before the cohort template was published, this guide is for you. You do not need to start over or migrate your repo. Follow the three steps below and you are aligned with the rest of the cohort.

---

## Step 1 — Add the environment variable reference file

Copy the `.env.example` file from the template repo into the root of your project:

[github.com/Talent-Index/minihack-cohort1-template](https://github.com/Talent-Index/minihack-cohort1-template)

Edit it to reflect the environment variables your project actually uses. The structure should match — one variable per line, placeholder values only, never real keys.

If you already have a `.env.example`, make sure it covers at minimum:

```
PRIVATE_KEY=
SNOWTRACE_API_KEY=
DARAJA_CONSUMER_KEY=
DARAJA_CONSUMER_SECRET=
DARAJA_SHORTCODE=
DARAJA_PASSKEY=
DARAJA_CALLBACK_URL=
```

Check your `.gitignore` — `.env` must be in there. If it is not, add it immediately and verify that no real keys have been pushed to your repo history. If they have, rotate those keys right now before doing anything else.

---

## Step 2 — Verify your Hardhat config targets Fuji

Open your `hardhat.config.js` and confirm the Fuji network block is present and correct:

```javascript
networks: {
  fuji: {
    url: "https://api.avax-test.network/ext/bc/C/rpc",
    chainId: 43113,
    accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
  },
},
```

If you do not have a `hardhat.config.js` yet, copy the one from the template repo root.

Test that it works:

```bash
npx hardhat compile
```

This should run without errors. If you see missing module errors, run `npm install` first.

---

## Step 3 — Add GitHub topics to your repo

Topics make your project discoverable across the org and in Avalanche ecosystem searches. They also flag your project for the monthly showcase review.

1. Go to your repo on GitHub
2. Click the gear icon next to **About** on the right side of the page
3. Add all of the following topics:

```
avalanche
mini-hack
web3-kenya
fuji-testnet
```

Add `m-pesa` if your project integrates M-Pesa. Add `solidity` if it includes smart contracts.

---

## Weekly submissions from your existing repo

Your submission process is identical to builders using the template. The only difference is your repo lives under your personal GitHub account and has your own structure.

**Branch naming — same format:**

```bash
git checkout -b week-{N}-{your-github-handle}
```

**PR title — same format:**

```
[Cohort 1 Week N] Your Name - Deliverable title
```

**Open your PR against the `main` branch of your own repo.**

Do not open PRs against the template repo.

**Submit the PR link in `#submissions` on Discord before Sunday midnight EAT.**

---

## What the reviewer expects to find

When your PR is reviewed, the reviewer will look for:

- A `README.md` that explains what you built this week and how to run it locally
- A `.env.example` file with placeholder values — no real keys anywhere
- A Snowtrace link to your deployed contract (required from Week 2)
- Passing unit tests (at least the ones required for that week's deliverable)
- Commit messages that describe what changed, not just "fix" or "update"

If your repo is missing any of these, update it before the deadline.

---

## Questions

Post in `#help` on Discord with: what you are trying to do, what you tried, and the exact error message.

Office hours: Thursdays 6:00 PM to 7:00 PM EAT on Discord voice, before the main session.
