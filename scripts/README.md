# 🧪 Test & Helper Scripts

Collection of test and utility scripts for development and testing.

## 🔬 Test Scripts

### `test_apify.py`
Basic Apify Instagram scraper test.
```bash
cd /Users/jaredshillingburg/Jared-Repos/fb_scraper/fuelaiagents
source venv/bin/activate
python3 scripts/test_apify.py
```

### `test_apify_advanced.py`
Advanced Apify testing with multiple strategies and actors.
```bash
python3 scripts/test_apify_advanced.py
```

### `test_scraper_service.py`
Tests the fixed Instagram scraper service layer with real accounts.
```bash
python3 scripts/test_scraper_service.py
```

### `test_full_ingestion.py`
End-to-end workflow test: adds brands, sources, fetches and ingests posts.
```bash
python3 scripts/test_full_ingestion.py
```

## 🛠️ Helper Scripts

### `quick_test.sh`
Quick test without .env file (pass credentials as arguments).
```bash
./scripts/quick_test.sh YOUR_APIFY_TOKEN [YOUR_IG_SESSIONID]
```

---

## 📝 Notes

- All scripts require the virtual environment to be activated
- Most scripts need `.env` file with credentials (see `/docs/SETUP_GUIDE.md`)
- Test scripts use real API calls and may consume credits

## 🚀 Common Usage

**Test if Apify is working:**
```bash
source venv/bin/activate
python3 scripts/test_apify.py
```

**Test full system:**
```bash
source venv/bin/activate
python3 scripts/test_full_ingestion.py
```

---

**For more information, see [/docs/SETUP_GUIDE.md](../docs/SETUP_GUIDE.md)**

