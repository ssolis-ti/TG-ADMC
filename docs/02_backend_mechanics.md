# Volume II: The Core Mechanisms (Backend)

> _"The engine does not guess; it executes."_

## 1. The Nervous System: `routes.py`

The Routing Layer is designed with **Tactical Intent**. Each endpoint serves a specific phase of the Deal Lifecycle.

- **GET /channels**: The Public Feed. Optimized with `limit/offset` for infinite scrolling.
- **POST /deals/create**: The Genesis Event. This triggers the storage of the "Deal Contract" and notifies the Channel Owner.
- **POST /confirm-payment**: The Critical Junction. This is where Web2 (API) meets Web3 (Blockchain).

## 2. The Heart: `EscrowService` (State Machine)

The Escrow logic (`src/services/escrow.py`) is the most critical component. It enforces the rules of engagement.

### The Lifecycle Flow

1.  **CREATED**: The intent is declared.
2.  **ACCEPTED**: The Channel Owner agrees to the terms.
3.  **DRAFT_SUBMITTED**: Work has been performed (Proof of Work).
4.  **AWAITING_PAYMENT**: The Advertiser validates the work.
5.  **LOCKED**: Payment is secured. **This is the Point of No Return.**
6.  **SCHEDULED/COMPLETED**: Delivery and release of value.

### Security Note

The automated transition to **LOCKED** currently trusts the Frontend's claim of a Transaction Hash. In Volume IV, we discuss hardening this link.

## 3. Identity & Authentication

We prioritize **Silent Authentication**.

- **`initData`**: We extract the signed payload from Telegram.
- **`IdentityService`**: We map the external Telegram ID (e.g., `123456`) to an internal, immutable User ID (e.g., `1`). This protects our database integrity if Telegram ever changes their API or ID structure.

## 4. The Database Schema

Our Schema (`src/db/models.py`) uses **SQLModel** (Pydantic + SQLAlchemy).

- **Users**: The Actors.
- **Channels**: The Assets.
- **Deals**: The Contracts linking Actors and Assets.
- **Relationships**: Strictly defined Foreign Keys ensure no "Orphan Deals" can exist.

---

**[Next Volume: The Interface Dynamics ->](./03_frontend_dynamics.md)**
