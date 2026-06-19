from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from backend.app.config import Settings
from backend.app.schemas import ContentBrief, RegistryRecord, Trend


REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "string", "name": "trendId", "type": "string"},
            {"internalType": "bytes32", "name": "trendHash", "type": "bytes32"},
            {"internalType": "string", "name": "title", "type": "string"},
            {"internalType": "string", "name": "category", "type": "string"},
            {"internalType": "uint256", "name": "score", "type": "uint256"},
            {"internalType": "string", "name": "briefHash", "type": "string"},
        ],
        "name": "registerTrend",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


def trend_hash(trend: Trend) -> str:
    payload = f"{trend.title}|{trend.first_seen.isoformat()}|{trend.category.value}|{trend.score}"
    return "0x" + sha256(payload.encode("utf-8")).hexdigest()


def fallback_brief_hash(brief: ContentBrief | None) -> str:
    if brief is None:
        return "pending"
    payload = f"{brief.trend_id}|{brief.hook}|{brief.script_30_60s}|{brief.generated_at.isoformat()}"
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


class AvalancheRegistryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def register_trend(self, trend: Trend, brief: ContentBrief | None, brief_hash: str | None = None) -> RegistryRecord:
        computed_trend_hash = trend_hash(trend)
        resolved_brief_hash = brief_hash or fallback_brief_hash(brief)
        payload = {
            "trend_id": trend.trend_id,
            "trend_hash": computed_trend_hash,
            "title": trend.title,
            "category": trend.category.value,
            "score": trend.score,
            "brief_hash": resolved_brief_hash,
        }

        if not self.settings.trend_registry_address or not self.settings.registry_private_key:
            return RegistryRecord(
                trend_id=trend.trend_id,
                trend_hash=computed_trend_hash,
                category=trend.category,
                score=trend.score,
                first_seen=trend.first_seen,
                transaction_hash=None,
                explorer_url=None,
                status="dry_run_missing_fuji_config",
                payload=payload,
            )

        try:
            from web3 import Web3
        except ImportError:
            return RegistryRecord(
                trend_id=trend.trend_id,
                trend_hash=computed_trend_hash,
                category=trend.category,
                score=trend.score,
                first_seen=trend.first_seen,
                transaction_hash=None,
                explorer_url=None,
                status="dry_run_web3_not_installed",
                payload=payload,
            )

        web3 = Web3(Web3.HTTPProvider(self.settings.avalanche_rpc_url))
        account = web3.eth.account.from_key(self.settings.registry_private_key)
        contract = web3.eth.contract(address=Web3.to_checksum_address(self.settings.trend_registry_address), abi=REGISTRY_ABI)
        nonce = web3.eth.get_transaction_count(account.address)

        tx = contract.functions.registerTrend(
            trend.trend_id,
            bytes.fromhex(computed_trend_hash[2:]),
            trend.title,
            trend.category.value,
            trend.score,
            resolved_brief_hash,
        ).build_transaction(
            {
                "chainId": self.settings.avalanche_chain_id,
                "from": account.address,
                "nonce": nonce,
            }
        )
        signed = account.sign_transaction(tx)
        raw_transaction = signed.raw_transaction if hasattr(signed, "raw_transaction") else signed.rawTransaction
        tx_hash = web3.eth.send_raw_transaction(raw_transaction).hex()

        return RegistryRecord(
            trend_id=trend.trend_id,
            trend_hash=computed_trend_hash,
            category=trend.category,
            score=trend.score,
            first_seen=trend.first_seen or datetime.now(timezone.utc),
            transaction_hash=tx_hash,
            explorer_url=f"https://testnet.snowtrace.io/tx/{tx_hash}",
            status="submitted",
            payload=payload,
        )
