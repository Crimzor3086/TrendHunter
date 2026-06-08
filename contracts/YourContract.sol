// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// This file is a placeholder. Replace it with your own contract.
//
// Week 1: No contract required — you are sending a basic transaction.
//
// Week 2: Write an ERC-20 token here. Start from scratch or extend OpenZeppelin:
//   import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
//
// Week 3: Your payment contract lives here. Record M-Pesa transaction references
//         on-chain if you are bridging to the blockchain.
//
// Week 4: Your final payment contract — accepts USDC, records receipts,
//         handles both M-Pesa and on-chain flows.
//
// Compile check: npx hardhat compile
// Test: npx hardhat test
// Deploy to Fuji: npx hardhat run scripts/deploy.js --network fuji

contract YourContract {
    address public owner;

    event Deployed(address indexed owner, uint256 timestamp);

    constructor() {
        owner = msg.sender;
        emit Deployed(msg.sender, block.timestamp);
    }
}
