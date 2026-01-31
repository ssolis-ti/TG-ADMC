# TG-ADMC: The Master Documentation Library

> _Precision. Clarity. Intent._

## Introduction

Welcome to the definitive technical library for the **Telegram Ads Marketplace Core (TG-ADMC)**. This documentation is structured into **Eight Volumes**, designed to guide developers, architects, and stakeholders from the philosophical "Why" to the granular "How" of the system.

**Current Status**: ✅ **MVP Complete** - 7 deals executed end-to-end on TON testnet.

---

## The Library Index

### [INDEX 0: THE CODEX (The Driver)](./000_the_codex.md)

**⚠️ MANDATORY READING**

- **The Vision**: The "Winning MVP" Mentality.
- **The Constraints**: Leveraging limitations as strengths.
- **The Goal**: Frictionless value transfer.

---

### [Volume I: The Genesis & Philosophy](./01_philosophy_architecture.md)

**"The Architectural Soul"**

- **Purpose**: Why does this project exist?
- **Intent**: The shift from Web2 chaos to Web3 order.
- **Blueprint**: The High-Level Architecture (Containerization, Modular Monolith).
- **Core Stack**: Rationale behind FastAPI, PostgreSQL, and Vanilla JS.
- **Philosophy**: Code as manifestation of thought.

**Status**: ✅ Architecture validated through production deployment.

---

### [Volume II: The Core Mechanisms (Backend)](./02_backend_mechanics.md)

**"The Engine Room"**

- **Tactical Routing**: How `routes.py` manages traffic.
- **Data Persistence**: The SQLAlchemy/SQLModel Schema logic.
- **The Escrow Machine**: Deep dive into `escrow.py`—the heart of the Marketplace.
- **Security**: Authentication flows and the "Chain of Trust".
- **Automation**: Scheduler-driven publishing and payouts.

**Status**: ✅ All core mechanisms operational. 100% success rate on 7 deals.

---

### [Volume III: The Interface Dynamics (Frontend)](./03_frontend_dynamics.md)

**"The User Interaction Layer"**

- **Modular Design**: The "Lego" architecture of `src/static/js/modules`.
- **Telegram Integration**: Leveraging `initData` and `MainButton`.
- **Reactivity**: How the UI updates without page reloads (DOM manipulation tactics).
- **TON Connect**: Wallet integration with Tonkeeper.
- **UX Philosophy**: Instant feedback, clear state transitions.

**Status**: ✅ Professional UI deployed. Cache-busting strategy implemented.

---

### [Volume IV: The Web3 Horizon](./04_web3_strategy.md)

**"The Bridge to the Future"**

- **TON Integration**: The "Dual-Net" Strategy (Testnet ✅ → Mainnet 🚧).
- **Wallet Connection**: The logic behind `wallet.js` and TON Connect UI.
- **Escrow Flow**: Python-based escrow with TONSDK.
- **Smart Contract Roadmap**: Migration path for grant phase.
- **Transaction Proof**: On-chain verification strategy.

**Status**: ✅ Testnet fully operational. 0.7 TON processed successfully.

---

### [Volume V: The Security & Risk Codex](./05_security_risk.md)

**"The Shield & Sword"**

- **SWOT Analysis**: Deep strategic view of the system's viability.
- **Anti-Abuse**: Defense against Replay Attacks, Sybil swarms, and Content switching.
- **QA Guidelines**: Integration vs. Stress vs. Red Team protocols.
- **MVP Security**: Testnet-appropriate measures.
- **Production Roadmap**: HSM, multi-sig, audit trail.

**Status**: ✅ MVP security implemented. Production roadmap defined.

---

### [Volume VI: Audit Report](./06_audit_report.md)

**"The Validation Chronicle"**

- **Bug Discovery**: Critical issues found and resolved.
- **Performance Metrics**: Response times, uptime, success rates.
- **Code Quality**: Linting, type safety, async patterns.
- **Integration Testing**: End-to-end flow validation.

**Status**: ✅ All critical bugs resolved. System stable for 11+ hours.

---

### [Volume VII: Hackathon Compliance](./07_hackathon_compliance.md)

**"The Contest Alignment"**

- **Scope Coverage**: All core requirements implemented.
- **MVP vs Production**: Clear delineation of what's done vs. planned.
- **Demo Readiness**: Step-by-step flow documentation.
- **Grant Roadmap**: Phase-by-phase production plan.

**Status**: ✅ 100% core scope complete. Production roadmap ready.

---

### [Volume VIII: Role Flows](./08_role_flows.md)

**"The User Journey Maps"**

- **Advertiser Flow**: Browse → Pay → Confirm → Proof.
- **Owner Flow**: Register → Accept → Receive → Verify.
- **Bot Automation**: Scheduler logic and state transitions.
- **Error Handling**: User feedback and recovery paths.

**Status**: ✅ Both flows validated with real users.

---

## Quick Navigation

### For Judges/Evaluators

1. Start with [The Codex](./000_the_codex.md) - Understand the vision
2. Review [Hackathon Compliance](./07_hackathon_compliance.md) - See scope coverage
3. Read [Philosophy](./01_philosophy_architecture.md) - Grasp the architecture
4. Check [Audit Report](./06_audit_report.md) - Validate quality

### For Developers

1. [Backend Mechanics](./02_backend_mechanics.md) - API and database
2. [Frontend Dynamics](./03_frontend_dynamics.md) - UI and UX
3. [Web3 Strategy](./04_web3_strategy.md) - Blockchain integration
4. [Security Codex](./05_security_risk.md) - Best practices

### For Product Owners

1. [Role Flows](./08_role_flows.md) - User journeys
2. [Philosophy](./01_philosophy_architecture.md) - Product vision
3. [Hackathon Compliance](./07_hackathon_compliance.md) - Roadmap

---

## Project Metrics (Current)

| Metric              | Value                |
| ------------------- | -------------------- |
| **Completed Deals** | 7                    |
| **Success Rate**    | 100%                 |
| **Uptime**          | 11+ hours continuous |
| **Total Volume**    | 0.7 TON (testnet)    |
| **Response Time**   | <500ms average       |
| **Code Coverage**   | Core flows validated |

---

## Philosophy Summary

> **"We build systems that think like humans but execute like machines."**

### Core Principles

1. **Precision over Cleverness**: Clear code beats clever code.
2. **Intent over Implementation**: Architecture reflects business logic.
3. **Async by Default**: Never block the event loop.
4. **Type Safety**: Pydantic models are contracts.
5. **Modular Monolith**: Ready to scale, optimized for MVP.

---

_Created by [@ssolis-ti](https://github.com/ssolis-ti) | [saiberaysen.cl](https://www.saiberaysen.cl)_
_Documentation generated with Antigravity (Google DeepMind)_
_Last Updated: 2026-01-31 - MVP Complete & Ready for Submission_
