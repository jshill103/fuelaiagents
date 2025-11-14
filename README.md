# ⚡ FuelAI Agents

AI-powered social media content automation system for FuelAI. Track competitor accounts, scrape content, and generate platform-native posts inspired by what's working in your market.

---

## 🚀 Quick Start

### 1. **Setup**
```bash
# Clone the repository
git clone https://github.com/jshill103/fuelaiagents.git
cd fuelaiagents

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
./setup.sh
```

### 2. **Start Services**
```bash
# Start Docker services (Postgres, Redis)
make up

# Initialize database
make init

# Start web server
./run_server.sh
```

### 3. **Open Dashboard**
Visit: **http://localhost:8000/dashboard**

---

## 📚 Documentation

Complete documentation is available in the [`/docs`](./docs) directory:

- **[Setup Guide](./docs/SETUP_GUIDE.md)** - Complete installation and configuration
- **[Dashboard Guide](./docs/DASHBOARD_GUIDE.md)** - Using the web interface
- **[Success Documentation](./docs/SUCCESS.md)** - Technical details and fixes
- **[Bug Fixes](./docs/BUG_FIXES.md)** - Comprehensive bug fix documentation

---

## ✨ Features

### ✅ Currently Working
- **Instagram Scraping** - Pull posts from any public Instagram account
- **Dashboard** - Web interface to manage tracked accounts
- **Discovery** - AI-powered account suggestions relevant to your audience
- **Source Management** - Add/remove accounts, view engagement metrics
- **Data Storage** - PostgreSQL with full post metadata and engagement
- **Scheduled Posts View** - See drafts and upcoming posts

### ⏳ Coming Soon
- **Semantic Search** - Find relevant inspiration posts by topic
- **Content Generation** - AI-generated platform-native drafts
- **Auto-Publishing** - Schedule and publish to social platforms
- **Facebook/LinkedIn** - Scraping support for additional platforms

---

## 🎯 Use Cases

1. **Track Competitors** - Monitor what competitors are posting
2. **Find Inspiration** - Scrape successful posts from your industry
3. **Analyze Engagement** - See what content resonates
4. **Generate Content** - AI creates posts inspired by top performers
5. **Schedule Posts** - Plan and auto-publish content

---

## 🛠️ Technology Stack

- **Backend:** FastAPI, Python 3.10+
- **Database:** PostgreSQL with pgvector (for embeddings)
- **Cache:** Redis
- **Storage:** MinIO (S3-compatible)
- **AI:** OpenAI (GPT-4o-mini, text-embedding-3-small)
- **Scraping:** Apify Instagram scraper
- **UI:** HTML/CSS/JavaScript (no framework)

---

## 📁 Project Structure

```
fuelaiagents/
├── app/                    # Application code
│   ├── agents/            # AI agents (discovery, drafting, semantic)
│   ├── routes/            # FastAPI routes
│   ├── services/          # Business logic
│   ├── db/                # Database utilities
│   └── cli/               # Command-line tools
├── docs/                   # Documentation
│   ├── SETUP_GUIDE.md
│   ├── DASHBOARD_GUIDE.md
│   ├── SUCCESS.md
│   └── BUG_FIXES.md
├── scripts/               # Test & helper scripts
│   ├── test_apify.py
│   ├── test_full_ingestion.py
│   └── ...
├── venv/                  # Virtual environment
├── docker-compose.yml     # Docker services
├── requirements.txt       # Python dependencies
├── Makefile              # Common commands
├── setup.sh              # Setup wizard
└── run_server.sh         # Server launcher
```

---

## 🌐 Dashboard URLs

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | http://localhost:8000/dashboard | Main control panel |
| **Discovery** | http://localhost:8000/discovery/ui | AI account suggestions |
| **Scheduled** | http://localhost:8000/dashboard/scheduled | View drafts & scheduled posts |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

---

## 🧪 Testing

Test scripts are available in the [`/scripts`](./scripts) directory:

```bash
# Test Apify integration
python3 scripts/test_apify.py

# Test full end-to-end workflow
python3 scripts/test_full_ingestion.py
```

See [scripts/README.md](./scripts/README.md) for more details.

---

## 🔧 Common Commands

```bash
# Start Docker services
make up

# Stop Docker services
make down

# Initialize database
make init

# View Docker logs
make logs

# Open database shell
make dbshell

# Start web server
./run_server.sh
```

---

## 📊 Current Status

- ✅ **Instagram scraping working** - Successfully pulling real data
- ✅ **15+ posts ingested** - NASA, Nike, Salesforce accounts
- ✅ **Dashboard operational** - Full web interface
- ✅ **Discovery working** - AI-powered suggestions
- ✅ **Database stable** - No connection leaks, proper error handling
- ✅ **All endpoints tested** - 200 OK responses

---

## 💰 Cost Estimates

- **Apify:** $5/month free tier (1,000-5,000 posts)
- **OpenAI:** 
  - Discovery: ~$0.001 per batch
  - Content generation: ~$0.005 per post
  - Embeddings: ~$0.00001 per post

**Estimated monthly cost for moderate use:** $5-20

---

## 🤝 Contributing

This is a private project. For questions or issues, contact the repository owner.

---

## 📝 License

Proprietary - All rights reserved.

---

## 🔗 Links

- **GitHub:** https://github.com/jshill103/fuelaiagents
- **Forked from:** https://github.com/bhadfieldfuel/fuelaiagents

---

**Built with ❤️ for FuelAI**

