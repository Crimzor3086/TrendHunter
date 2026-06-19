// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract TrendRegistry {
    uint256 public trendCount;
    address public owner;

    struct Trend {
        uint256 id;
        string title;
        string category;
        uint256 score;
        uint256 firstSeen;
        string contentHash;
        address creator;
        bool verified;
    }

    mapping(uint256 => Trend) public trends;
    mapping(address => uint256) public creatorReputation;

    event TrendRegistered(uint256 indexed trendId, string title, address indexed creator);
    event TrendVerified(uint256 indexed trendId);
    event TrendScoreUpdated(uint256 indexed trendId, uint256 oldScore, uint256 newScore);
    event ContentHashUpdated(uint256 indexed trendId, string contentHash);

    error EmptyTitle();
    error EmptyCategory();
    error EmptyContentHash();
    error TrendNotFound(uint256 trendId);
    error NotOwner();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier trendExists(uint256 trendId) {
        if (trendId == 0 || trendId > trendCount) revert TrendNotFound(trendId);
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerTrend(
        string memory title,
        string memory category,
        uint256 score,
        string memory contentHash
    ) external returns (uint256 trendId) {
        if (bytes(title).length == 0) revert EmptyTitle();
        if (bytes(category).length == 0) revert EmptyCategory();
        if (bytes(contentHash).length == 0) revert EmptyContentHash();

        trendCount++;
        trendId = trendCount;

        trends[trendId] = Trend({
            id: trendId,
            title: title,
            category: category,
            score: score,
            firstSeen: block.timestamp,
            contentHash: contentHash,
            creator: msg.sender,
            verified: false
        });

        creatorReputation[msg.sender] += 1;

        emit TrendRegistered(trendId, title, msg.sender);
    }

    function verifyTrend(uint256 trendId) external onlyOwner trendExists(trendId) {
        trends[trendId].verified = true;
        creatorReputation[trends[trendId].creator] += 3;

        emit TrendVerified(trendId);
    }

    function updateScore(uint256 trendId, uint256 newScore) external trendExists(trendId) {
        uint256 oldScore = trends[trendId].score;
        trends[trendId].score = newScore;

        emit TrendScoreUpdated(trendId, oldScore, newScore);
    }

    function updateContentHash(uint256 trendId, string memory contentHash) external trendExists(trendId) {
        if (bytes(contentHash).length == 0) revert EmptyContentHash();

        trends[trendId].contentHash = contentHash;
        creatorReputation[msg.sender] += 1;

        emit ContentHashUpdated(trendId, contentHash);
    }

    function getTrend(uint256 trendId) external view trendExists(trendId) returns (Trend memory) {
        return trends[trendId];
    }
}
