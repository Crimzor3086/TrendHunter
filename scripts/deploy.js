const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "AVAX");

  if (balance === 0n) {
    console.error(
      "Error: account has no AVAX. Get testnet AVAX from https://core.app/tools/testnet-faucet"
    );
    process.exit(1);
  }

  const Contract = await ethers.getContractFactory("TrendRegistry");

  console.log("Deploying...");

  const contract = await Contract.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const network = await ethers.provider.getNetwork();

  const deployment = {
    network: "fuji",
    chainId: Number(network.chainId),
    contractName: "TrendRegistry",
    address,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(deploymentsDir, { recursive: true });
  const deploymentPath = path.join(deploymentsDir, "fuji-TrendRegistry.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deployment, null, 2));

  console.log("Contract deployed to:", address);
  console.log("Deployment artifact written to:", deploymentPath);
  console.log(
    "View on Snowtrace: https://testnet.snowtrace.io/address/" + address
  );
  console.log("");
  console.log("To verify on Snowtrace, run:");
  console.log(
    `npx hardhat verify --network fuji ${address}`
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
