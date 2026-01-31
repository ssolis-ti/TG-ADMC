# TG-ADMC: Project Overview

> **Hackathon Submission for TON Ecosystem Contest**

---

## 📊 Quick Facts

| Aspect              | Details                                            |
| ------------------- | -------------------------------------------------- |
| **Project Name**    | TG-ADMC (Telegram Ads Marketplace Core)            |
| **Category**        | Decentralized Marketplace                          |
| **Blockchain**      | TON (The Open Network)                             |
| **Status**          | MVP Complete - Production Deployed                 |
| **Demo Bot**        | [@AdTGram_Bot](https://t.me/AdTGram_Bot)           |
| **Live URL**        | [https://tgadmc.mpbot.cl](https://tgadmc.mpbot.cl) |
| **Deals Completed** | 7 (100% success rate)                              |

---

## 🎯 Problem Statement

The Telegram advertising ecosystem is fragmented and trust-based:

- Advertisers risk prepayment without delivery guarantee
- Channel owners risk work without payment guarantee
- No proof of publication or transaction history
- Manual coordination creates friction and delays

**Result**: High transaction costs, low trust, limited market efficiency.

---

## 💡 Solution

TG-ADMC is a **trust-minimized marketplace** that uses TON blockchain for escrow and proof:

1. **Verified Channels**: Bot verifies ownership before listing
2. **Escrow Payments**: Funds locked on-chain until ad is published
3. **Auto-Publishing**: Bot posts ads automatically on approval
4. **Instant Payouts**: Owners receive payment immediately after posting
5. **Blockchain Proof**: Every transaction recorded on TON testnet

**Value Proposition**: Zero-trust marketplace where code enforces fairness.

---

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Telegram)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼────┐              ┌────▼────┐
   │   Bot   │              │ WebApp  │
   │(aiogram)│◄────────────►│(Vanilla │
   │ Agent   │   Webhooks   │   JS)   │
   └────┬────┘              └────┬────┘
        │                        │
        │    ┌───────────────────┘
        │    │
   ┌────▼────▼────┐
   │  API Gateway │
   │   (FastAPI)  │
   │  Async Core  │
   └────┬────┬────┘
        │    │
   ┌────▼────▼────┬────────────┐
   │              │            │
┌──▼──┐      ┌───▼───┐   ┌───▼────┐
│PostgreSQL  │  TON  │   │Scheduler│
│  (State)   │Gateway│   │(APSched)│
└────────┘   └───────┘   └────────┘
```

### Technology Stack

**Backend**:

- **FastAPI** (async web framework) - High performance, type-safe
- **aiogram** (Telegram Bot API) - Modern async bot library
- **PostgreSQL** - ACID compliance for deal state machine
- **SQLModel** - Pydantic + SQLAlchemy for type safety
- **APScheduler** - Background task scheduling
- **tonsdk** - TON blockchain SDK for payments

**Frontend**:

- **Vanilla JavaScript (ES6+)** - Zero build step, instant load
- **TON Connect UI** - Wallet integration
- **Telegram WebApp SDK** - Mini App integration

**Infrastructure**:

- **Docker + Docker Compose** - Containerization
- **Cloudflare Tunnel** - Secure public access
- **PostgreSQL 15** - Production database

---

## 🔑 Key Technical Decisions

### 1. Modular Monolith Architecture

**Decision**: Single codebase with strict module separation

**Rationale**:

- **MVP Speed**: Faster development than microservices
- **Type Safety**: Shared Pydantic models across modules
- **Future-Proof**: Modules can be extracted to microservices later

**Trade-off**: Horizontal scaling requires load balancer (acceptable for MVP)

---

### 2. Vanilla JavaScript (No Framework)

**Decision**: ES6 modules instead of React/Vue

**Rationale**:

- **Performance**: 50KB vs 500KB+ bundle size
- **Load Time**: <1s on 3G networks (critical for global reach)
- **Simplicity**: No build step, direct debugging
- **Telegram Native**: WebApp SDK works perfectly with vanilla JS

**Trade-off**: More manual DOM manipulation (acceptable for MVP scope)

---

### 3. Python Escrow (Not Smart Contract)

**Decision**: Server-side escrow with TONSDK instead of TON smart contract

**Rationale**:

- **MVP Speed**: Faster to implement and test
- **Flexibility**: Easy to modify business logic
- **Cost**: No gas fees for contract deployment/calls
- **Testnet**: Sufficient for hackathon demo

**Future Plan**: Migrate to smart contract in grant phase for trustlessness

---

### 4. Async/Await Throughout

**Decision**: Every I/O operation is async

**Rationale**:

- **Performance**: Never block event loop
- **Scalability**: Handle 1000+ concurrent users
- **Best Practice**: FastAPI and aiogram are async-first

**Implementation**: All database calls, HTTP requests, and bot handlers use `await`

---

### 5. Type Safety with Pydantic

**Decision**: Pydantic models for all data validation

**Rationale**:

- **Correctness**: Invalid data rejected at API boundary
- **Documentation**: Models serve as API docs
- **IDE Support**: Autocomplete and type checking

**Example**:

```python
class DealCreate(BaseModel):
    channel_id: int
    ad_brief: str
    amount_ton: float = Field(gt=0)  # Must be positive
```

---

## 🚀 Implementation Highlights

### 1. Deal State Machine

```python
class DealStatus(str, Enum):
    PENDING = "PENDING"      # Created, awaiting payment
    PAID = "PAID"            # Payment confirmed, awaiting owner
    ACCEPTED = "ACCEPTED"    # Owner accepted, scheduled
    COMPLETED = "COMPLETED"  # Published and paid out
    REJECTED = "REJECTED"    # Owner rejected
```

**Transitions**:

- PENDING → PAID (on TON payment confirmation)
- PAID → ACCEPTED (owner approval)
- ACCEPTED → COMPLETED (bot publishes + payout)
- PAID → REJECTED (owner rejection)

---

### 2. Automated Publishing

**Scheduler** checks every minute for `ACCEPTED` deals:

```python
@scheduler.scheduled_job('interval', minutes=1)
async def check_scheduled_posts():
    deals = await get_accepted_deals()
    for deal in deals:
        await bot.send_message(deal.channel_id, deal.ad_brief)
        await send_payout_to_owner(deal)
        await mark_deal_completed(deal)
```

---

### 3. TON Integration

**Payment Flow**:

1. Advertiser clicks "Buy Ad"
2. Frontend calls `Wallet.sendPayment(amount, dealId)`
3. TON Connect opens Tonkeeper
4. User confirms transaction
5. Backend polls TON API for confirmation
6. Deal status → PAID

**Payout Flow**:

1. Deal published successfully
2. Backend calls `ton.send_ton_transfer(owner_wallet, amount)`
3. Server signs transaction with escrow mnemonic
4. Transaction broadcasted to TON testnet
5. Owner receives payment instantly

---

## 📈 Current Metrics

| Metric              | Value                  |
| ------------------- | ---------------------- |
| **Completed Deals** | 7                      |
| **Success Rate**    | 100%                   |
| **Total Volume**    | 0.7 TON (testnet)      |
| **Uptime**          | 11+ hours continuous   |
| **Response Time**   | <500ms average         |
| **Users**           | 2 (Owner + Advertiser) |
| **Channels**        | 1 verified             |

---

## 🚧 Known Limitations

### Security

**Current**: Mnemonic stored in `.env` file
**Risk**: Acceptable for testnet, **not for mainnet**
**Mitigation Plan**: HSM or multi-sig wallet in grant phase

### Dispute Resolution

**Current**: Simple accept/reject
**Limitation**: No arbitration for disputes
**Mitigation Plan**: Implement dispute flow with evidence submission

### Edge Cases

**Current**: Happy path optimized
**Limitation**: Limited retry logic for network failures
**Mitigation Plan**: Add circuit breakers, idempotency keys

### Monitoring

**Current**: Basic stdout logging
**Limitation**: No metrics, alerts, or APM
**Mitigation Plan**: Prometheus + Grafana + PagerDuty

---

## 🔮 Future Roadmap

### Phase 1: Security Hardening (Weeks 1-4)

- [ ] HSM for key management
- [ ] Multi-sig escrow wallet
- [ ] Rate limiting
- [ ] Security audit

### Phase 2: Reliability (Weeks 5-8)

- [ ] Redis caching
- [ ] Load balancing
- [ ] Transaction retry logic
- [ ] Performance benchmarking

### Phase 3: Features (Weeks 9-12)

- [ ] Dispute resolution
- [ ] Analytics dashboard
- [ ] Multi-channel management
- [ ] Scheduled posting

### Phase 4: Mainnet (Weeks 13-16)

- [ ] Smart contract deployment
- [ ] Legal compliance
- [ ] User onboarding
- [ ] Public launch

---

## 🤖 AI Code Percentage

### Breakdown

| Component            | AI-Generated                  | Human-Written                 | Percentage  |
| -------------------- | ----------------------------- | ----------------------------- | ----------- |
| **Backend (Python)** | Architecture, boilerplate     | Business logic, debugging     | **~60% AI** |
| **Frontend (JS)**    | Module structure, TON Connect | UI logic, error handling      | **~50% AI** |
| **Database Models**  | Schema generation             | Relationships, constraints    | **~70% AI** |
| **Documentation**    | Structure, formatting         | Content, philosophy           | **~80% AI** |
| **Docker/DevOps**    | Configuration                 | Optimization, troubleshooting | **~40% AI** |

### Overall Estimate

**~60% AI-generated, 40% human-written**

### Methodology

**AI Contributions** (via Antigravity/Claude):

- Initial code scaffolding
- Boilerplate generation
- Documentation structure
- Bug identification and fixes
- Code refactoring suggestions

**Human Contributions**:

- Architecture decisions
- Business logic design
- Bug diagnosis and resolution
- Integration testing
- Production deployment
- Philosophy and vision

### Transparency Note

All AI-generated code was:

1. **Reviewed** for correctness and security
2. **Tested** in development and production
3. **Refactored** to match project style
4. **Debugged** when issues arose
5. **Optimized** for performance

The AI served as a **productivity multiplier**, not a replacement for engineering judgment.

---

## 🎓 Lessons Learned

### What Worked Well

1. **Async/Await**: Never blocked, excellent performance
2. **Type Safety**: Caught bugs early, improved DX
3. **Modular Design**: Easy to debug and extend
4. **Docker**: Consistent dev/prod environment
5. **TON Connect**: Smooth wallet integration

### What We'd Do Differently

1. **Testing**: Add integration tests from day 1
2. **Monitoring**: Set up observability earlier
3. **Documentation**: Write docs alongside code
4. **Smart Contracts**: Consider earlier for trustlessness
5. **Error Handling**: More comprehensive from start

---

## 📞 Contact & Links

- **GitHub**: [@ssolis-ti](https://github.com/ssolis-ti)
- **Website**: [saiberaysen.cl](https://www.saiberaysen.cl)
- **Project Repository**: [github.com/ssolis-ti/TG-ADMC](https://github.com/ssolis-ti/TG-ADMC)
- **Demo Bot**: [@AdTGram_Bot](https://t.me/AdTGram_Bot)
- **Live App**: [https://tgadmc.mpbot.cl](https://tgadmc.mpbot.cl)
- **Documentation**: [docs/](docs/)

---

## 🙏 Acknowledgments

This project was built by [@ssolis-ti](https://github.com/ssolis-ti) ([saiberaysen.cl](https://www.saiberaysen.cl)) with:

- **Antigravity AI** (Google DeepMind) - Development assistant
- **TON Foundation** - Blockchain infrastructure
- **Telegram** - Bot API and WebApp SDK
- **FastAPI Community** - Excellent framework
- **Open Source Community** - Libraries and tools

---

**Built for the TON Ecosystem Hackathon**
**MVP Complete - Ready for Grant Phase**
