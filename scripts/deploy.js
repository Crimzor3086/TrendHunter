const { ethers } = require("hardhat");

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

  // Replace "YourContract" with the name of your compiled contract
  // Example: const Contract = await ethers.getContractFactory("MyToken");
  const Contract = await ethers.getContractFactory("YourContract");

  console.log("Deploying...");

  // Update constructor arguments to match your contract
  const contract = await Contract.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();

  console.log("Contract deployed to:", address);
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
