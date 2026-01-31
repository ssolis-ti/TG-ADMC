# Volume IV: The Web3 Horizon

> _"Trust Code, Not Corporations."_

## 1. The Integration: "Dual-Net" Strategy

We have designed the system to be **Network Agnostic** but **Protocol Specific**.

- **Testnet**: For zero-risk development. Used during the MVP phase.
- **Mainnet**: For value transfer. Requires a simple configuration switch in `.env` (`TON_API_URL`).

## 2. The Bridge: `wallet.js` & `ton.py`

We bridge the gap between Web2 (Server) and Web3 (Blockhain) using two anchors:

1.  **Client-Side (Wallet.js)**: Uses `TON Connect UI`. This allows the user to sign transactions using their preferred wallet (Tonkeeper, Telegram Wallet).
2.  **Server-Side (Ton.py)**: Acts as the "Watcher". It continuously polls the public ledger (via TonCenter API) to verify that funds have actually moved.

## 3. Clinical Audit: The "Finality" Gap

**Current State (MVP)**:

- The Backend validates that a payment of amount `X` with comment `Y` exists.
- **Risk**: A split-second blockchain "re-organization" could theoretically erase a transaction that we just marked as valid.

**Prescription (For V2)**:

- Implement a **Confirmation Depth** check (wait for 5-10 blocks).
- Or migrate to a Smart Contract where the atomic swap happens on-chain.

## 4. The Future: From Hybrid to DeFi

Currently, `EscrowService` is a Python Class.
**The Evolution**:

- Migrate `EscrowService` to a **Smart Contract** (written in Tact or FunC).
- The Python backend will then become merely an "Indexer" (a read-only view) of the on-chain truth, rather than the authority.

---

**[Return to Master Index](./00_master_index.md)**
