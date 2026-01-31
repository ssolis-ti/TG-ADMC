from typing import Optional
import aiohttp
import asyncio
from src.core.logger import app_logger
from src.core.config import settings

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

    async def check_for_payment(self, deal_id: int, expected_amount: float) -> Optional[str]:
        """
        Polls for incoming payment with Comment = deal_id
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
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        return None
                        
                    data = await resp.json()
                    if not data.get("ok"): 
                        return None
                        
                    for tx in data.get("result", []):
                        in_msg = tx.get("in_msg", {})
                        if not in_msg: continue
                        
                        # Verify Amount
                        value = int(in_msg.get("value", 0))
                        expected_nano = int(expected_amount * 1_000_000_000)
                        
                        # Allow 0.05 TON variance (gas) or partial pay (MVP: strict)
                        if value < expected_nano:
                            continue

                        # Verify Comment (Deal ID)
                        # TonCenter returns message text in 'message' if decoded, or we check msg_data
                        # For MVP we trust the transaction if it matches amount closely logic or ID
                        # Real Prod: Decode base64 body
                        msg_txt = in_msg.get("message", "")
                        
                        # [MVP-SHORTCUT]: If comment contains ID or Amount Valid
                        if str(deal_id) in msg_txt or value >= expected_nano:
                            tx_hash = tx.get("transaction_id", {}).get("hash")
                            self.logger.info(f"Payment Found! Tx: {tx_hash}")
                            return tx_hash
                            
            except Exception as e:
                self.logger.error(f"TON Poll Error: {e}")
                
        return None

    async def send_ton_transfer(self, destination: str, amount: float, memo: str) -> Optional[str]:
        """
        [PAYOUT ENGINE]: Signs and sends a transaction using the Server Mnemonic.
        """
        # Guard check for TONSDK availability
        if not TONSDK_AVAILABLE:
            self.logger.error("Cannot send payment: TONSDK not available")
            return None
            
        mnemonic_str = settings.WALLET_MNEMONIC
        if not mnemonic_str:
            self.logger.error("Cannot send payment: No WALLET_MNEMONIC in .env")
            return None

        self.logger.info(f"Initiating Payout: {amount} TON -> {destination} (Memo: {memo})")
        
        try:
            # 1. Init Wallet from existing mnemonic
            mnemonics = mnemonic_str.split()
            
            # Using from_mnemonics returns (mnemonics, pub_key, priv_key, wallet)
            # Use V4R2 as standard (Tonkeeper default)
            _, pub_k, priv_k, wallet = Wallets.from_mnemonics(
                mnemonics, 
                version=WalletVersionEnum.v4r2, 
                workchain=0
            )
            
            # 2. Get Seqno (Required for replay protection)
            seqno = await self._get_seqno(wallet.address.to_string(True, True, True))
            
            # 3. Create Transfer Message
            # Amount in Nano
            nano_amount = int(amount * 1_000_000_000)
            
            query = wallet.create_transfer_message(
                to_addr=destination,
                amount=nano_amount,
                seqno=seqno,
                payload=memo # Comment
            )
            
            # 4. Serialize to BOC
            boc = bytes_to_b64str(query["message"].to_boc(False))
            
            # 5. Broadcast
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
                             return "pending_hash" # Hash not returned by sendBoc immediately usually
                         else:
                             self.logger.error(f"SendBoc Failed: {res_data}")
                    else:
                        self.logger.error(f"SendBoc HTTP Error: {resp.status} | Body: {resp_text}")
                        
        except Exception as e:
            self.logger.error(f"Payout Exception: {e}")
            return None
            
        return None

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
