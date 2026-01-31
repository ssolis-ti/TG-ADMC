# Volume V: The Security & Risk Codex

> _"Security is not a feature. It is a state of mind."_

## 1. SWOT Analysis: The Strategic View

### Strengths (The Fortress)

- **Modular Isolation**: Our "Lego" architecture limits the blast radius. If the Frontend (`wallet.js`) is compromised, the Backend (`escrow.py`) remains the final authority on state.
- **Platform Leverage**: By stripping identity management and offloading it to Telegram (`initData`), we eliminate 90% of traditional phishing vectors (Password theft is impossible because there are no passwords).
- **Silent Auth**: The removal of "Simulate ID" in production effectively creates a permissioned environment. Only valid Telegram sessions can enter.

### Weaknesses (The Cracks)

- **Centralized Oracle**: The `EscrowService` currently acts as a centralized oracle. If the server is hacked, the "Truth" of the deal status can be manipulated (though funds on blockchain remain safe, the metadata is vulnerable).
- **Blind Trust (MVP)**: The backend currently trusts the tx_hash provided by the user without performing a deep cryptographic verification of the sender's signature in relation to the deal.

### Opportunities (The Potential)

- **Trustless Escrow**: Migrating `EscrowService` to a Tact Smart Contract would make the system **Unstoppable**. Even if the servers burn down, the deals and funds would exist on-chain.
- **Reputation Token**: We can tokenize the "Verified" status. Good actors earn SBTs (Soulbound Tokens); bad actors get slashed.

### Threats (The Vectors)

- **Sybil Attacks**: Users creating 100 fake channels to spam brief requests. Current mitigation: `IdentityService` maps 1-to-1 TG ID, but TG accounts are cheap.
- **Replay Attacks**: A user taking a valid transaction hash from the block explorer and submitting it to our API as if it were their new payment.

## 2. Abuse Prevention: The "Anti-Cheat" Guidelines

### Vector A: The "Fake Payer" (Replay Attack)

- **Scenario**: User A pays 5 TON. User B copies the hash and Send it to `confirm-payment`.
- **Defense (Implemented)**: `IdentityService` checks ownership.
- **Defense (Required V2)**: The Payment Comment (Memo) **MUST** equal the `deal_id`. If the comment on-chain does not match the deal ID, the backend acts as a firewall and rejects the confirmation.

### Vector B: The "Forever Pending" (Dos)

- **Scenario**: Attacker creates 10,000 deals but never pays, clogging the database.
- **Defense**: Implement a `TTL` (Time To Live). If a deal remains in `CREATED` for > 24 hours, the `Scheduler` (Heartbeat) auto-archives it.

### Vector C: The "Switcheroo" (Content Injection)

- **Scenario**: Channel Owner submits a safe draft, gets approved, then edits the post to scams _after_ payment.
- **Defense**: The Bot must verify the _final_ public post against the _approved_ draft hash. If they mismatch, the "Completed" status is revoked and the user is flagged.

## 3. QA Guidelines: The Clinical Audit

### Phase 1: The Happy Path (Integration Testing)

1.  **Flow**: Create -> Accept -> Pay -> Verify.
2.  **Metric**: Success rate must be 100%. Any friction here kills conversion.

### Phase 2: The Stress Test (Load Testing)

1.  **Scenario**: 100 Users clicking "Pay" simultaneously.
2.  **Risk**: Database locking (Race Conditions).
3.  **Insight**: Our usage of `AsyncSession` and `Select for Update` (row locking) in `lock_funds` is critical here.

### Phase 3: The Red Team (Penetration Testing)

1.  **Task**: Try to call `/api/deals/{id}/approve` as the Channel Owner (not the Advertiser).
2.  **Expected**: `403 Forbidden`. The `Role Guard` logic must be impenetrable.

---

**[Return to Master Index](./00_master_index.md)**
