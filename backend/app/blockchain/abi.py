from typing import Any

TREND_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "string", "name": "title", "type": "string"},
            {"internalType": "string", "name": "category", "type": "string"},
            {"internalType": "uint256", "name": "score", "type": "uint256"},
            {"internalType": "string", "name": "contentHash", "type": "string"},
        ],
        "name": "registerTrend",
        "outputs": [{"internalType": "uint256", "name": "trendId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "trendId", "type": "uint256"}],
        "name": "getTrend",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "string", "name": "title", "type": "string"},
                    {"internalType": "string", "name": "category", "type": "string"},
                    {"internalType": "uint256", "name": "score", "type": "uint256"},
                    {"internalType": "uint256", "name": "firstSeen", "type": "uint256"},
                    {"internalType": "string", "name": "contentHash", "type": "string"},
                    {"internalType": "address", "name": "creator", "type": "address"},
                    {"internalType": "bool", "name": "verified", "type": "bool"},
                ],
                "internalType": "struct TrendRegistry.Trend",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "trendCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "creatorReputation",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "trendId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "title", "type": "string"},
            {"indexed": True, "internalType": "address", "name": "creator", "type": "address"},
        ],
        "name": "TrendRegistered",
        "type": "event",
    },
]
