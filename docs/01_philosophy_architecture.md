# Volume I: The Genesis & Philosophy

> _"Code is but the manifestation of thought. Architecture is the manifestation of intent."_

## 1. The Vision: Why TG-ADMC?

### The Problem

The Telegram Ad ecosystem is currently fragmented. Deals happen in DMs, trust is based on reputation alone, and payments are manual. There is no **System of Record**.

**Real-world pain points:**

- Advertisers risk prepayment without delivery guarantee
- Channel owners risk work without payment guarantee
- No proof of publication or transaction history
- Manual coordination creates friction and delays

### The Solution

TG-ADMC (Telegram Ads Marketplace Core) acts as the **Trust Engine**. It introduces a structured workflow:

1. **Verification**: Channels are not just claimed; they are verified via bot admin checks.
2. **Escrow**: Funds are locked in TON blockchain before work begins, protecting both parties.
3. **Automation**: The bot acts as the impartial mediator, automating notifications and state transitions.
4. **Proof**: Every deal has on-chain payment proof and published message links.

**Result**: Zero-trust marketplace where code enforces fairness.

---

## 2. Architectural Design: The "Fortress" Approach

We utilize a **Modular Monolith** architecture, containerized via Docker. This ensures that while the code lives in one repository for ease of MVP development, the logical components are strictly separated—ready to be peeled off into microservices.

### The Triad

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Telegram)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼────┐              ┌────▼────┐
   │   Bot   │              │ WebApp  │
   │ (aiogram│              │(Vanilla │
   │  Agent) │              │   JS)   │
   └────┬────┘              └────┬────┘
        │                        │
        └────────────┬───────────┘
                     │
            ┌────────▼────────┐
            │   API Gateway   │
            │    (FastAPI)    │
            │   Async Core    │
            └────────┬────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼───┐   ┌───▼────┐
   │PostgreSQL│  │  TON  │   │Scheduler│
   │  (State) │  │Gateway│   │ (APScheduler)│
   └──────────┘  └───────┘   └────────┘
```

#### 1. **The API Gateway (FastAPI)**: The Brain

- Handles all I/O, validation, and business logic routing
- Stateless and horizontally scalable
- Async/await throughout - never blocks
- Pydantic models enforce type safety at boundaries

#### 2. **The State Keeper (PostgreSQL)**: The Memory

- Relational logic because a Deal is a rigid contract
- ACID transactions ensure state consistency
- Steps (PENDING → PAID → ACCEPTED → COMPLETED) must be preserved transactionally
- SQLAlchemy ORM with async support

#### 3. **The Bot Agent (Aiogram)**: The Hands

- Reaches into Telegram ecosystem to pull users in
- Notifies owners of new deals
- Posts ads to channels automatically
- Our "Virality Vector" - every interaction is a growth opportunity

---

## 3. Technology Rationale

### Why FastAPI?

**Speed**: Asynchronous by default. Critical for handling thousands of webhook events.

```python
# Every endpoint is async - no blocking
@router.post("/api/deal/create")
async def create_deal(
    deal: DealCreate,
    user_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Database calls are awaited, not blocking
    result = await session.execute(...)
    return result
```

**Type Safety**: Pydantic models ensure that data corruption is rejected at the gate.

```python
class DealCreate(BaseModel):
    channel_id: int
    ad_brief: str
    amount_ton: float = Field(gt=0)  # Must be positive
```

**Developer Experience**: Auto-generated OpenAPI docs, dependency injection, and excellent error messages.

---

### Why Vanilla JS (Frontend)?

**Performance**: React/Vue payloads are heavy for a Mini App that must load instantly on 3G networks globally.

- **Bundle size**: ~50KB vs 500KB+ for React
- **Load time**: <1s on slow connections
- **No build step**: Direct ES6 modules in development

**Simplicity**: By using ES6 Modules, we achieve component-style organization without the build-step complexity (Webpack/Vite) for the MVP phase.

```javascript
// Clean module separation
import { API } from "./api.js";
import { Wallet } from "./wallet.js";
import { UI } from "./ui.js";

// Composable, testable, maintainable
export async function createDeal(channelId, brief, amount) {
  await Wallet.sendPayment(amount);
  await API.createDeal(channelId, brief);
  UI.showSuccess();
}
```

**Telegram Native**: Telegram WebApp SDK works perfectly with vanilla JS. No framework conflicts.

---

### Why TON (The Open Network)?

**Native**: It is the only ledger users in Telegram already have in their pocket.

- Tonkeeper is pre-installed for many users
- No need to explain "what is crypto" - they already use it

**Speed**: Finality is seconds, not minutes.

- Transaction confirmed in <10 seconds
- Users see payment success immediately
- No waiting for "6 confirmations"

**Cost**: Micro-transactions are viable, enabling small ad deals (e.g., 0.1 TON).

- Gas fees are negligible (~0.01 TON)
- Makes sense for $5-10 ad deals
- Ethereum would cost more in gas than the ad itself

---

## 4. Programming Philosophy

### Principle 1: **Async by Default**

Every I/O operation is async. Database calls, HTTP requests, file operations - all use `await`.

**Why?** A single blocking call can freeze the entire event loop, degrading performance for all users.

```python
# ❌ BAD - Blocks event loop
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

# ✅ GOOD - Non-blocking
async def get_user(user_id):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

---

### Principle 2: **Type Safety as Contract**

Pydantic models are not just validation - they are **contracts** between components.

```python
class DealResponse(BaseModel):
    id: int
    status: DealStatus  # Enum, not string
    amount_ton: float
    created_at: datetime

    class Config:
        from_attributes = True  # Works with SQLAlchemy
```

If a function returns `DealResponse`, you **know** it has these fields with these types. No guessing.

---

### Principle 3: **Separation of Concerns**

Each module has one job:

- `routes.py`: HTTP routing only
- `services/`: Business logic
- `db/models.py`: Data structure
- `bot/handlers/`: Telegram interaction

**No mixing**. A route should never contain business logic. A service should never know about HTTP.

---

### Principle 4: **Fail Fast, Fail Loud**

```python
if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

Don't return `None` and hope the caller checks. Don't log and continue. **Crash immediately** with a clear error.

This makes bugs obvious during development, not in production.

---

### Principle 5: **Code is Documentation**

```python
async def send_ton_transfer(
    self,
    destination: str,  # TON address in user-friendly format
    amount: float,     # Amount in TON (not nanoTON)
    memo: str          # Transaction comment
) -> Optional[str]:    # Returns tx hash or None on failure
    """
    [PAYOUT ENGINE]: Signs and sends a transaction using the Server Mnemonic.

    This is called automatically after a deal is published to pay the channel owner.
    """
```

Function names, parameter names, and docstrings should make the code self-explanatory.

---

## 5. The MVP Mindset

### What We Built

✅ **Core Flow**: Catalog → Deal → Payment → Escrow → Auto-post → Payout
✅ **Real Integration**: TON testnet, real wallets, real transactions
✅ **Production Deployment**: Cloudflare tunnel, Docker, PostgreSQL
✅ **Both Roles**: Advertiser and Owner flows fully functional

### What We Simplified (For Now)

🚧 **Security**: Mnemonic in `.env` (OK for testnet, not for mainnet)
🚧 **Monitoring**: Basic logging (production needs metrics, alerts)
🚧 **Disputes**: Simple accept/reject (production needs arbitration)
🚧 **Edge Cases**: Happy path works (production needs retry logic, timeouts)

### Why This Is The Right Approach

**For Hackathon**: Judges want to see a working end-to-end flow. We delivered that.

**For Grant Phase**: We have a clear roadmap of what to harden for production.

**For Users**: The core value proposition is proven. The rest is engineering.

---

## 6. Success Metrics

| Metric          | Target  | Actual        | Status       |
| --------------- | ------- | ------------- | ------------ |
| End-to-end flow | Working | ✅ 7 deals    | **EXCEEDED** |
| TON integration | Testnet | ✅ Real txs   | **ACHIEVED** |
| Deployment      | Demo    | ✅ Production | **EXCEEDED** |
| Success rate    | >80%    | 100%          | **EXCEEDED** |
| Uptime          | >1 hour | 11+ hours     | **EXCEEDED** |

---

**[Next Volume: The Core Mechanisms →](./02_backend_mechanics.md)**
