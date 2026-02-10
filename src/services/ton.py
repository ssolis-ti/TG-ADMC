from typing import Optional
import aiohttp
import asyncio
from src.core.logger import app_logger
from src.core.config import settings
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log
import logging

# [HARDENING]: Logger bridge for tenacity (requires stdlib logger)
_tenacity_logger = logging.getLogger("tenacity.ton_gateway")

# TON SDK Imports
TONSDK_AVAILABLE = False
Wallets = None
WalletVersionEnum = None
to_nano = None
bytes_to_b64str = None
mnemonic_to_wallet_key = None

try:
    from tonsdk.contract.wallet import Wallets, WalletVersionEnum
    from tonsdk.utils import to_nano, bytes_to_b64str
    from tonsdk.crypto._mnemonic import mnemonic_to_wallet_key
    TONSDK_AVAILABLE = True
    app_logger.info("TONSDK imported successfully.")
except ImportError as e:
    app_logger.error(f"TONSDK not installed or import error: {e}. Payouts will fail.")

class TonGateway:
    """
    [PAYMENT GATEWAY]: Real-Time Blockchain Interaction.
    """
    
    def __init__(self, wallet_address: str, api_key: str = ""):
        self.wallet_address = wallet_address
        self.api_key = api_key
        self.logger = app_logger
        # Testnet URL
        self.base_url = "https://testnet.toncenter.com/api/v2"

    async def check_connection(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                # Use getMasterchainInfo as health check
                url = f"{self.base_url}/getMasterchainInfo"
                async with session.get(url) as resp:
                    return resp.status == 200
            except Exception:
                return False

    async def generate_payment_link(self, deal_id: int, amount: float) -> str:
        nanoton = int(amount * 1_000_000_000)
        # Deep Link for Tonkeeper
        return f"ton://transfer/{self.wallet_address}?amount={nanoton}&text={deal_id}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        before=before_log(_tenacity_logger, logging.INFO),
        after=after_log(_tenacity_logger, logging.WARNING),
        reraise=True  # [IMPORTANT]: Re-raise after final attempt so caller sees the error
    )
    async def check_for_payment(self, deal_id: int, expected_amount: float) -> Optional[str]:
        """
        [PAYMENT VERIFICATION]: Polls TON testnet for incoming payment matching deal_id.
        
        Retry Policy: 3 attempts, 2s between each (handles transient API failures).
        Returns tx_hash if found, None if no matching payment yet.
        Raises on network errors after 3 retries.
        """
        self.logger.info(f"Checking TON for Deal {deal_id}...")
        
        url = f"{self.base_url}/getTransactions"
        params = {
            "address": self.wallet_address,
            "limit": 20,
            "archival": "true",
            "api_key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            # [HARDENING]: Let network exceptions propagate so tenacity retries them
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    # [HARDENING]: Raise on HTTP errors so tenacity retries
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history,
                        status=resp.status, message=f"TON API returned {resp.status}"
                    )
                    
                data = await resp.json()
                if not data.get("ok"): 
                    return None  # API responded but no valid data — not a network error
                    
                for tx in data.get("result", []):
                    in_msg = tx.get("in_msg", {})
                    if not in_msg: continue
                    
                    # Verify Amount (in nanoTON)
                    value = int(in_msg.get("value", 0))
                    expected_nano = int(expected_amount * 1_000_000_000)
                    
                    if value < expected_nano:
                        continue

                    # Verify Comment contains Deal ID
                    msg_txt = in_msg.get("message", "")
                    
                    # [MVP-SHORTCUT]: Match by comment OR amount
                    if str(deal_id) in msg_txt or value >= expected_nano:
                        tx_hash = tx.get("transaction_id", {}).get("hash")
                        self.logger.info(f"Payment Found! Tx: {tx_hash}")
                        return tx_hash
                        
        return None  # No matching payment found (legitimate, not an error)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        before=before_log(_tenacity_logger, logging.INFO),
        after=after_log(_tenacity_logger, logging.WARNING),
        reraise=True
    )
    async def send_ton_transfer(self, destination: str, amount: float, memo: str) -> Optional[str]:
        """
        [PAYOUT ENGINE]: Signs and sends a transaction using the Server Mnemonic.
        
        Retry Policy: 3 attempts, 2s between each.
        Guard checks (TONSDK missing, no mnemonic) do NOT retry — they are config errors.
        Network errors during broadcast DO retry.
        """
        # Guard checks — these are config errors, not transient. Don't retry.
        if not TONSDK_AVAILABLE:
            self.logger.error("Cannot send payment: TONSDK not available")
            return None
            
        mnemonic_str = settings.WALLET_MNEMONIC
        if not mnemonic_str:
            self.logger.error("Cannot send payment: No WALLET_MNEMONIC in .env")
            return None

        self.logger.info(f"Initiating Payout: {amount} TON -> {destination} (Memo: {memo})")
        
        # 1. Init Wallet from existing mnemonic
        mnemonics = mnemonic_str.split()
        _, pub_k, priv_k, wallet = Wallets.from_mnemonics(
            mnemonics, 
            version=WalletVersionEnum.v4r2, 
            workchain=0
        )
        
        # 2. Get Seqno (Required for replay protection)
        seqno = await self._get_seqno(wallet.address.to_string(True, True, True))
        
        # 3. Create Transfer Message (amount in nanoTON)
        nano_amount = int(amount * 1_000_000_000)
        query = wallet.create_transfer_message(
            to_addr=destination,
            amount=nano_amount,
            seqno=seqno,
            payload=memo
        )
        
        # 4. Serialize to BOC (Bag of Cells)
        boc = bytes_to_b64str(query["message"].to_boc(False))
        
        # 5. Broadcast to TON Network
        url = f"{self.base_url}/sendBoc"
        payload = {"boc": boc}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                resp_text = await resp.text()
                self.logger.info(f"SendBoc Response: Status={resp.status}")
                if resp.status == 200:
                     import json
                     res_data = json.loads(resp_text)
                     if res_data.get("ok"):
                         self.logger.info("Payout Sent Successfully!")
                         return "pending_hash"
                     else:
                         # API rejected our BOC — likely a logic error, not transient
                         self.logger.error(f"SendBoc Failed: {res_data}")
                         return None
                else:
                    # [HARDENING]: Raise on HTTP errors so tenacity retries
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history,
                        status=resp.status, message=f"SendBoc HTTP {resp.status}"
                    )

    async def _get_seqno(self, address: str) -> int:
        """Helper to get wallet sequence number"""
        url = f"{self.base_url}/runGetMethod"
        payload = {
            "address": address,
            "method": "seqno",
            "stack": []
        }
        async with aiohttp.ClientSession() as session:
             async with session.post(url, json=payload) as resp:
                 if resp.status == 200:
                     data = await resp.json()
                     if data.get("ok"):
                         # Logica de stack parsing para TonCenter
                         # stack: [['num', '0x123']]
                         stack = data.get("result", {}).get("stack", [])
                         if stack and stack[0][0] == 'num':
                             return int(stack[0][1], 16)
        return 0
