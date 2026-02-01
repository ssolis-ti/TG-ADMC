# TG-ADMC: Telegram Ads Marketplace Core

> **Decentralized ad marketplace for Telegram channels, powered by TON blockchain**

[![Status](https://img.shields.io/badge/status-MVP%20Complete-success)](https://github.com)
[![TON](https://img.shields.io/badge/TON-Testnet-blue)](https://testnet.toncenter.com)
[![Python](https://img.shields.io/badge/python-3.11.14-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🎯 Overview

TG-ADMC is a **trust-minimized marketplace** that connects Telegram channel owners with advertisers. It uses TON blockchain for payments and escrow, eliminating the need for manual coordination and building trust through code.

### Key Features

- ✅ **Verified Channels**: Bot-verified ownership before listing
- 💰 **Escrow Payments**: Funds locked until ad is published
- 🤖 **Auto-Publishing**: Bot posts ads automatically on approval
- 🔐 **Blockchain Proof**: Every transaction recorded on TON
- ⚡ **Instant Payouts**: Owners receive payment immediately after posting

### Current Status

| Metric              | Value                          |
| ------------------- | ------------------------------ |
| **Completed Deals** | 7                              |
| **Success Rate**    | 100%                           |
| **Total Volume**    | 0.7 TON (testnet)              |
| **Uptime**          | 11+ hours continuous           |
| **Deployment**      | Production (Cloudflare Tunnel) |

---

## 🛠️ Technology Stack

### Backend

| Technology      | Version  | Purpose                 |
| --------------- | -------- | ----------------------- |
| **Python**      | 3.11.14  | Core language           |
| **FastAPI**     | ≥0.109.0 | Async web framework     |
| **Uvicorn**     | ≥0.27.0  | ASGI server             |
| **aiogram**     | ≥3.17.0  | Telegram Bot API        |
| **PostgreSQL**  | 15.15    | Database                |
| **SQLModel**    | ≥0.0.14  | ORM with Pydantic       |
| **asyncpg**     | ≥0.29.0  | Async PostgreSQL driver |
| **APScheduler** | ≥3.10.4  | Task scheduling         |
| **tonsdk**      | ≥1.0.14  | TON blockchain SDK      |
| **Pydantic**    | ≥2.5.3   | Data validation         |
| **Loguru**      | ≥0.7.2   | Logging                 |

### Frontend

| Technology              | Version | Purpose              |
| ----------------------- | ------- | -------------------- |
| **Vanilla JavaScript**  | ES6+    | UI logic             |
| **TON Connect UI**      | Latest  | Wallet integration   |
| **Telegram WebApp SDK** | Latest  | Mini App integration |

### Infrastructure

| Technology            | Version | Purpose                       |
| --------------------- | ------- | ----------------------------- |
| **Docker**            | Latest  | Containerization              |
| **Docker Compose**    | 3.8     | Multi-container orchestration |
| **Cloudflare Tunnel** | Latest  | Secure public access          |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: ≥20.10.0
- **Docker Compose**: ≥2.0.0
- **Git**: Latest
- **Telegram Account**: For bot creation
- **TON Wallet**: Tonkeeper (testnet mode)

### System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **RAM**: ≥2GB
- **Disk**: ≥5GB free space
- **Network**: Stable internet connection

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/TG-ADMC.git
cd TG-ADMC
```

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the **Bot Token** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Send `/mybots` → Select your bot → **Bot Settings** → **Inline Mode** → Enable
5. Send `/setmenubutton` → Select your bot → Send URL: `https://yourdomain.com/app`

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Database (use default for Docker)
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/tgadmc

# TON Blockchain
TON_WALLET_ADDRESS=your_escrow_wallet_address
WALLET_MNEMONIC="your 24 word mnemonic phrase here"

# Deployment
WEBHOOK_URL=https://yourdomain.com
TUNNEL_TOKEN=your_cloudflare_tunnel_token
```

**⚠️ Security Note**: Never commit `.env` to version control. The `.gitignore` file already excludes it.

### 4. Deploy Escrow Wallet (TON Testnet)

1. Install **Tonkeeper** on your phone
2. Switch to **Testnet** mode:
   - Settings → Developer → Enable Testnet
3. Create a new wallet or import existing one
4. Get testnet TON from [faucet](https://t.me/testgiver_ton_bot)
5. **Send 0.01 TON** to any address to deploy the wallet contract
6. Copy your wallet address (format: `0:abc123...`)
7. Export your **24-word mnemonic** (Settings → Backup)
8. Add both to `.env` file

### 5. Set Up Cloudflare Tunnel (Production)

1. Create account at [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Navigate to **Access** → **Tunnels** → **Create a tunnel**
3. Name it (e.g., `tg-admc-tunnel`)
4. Copy the **Tunnel Token**
5. Add to `.env` as `TUNNEL_TOKEN`
6. Configure public hostname:
   - Subdomain: `tgadmc` (or your choice)
   - Domain: Your Cloudflare domain
   - Service: `http://bot:8000`

### 6. Build and Run

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f bot

# Verify services are running
docker-compose ps
```

Expected output:

```
NAME                  STATUS              PORTS
tg-admc-bot           Up 10 seconds       0.0.0.0:7777->8000/tcp
tg-admc-db            Up 10 seconds       5432/tcp
tg-admc-cloudflared-1 Up 10 seconds
```

### 7. Initialize Database

The database schema is created automatically on first run. To verify:

```bash
docker exec tg-admc-db psql -U user -d tgadmc -c "\dt"
```

Expected tables:

- `user`
- `channel`
- `deal`

### 8. Test the Bot

1. Open Telegram
2. Search for your bot (`@YourBotName`)
3. Send `/start`
4. Click **🚀 Open Marketplace**
5. Connect your TON wallet
6. You're ready! 🎉

---

## 📖 Usage Guide

### For Channel Owners

1. **Register Channel**:
   - Add bot as **Administrator** to your channel
   - Open marketplace → "My Channels" → "Register Channel"
   - Enter channel username (e.g., `@mychannel`)
   - Set price per post (e.g., `0.1` TON)

2. **Manage Deals**:
   - Receive notifications for new ad requests
   - Review ad brief in "Deals" tab
   - Accept or reject offers
   - Bot auto-publishes on acceptance
   - Receive payment instantly

### For Advertisers

1. **Browse Channels**:
   - Open marketplace → "Channels" tab
   - View verified channels with prices
   - Check subscriber counts and engagement

2. **Create Ad**:
   - Click "Buy Ad" on desired channel
   - Write ad brief (text, links, media)
   - Confirm payment in Tonkeeper
   - Wait for owner approval

3. **Track Progress**:
   - View deal status in "Deals" tab
   - Receive notification when published
   - Get proof link to published message

---

## 🔧 Development

### Project Structure

```
TG-ADMC/
├── src/
│   ├── bot/                 # Telegram bot handlers
│   │   ├── handlers/
│   │   │   ├── common.py    # /start command
│   │   │   └── verification.py # Channel registration and smart link logic
│   │   └── (no main.py, see src/main.py)
│   ├── api/                 # FastAPI routes
│   │   └── routes.py        # API endpoints
│   ├── db/                  # Database layer
│   │   ├── models.py        # SQLModel schemas
│   │   └── database.py      # Session management
│   ├── services/            # Business logic
│   │   ├── identity.py      # User management
│   │   ├── escrow.py        # Deal state machine
│   │   └── ton.py           # Blockchain integration
│   ├── workers/             # Background tasks
│   │   └── scheduler.py     # Auto-publishing
│   ├── core/                # Configuration
│   │   └── config.py        # Settings
│   ├── static/              # Frontend
│   │   ├── js/modules/      # Modular JS
│   │   │   ├── main.js
│   │   │   ├── wallet.js
│   │   │   ├── api.js
│   │   │   └── controllers.js
│   │   ├── css/
│   │   └── index.html
│   └── main.py              # FastAPI app
├── docs/                    # Documentation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Running Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up local database
export DATABASE_URL=sqlite+aiosqlite:///./database.db

# Run FastAPI server
uvicorn src.main:app --reload --port 8000

# In another terminal, run bot
# In another terminal, run bot (via Uvicorn as it's part of the main app)
# Note: The bot runs inside the FastAPI process in this MVP
uvicorn src.main:app --reload --port 8000
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 🐳 Docker Commands

### Useful Commands

```bash
# View logs
docker-compose logs -f bot          # Bot logs
docker-compose logs -f db           # Database logs

# Restart services
docker-compose restart bot          # Restart bot only
docker-compose restart              # Restart all

# Stop services
docker-compose down                 # Stop and remove containers
docker-compose down -v              # Also remove volumes (⚠️ deletes data)

# Rebuild after code changes
docker-compose up -d --build --force-recreate

# Execute commands in containers
docker exec -it tg-admc-bot bash    # Shell in bot container
docker exec tg-admc-db psql -U user -d tgadmc  # PostgreSQL CLI

# View resource usage
docker stats
```

### Database Management

```bash
# Backup database
docker exec tg-admc-db pg_dump -U user tgadmc > backup.sql

# Restore database
docker exec -i tg-admc-db psql -U user tgadmc < backup.sql

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
```

---

## 🔒 Security Considerations

### MVP (Current)

- ✅ Testnet only (no real funds at risk)
- ✅ Mnemonic in `.env` (acceptable for testing)
- ✅ HTTPS via Cloudflare Tunnel
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)

### Production Roadmap

- [ ] Hardware Security Module (HSM) for keys
- [ ] Multi-signature escrow wallet
- [ ] Rate limiting (100 req/min per user)
- [ ] CSRF protection
- [ ] Security audit by third party
- [ ] Encrypted secrets management (Vault)

---

## 📊 Monitoring

### Health Check

```bash
# Check if services are running
curl https://yourdomain.com/health

# Expected response
{"status": "healthy", "database": "connected"}
```

### Logs

```bash
# Real-time logs
docker-compose logs -f --tail=100

# Search logs
docker-compose logs | grep ERROR

# Export logs
docker-compose logs > logs.txt
```

---

## 🐛 Troubleshooting

### Bot Not Responding

```bash
# Check bot logs
docker-compose logs bot | tail -50

# Verify bot token
docker exec tg-admc-bot env | grep BOT_TOKEN

# Restart bot
docker-compose restart bot
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps db

# Check connection
docker exec tg-admc-bot python -c "from src.db.database import engine; print('OK')"

# Reset database
docker-compose down -v && docker-compose up -d
```

### Payment Not Working

```bash
# Verify wallet mnemonic is set
docker exec tg-admc-bot env | grep WALLET_MNEMONIC

# Check TONSDK import
docker exec tg-admc-bot python -c "from src.services.ton import TONSDK_AVAILABLE; print(TONSDK_AVAILABLE)"

# View payout logs
docker-compose logs bot | grep -i payout
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
docker-compose logs cloudflared

# Verify tunnel token
docker exec tg-admc-cloudflared-1 env | grep TUNNEL_TOKEN

# Restart tunnel
docker-compose restart cloudflared
```

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Master Index](docs/00_master_index.md)** - Navigation guide
- **[Philosophy & Architecture](docs/01_philosophy_architecture.md)** - Design principles
- **[Backend Mechanics](docs/02_backend_mechanics.md)** - API and database
- **[Frontend Dynamics](docs/03_frontend_dynamics.md)** - UI and UX
- **[Web3 Strategy](docs/04_web3_strategy.md)** - TON integration
- **[Security & Risk](docs/05_security_risk.md)** - Security analysis
- **[Hackathon Compliance](docs/07_hackathon_compliance.md)** - Contest requirements
- **[Role Flows](docs/08_role_flows.md)** - User journeys

---

## 🤝 Contributing

This project is part of a hackathon submission. Contributions are welcome after the contest period.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use `black` formatter
- **JavaScript**: ES6+, use `prettier` formatter
- **Commits**: Conventional Commits format

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

- **GitHub**: [@ssolis-ti](https://github.com/ssolis-ti)
- **Website**: [saiberaysen.cl](https://www.saiberaysen.cl)
- **Project Repository**: [github.com/ssolis-ti/TG-ADMC](https://github.com/ssolis-ti/TG-ADMC)
- **Demo Bot**: [@AdTGram_Bot](https://t.me/AdTGram_Bot)
- **Live Demo**: [https://tgadmc.mpbot.cl](https://tgadmc.mpbot.cl)

---

## 🙏 Acknowledgments

- **Development**: [@ssolis-ti](https://github.com/ssolis-ti) | [saiberaysen.cl](https://www.saiberaysen.cl)
- **AI Assistant**: Antigravity (Google DeepMind)
- **TON Foundation** - Blockchain infrastructure
- **Telegram** - Bot API and WebApp SDK
- **FastAPI** - Async web framework
- **aiogram** - Telegram bot library

## 🎯 Roadmap

### Phase 1: MVP (✅ Complete)

- [x] Core marketplace functionality
- [x] TON testnet integration
- [x] Auto-publishing
- [x] Escrow and payouts

### Phase 2: Production Hardening (Grant Phase)

- [ ] Security audit
- [ ] Mainnet deployment
- [ ] Dispute resolution
- [ ] Analytics dashboard

### Phase 3: Scale

- [ ] Multi-language support
- [ ] Smart contract migration
- [ ] Mobile app
- [ ] API for third parties

---

**Built with ❤️ for the TON Ecosystem by [@ssolis-ti](https://github.com/ssolis-ti) | [saiberaysen.cl](https://www.saiberaysen.cl)**
