# TG-ADMC: Architecture & Developer Map

> **Version**: 1.0.0 (MVP)
> **Stack**: FastAPI (Python), Vanilla JS (ES6 Modules), Aiogram, SQLModel, Docker.

## 1. Project Overview

TG-ADMC is a **Telegram Mini App Marketplace** connecting Channel Owners and Advertisers.
It uses a **Hybrid Architecture**:

- **Bot**: Acts as the entry point and notifier.
- **Web App (SPA)**: The main interface for Marketplace, Deals, and Dashboard.
- **API**: RESTful backend managing state and business logic.

---

## 2. Directory Structure & Responsibilities

```
src/
├── api/                    # REST API Endpoints
│   └── routes.py           # /api/* endpoints (Deals, Channels, Auth)
├── bot/                    # Telegram Bot Helpers
│   ├── handlers/
│   │   ├── common.py       # Start, Help & Base Commands
│   │   └── verification.py # Channel Registration Logic
│   └── loader.py           # Bot Instance Simulation
├── db/                     # Database Layer
│   ├── database.py         # Async Session & Init
│   └── models.py           # SQLModel Entities (User, Channel, Deal)
├── services/               # [CORE] Business Logic
│   ├── escrow.py           # Deal Lifecycle (Create -> Pay -> Lock)
│   ├── identity.py         # User/Channel Auth & Management
│   └── marketplace.py      # Search & Listing Logic
├── utils/                  # Shared Utilities
│   └── auth.py             # JWT & Telegram Hash Validation
├── workers/                # Background Tasks
│   └── scheduler.py        # Periodic Jobs (e.g. Stats Sync)
├── static/                 # Frontend Assets
│   ├── css/                # Styles
│   ├── js/
│   │   └── modules/        # [LEGO ARCHITECTURE] ES6 Modules
│   └── index.html          # SPA Entry Point
└── main.py                 # FastAPI Application Factory
```

---

## 3. Modular Frontend Architecture ("Lego Blocks")

The frontend was refactored from a monolith to strict ES6 Modules to ensure separation of concerns.

| Module               | Responsibility                                                                                             | Dependencies                 |
| :------------------- | :--------------------------------------------------------------------------------------------------------- | :--------------------------- |
| **`main.js`**        | **Orchestrator**. Initializes app, routes views, and binds global events.                                  | All Modules                  |
| **`auth.js`**        | **Identity**. Handles User ID retrieval (URL Param vs Telegram InitData) and Persistence (`localStorage`). | `config.js`                  |
| **`api.js`**         | **Data Layer**. Pure wrappers for `fetch()`. No UI logic.                                                  | `config.js`, `auth.js`       |
| **`ui.js`**          | **View Layer**. Renders HTML strings (Cards, Buttons, Modals). No state logic.                             | `auth.js` (for formatting)   |
| **`controllers.js`** | **Logic**. The "Brain". Calls `api.js`, processes data, and passes it to `ui.js`.                          | `api.js`, `ui.js`, `auth.js` |
| **`config.js`**      | **Constants**. Enums (ROLES), DOM Selectors, API Base URL.                                                 | None                         |

### Key Frontend Flows

1.  **Boot**: `main.js` waits for DOM -> calls `initTabs`.
2.  **Auth**: `auth.js` checks `?user_id=X` -> Fallback to `Telegram.initData` -> Fallback to `localStorage`.
3.  **Role Switch**: `main.js` toggles DOM visibility between Dashboard and Tabs.
4.  **Edit Price**: `controllers.js` prompts user -> calls `api.updateChannelPrice` -> refreshes View.

---

## 4. Backend Services (Python)

The backend is service-oriented to keep `routes.py` clean.

### `IdentityService`

- **Role**: Manages Users and Channels.
- **Critical Functions**:
  - `get_or_create_user(id)`: Concurrency-safe creation (Handles Race Conditions).
  - `register_channel(owner_id, ...)`: Links channel to owner.
  - `set_channel_price(channel_id, price)`: Updates asking price.

### `EscrowService`

- **Role**: State Machine for Deals.
- **States**:
  - `CREATED`: Advertiser sent offer.
  - `ACCEPTED`: Owner accepted.
  - `DRAFTED`: Owner submitted content.
  - `APPROVED`: Advertiser approved content.
  - `LOCKED`: Payment verified (TON Connect).

---

## 5. Data Models (ER Diagram)

- **User**: Telegram ID, Username.
- **Channel**: Belongs to `User` (Owner). Attributes: `price_post`, `subscribers`, `verified`.
- **Deal**: Links `Advertiser (User)` <-> `Channel`. Tracks `status`, `amount`, `tx_hash`.

## 6. Development & Deployment

- **Docker**: Managed via `docker-compose.yml`.
- **Tunnel**: Uses Cloudflare Tunnel for HTTPS access in Telegram Webview.
- **Poll**: `run_polling.py` for Bot updates (Dev mode).

---

## 7. Background System

The system runs autonomous agents to ensure data freshness.

### `Scheduler (src/workers/scheduler.py)`

- **Role**: Periodic Background Worker (APScheduler).
- **Jobs**:
  - `sync_channel_stats`: Updates subscriber counts every 6 hours.
  - `check_expired_deals`: Unlocks funds if deal stalls > 24h.

### `Utils (src/utils/)`

- **`auth.py`**:
  - `validate_telegram_data()`: Cryptographic check of `initData` from WebApp.
  - `create_access_token()`: Generates Session JWTs.

---

## 8. Integration Points (For AI/Devs)

- **Adding a new UI Feature**:

1.  Add Render function in `ui.js`.
2.  Add API wrapper in `api.js`.
3.  Wire them in `controllers.js`.

- **Changing State Logic**: Modify `EscrowService` methods.
- **Database Schema**: Edit `models.py` and run migration (auto-created in MVP).
