# FuelAI Agents - Setup Guide

## Prerequisites

1. **Docker Desktop** - for running Postgres, Redis, and MinIO
2. **Python 3.10+** - already installed ✓
3. **API Keys** - see below

## Step 1: Get API Keys

### Apify Token (Required for Instagram Scraping)

1. Go to [https://console.apify.com/sign-up](https://console.apify.com/sign-up)
2. Sign up for a free account (includes $5 free credits monthly)
3. Go to Settings → Integrations → API Tokens
4. Copy your API token

**Free tier includes:**
- $5 monthly credits (renews each month)
- ~1,000-5,000 Instagram posts can be scraped per month
- No credit card required

### OpenAI API Key (Required for AI Agents)

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### Instagram Session Cookie (Optional but Recommended)

This helps avoid rate limits when scraping Instagram:

1. Log into Instagram in your browser
2. Open Developer Tools (F12)
3. Go to Application → Cookies → https://www.instagram.com
4. Find the `sessionid` cookie and copy its value

## Step 2: Create .env File

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_PROJECT_ID=  # optional

# Apify Configuration
APIFY_TOKEN=your-apify-token-here

# Instagram Session Cookie (optional but recommended)
IG_SESSIONID=your-session-cookie-here

# Database Configuration (leave as-is for Docker)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asa
DB_USER=postgres
DB_PASSWORD=postgres
```

## Step 3: Start Docker Services

```bash
make up         # Start all services
make init       # Initialize database schema
```

## Step 4: Test the Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Test Apify integration
python3 test_apify.py

# If that works, test the full ingestion
python3 -m app.cli.discover_accounts
```

## Step 5: Run the Web Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Then visit:
- http://localhost:8000/discovery/ui - Discovery interface
- http://localhost:8000/docs - API documentation

## Common Issues

### "APIFY_TOKEN not set"
Make sure you created the `.env` file and it contains your Apify token.

### "no_items" error from Apify
- Your Apify credits may be exhausted
- Try adding IG_SESSIONID to your .env file
- Check Apify dashboard for quota

### Docker pull timeout
If `make up` fails with network timeout, try again or check your internet connection.

### Can't connect to database
Make sure Docker services are running: `docker compose ps`

## Testing the Full Workflow

1. **Discovery**: Visit http://localhost:8000/discovery/ui to find accounts
2. **Approve sources**: Click "Approve" on suggested accounts
3. **Ingest posts**: Run `python3 -m app.cli.ingest_instagram_sources`
4. **Generate content**: (API endpoint to be added)

## Cost Estimates

- **Apify**: $5/month free tier (1,000-5,000 posts)
- **OpenAI**: 
  - Discovery: ~$0.001 per batch of suggestions
  - Content generation: ~$0.005 per post package
  - Embeddings: ~$0.00001 per post

Total estimated cost for moderate use: $5-20/month

