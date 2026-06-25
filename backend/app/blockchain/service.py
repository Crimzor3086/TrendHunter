from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from backend.app.blockchain.abi import TREND_REGISTRY_ABI
from backend.app.config import Settings
from backend.app.schemas import BlockchainStatus, ContentBrief, OnChainTrend, RegistryRecord, Trend


def trend_hash(trend: Trend) -> str:
    payload = f"{trend.title}|{trend.first_seen.isoformat()}|{trend.category.value}|{trend.score}"
    return "0x" + sha256(payload.encode("utf-8")).hexdigest()


def fallback_brief_hash(brief: ContentBrief | None) -> str:
    if brief is None:
        return "pending"
    payload = f"{brief.trend_id}|{brief.hook}|{brief.script_30_60s}|{brief.generated_at.isoformat()}"
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def build_content_hash(trend: Trend, brief: ContentBrief | None, brief_hash: str | None = None) -> str:
    """Canonical on-chain content hash: trend fingerprint + optional brief digest."""
    computed = trend_hash(trend)
    resolved_brief = brief_hash or fallback_brief_hash(brief)
    if resolved_brief == "pending":
        return computed
    return f"{computed}|{resolved_brief}"


class AvalancheRegistryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(self.settings.trend_registry_address and self.settings.registry_private_key)

    def _web3_client(self) -> Any:
        from web3 import Web3

        return Web3(Web3.HTTPProvider(self.settings.avalanche_rpc_url))

    def _contract(self, web3: Any) -> Any:
        from web3 import Web3

        address = Web3.to_checksum_address(self.settings.trend_registry_address)
        return web3.eth.contract(address=address, abi=TREND_REGISTRY_ABI)

    def get_status(self) -> BlockchainStatus:
        address = self.settings.trend_registry_address
        if not address:
            return BlockchainStatus(
                configured=False,
                rpc_url=self.settings.avalanche_rpc_url,
                chain_id=self.settings.avalanche_chain_id,
            )

        try:
            web3 = self._web3_client()
            connected = web3.is_connected()
            contract = self._contract(web3)
            trend_count = int(contract.functions.trendCount().call()) if connected else None
            signer_address = None
            if self.settings.registry_private_key:
                signer_address = web3.eth.account.from_key(self.settings.registry_private_key).address

            return BlockchainStatus(
                configured=self.is_configured(),
                rpc_url=self.settings.avalanche_rpc_url,
                chain_id=self.settings.avalanche_chain_id,
                contract_address=address,
                connected=connected,
                trend_count=trend_count,
                signer_address=signer_address,
            )
        except Exception as exc:
            return BlockchainStatus(
                configured=self.is_configured(),
                rpc_url=self.settings.avalanche_rpc_url,
                chain_id=self.settings.avalanche_chain_id,
                contract_address=address,
                connected=False,
                error=str(exc),
            )

    def list_on_chain_trends(self) -> list[OnChainTrend]:
        if not self.settings.trend_registry_address:
            return []

        web3 = self._web3_client()
        if not web3.is_connected():
            return []

        contract = self._contract(web3)
        count = int(contract.functions.trendCount().call())
        trends: list[OnChainTrend] = []

        for trend_id in range(1, count + 1):
            record = contract.functions.getTrend(trend_id).call()
            trends.append(
                OnChainTrend(
                    on_chain_trend_id=trend_id,
                    title=record[1],
                    category=record[2],
                    score=int(record[3]),
                    first_seen=int(record[4]),
                    content_hash=record[5],
                    creator=record[6],
                    verified=bool(record[7]),
                )
            )

        return trends

    def register_trend(self, trend: Trend, brief: ContentBrief | None, brief_hash: str | None = None) -> RegistryRecord:
        computed_trend_hash = trend_hash(trend)
        resolved_brief_hash = brief_hash or fallback_brief_hash(brief)
        content_hash = build_content_hash(trend, brief, resolved_brief_hash)
        payload = {
            "trend_id": trend.trend_id,
            "trend_hash": computed_trend_hash,
            "title": trend.title,
            "category": trend.category.value,
            "score": trend.score,
            "brief_hash": resolved_brief_hash,
            "content_hash": content_hash,
        }

        if not self.settings.trend_registry_address or not self.settings.registry_private_key:
            return RegistryRecord(
                trend_id=trend.trend_id,
                trend_hash=computed_trend_hash,
                category=trend.category,
                score=trend.score,
                first_seen=trend.first_seen,
                content_hash=content_hash,
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
                content_hash=content_hash,
                transaction_hash=None,
                explorer_url=None,
                status="dry_run_web3_not_installed",
                payload=payload,
            )

        try:
            web3 = self._web3_client()
            if not web3.is_connected():
                raise ConnectionError("Avalanche RPC is not reachable")

            account = web3.eth.account.from_key(self.settings.registry_private_key)
            contract = self._contract(web3)
            nonce = web3.eth.get_transaction_count(account.address)

            tx = contract.functions.registerTrend(
                trend.title,
                trend.category.value,
                trend.score,
                content_hash,
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
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.settings.tx_confirmation_timeout)

            if receipt.status != 1:
                return RegistryRecord(
                    trend_id=trend.trend_id,
                    trend_hash=computed_trend_hash,
                    category=trend.category,
                    score=trend.score,
                    first_seen=trend.first_seen,
                    content_hash=content_hash,
                    transaction_hash=tx_hash,
                    explorer_url=f"https://testnet.snowtrace.io/tx/{tx_hash}",
                    status="reverted",
                    payload=payload,
                )

            on_chain_trend_id = None
            event_logs = contract.events.TrendRegistered().process_receipt(receipt)
            if event_logs:
                on_chain_trend_id = int(event_logs[0]["args"]["trendId"])

            return RegistryRecord(
                trend_id=trend.trend_id,
                trend_hash=computed_trend_hash,
                category=trend.category,
                score=trend.score,
                first_seen=trend.first_seen or datetime.now(timezone.utc),
                content_hash=content_hash,
                on_chain_trend_id=on_chain_trend_id,
                transaction_hash=tx_hash,
                explorer_url=f"https://testnet.snowtrace.io/tx/{tx_hash}",
                status="confirmed",
                payload=payload,
            )
        except Exception as exc:
            return RegistryRecord(
                trend_id=trend.trend_id,
                trend_hash=computed_trend_hash,
                category=trend.category,
                score=trend.score,
                first_seen=trend.first_seen,
                content_hash=content_hash,
                transaction_hash=None,
                explorer_url=None,
                status=f"failed:{exc}",
                payload=payload,
            )
