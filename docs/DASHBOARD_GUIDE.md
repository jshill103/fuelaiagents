# 🎯 FuelAI Agents Dashboard Guide

## 🚀 Dashboard is LIVE!

The web application is now running at: **http://localhost:8000**

---

## 📱 Available Pages

### 1. **Main Dashboard** - http://localhost:8000/dashboard

**Features:**
- ✅ View all tracked accounts (sources)
- ✅ See post counts, likes, comments for each account
- ✅ See when accounts were last crawled
- ✅ **Add new accounts** manually
- ✅ **Delete accounts** (removes account and all posts)
- ✅ **Fetch posts** on-demand for any account
- ✅ Overview stats (total sources, posts, drafts, scheduled)

**What You Can Do:**
- Click **"Discover New Accounts"** to find AI-suggested accounts
- Click **"+ Add Manual"** to manually add an Instagram/Facebook/LinkedIn account
- Click **"Fetch"** next to any account to pull their latest posts
- Click **"Delete"** to remove an account
- View engagement metrics (likes, comments) for each account

---

### 2. **Discovery** - http://localhost:8000/discovery/ui

**Features:**
- ✅ AI-powered account suggestions
- ✅ Shows reasoning for why each account is relevant
- ✅ Fit score (0-100) for each suggestion
- ✅ Voice notes (what to learn from their content style)
- ✅ One-click approve to add accounts

**How It Works:**
1. Uses OpenAI GPT-4o-mini to analyze your brand
2. Suggests accounts your target audience follows
3. Filters by sales/SDR/outbound focus
4. Shows competitors, inspiration accounts, and meme accounts
5. Click "Approve" to add them to your tracked sources

---

### 3. **Scheduled Posts** - http://localhost:8000/dashboard/scheduled

**Features:**
- ✅ View all draft posts
- ✅ See scheduled posts with dates/times
- ✅ View posts by platform (Instagram, Facebook, LinkedIn)
- ✅ See post type (educational, meme, sales, etc.)
- ✅ Preview captions and hashtags
- ✅ Delete drafts

**Coming Soon:**
- Schedule posts for specific times
- Edit drafts
- Auto-publish to social platforms

---

### 4. **API Documentation** - http://localhost:8000/docs

Interactive API documentation (Swagger UI) with all endpoints.

---

## 🎨 Dashboard Features in Detail

### **Current Sources Table**

| Column | Description |
|--------|-------------|
| **Platform** | Instagram, Facebook, or LinkedIn |
| **Handle** | Account username (clickable link) |
| **Type** | Competitor or Inspiration |
| **Posts** | Number of posts ingested |
| **Total Likes** | Sum of all likes across posts |
| **Total Comments** | Sum of all comments |
| **Latest Post** | When their most recent post was published |
| **Last Crawl** | When we last fetched from this account |
| **Schedule** | How often we fetch (daily, weekly, etc.) |
| **Actions** | Fetch now or Delete |

### **Stats Overview**

- **Total Sources**: How many accounts you're tracking
- **Posts Ingested**: Total posts in database
- **Pending Drafts**: Drafts waiting for review
- **Scheduled Posts**: Posts scheduled for future publishing

---

## 🔥 Quick Actions

### **Add a New Account**

1. Go to http://localhost:8000/dashboard
2. Click **"+ Add Manual"**
3. Select platform (Instagram/Facebook/LinkedIn)
4. Enter handle (without @)
5. Check "Mark as competitor" if applicable
6. Click "Add Source"

### **Fetch Posts from an Account**

1. Find the account in the dashboard table
2. Click the green **"Fetch"** button
3. Wait 1-2 minutes (it will fetch up to 20 posts)
4. Page will reload with updated stats

### **Delete an Account**

1. Click the red **"Delete"** button next to any account
2. Confirm the deletion
3. This removes the account AND all its posts from the database

### **Discover New Accounts with AI**

1. Go to http://localhost:8000/discovery/ui
2. View AI-suggested accounts relevant to your audience
3. Read the **Reason** (why they're relevant)
4. Read the **Voice to borrow** (what to learn from them)
5. Click **"Approve"** to add them to your sources
6. Return to dashboard to see them

---

## 🎯 Current Data

You currently have:
- **3 sources**: NASA, Nike, Salesforce
- **15 posts**: 5 from each account
- **Real engagement data**: Likes, comments from Instagram

---

## 🚀 Workflow

### **1. Discover Accounts**
- Use Discovery page to find relevant accounts
- AI suggests based on your target audience
- Approve the ones you like

### **2. Fetch Content**
- Dashboard shows all your sources
- Click "Fetch" to pull their latest posts
- Posts are automatically deduplicated

### **3. Generate Content** (Coming Soon)
- AI will analyze your ingested posts
- Create semantic embeddings
- Generate platform-native drafts inspired by what's working

### **4. Schedule & Publish** (Coming Soon)
- Review drafts in Scheduled page
- Set publish dates/times
- Auto-publish to social platforms

---

## 🛠️ Technical Details

### **What's Included**

| Feature | Status |
|---------|--------|
| Instagram scraping | ✅ Working |
| Dashboard UI | ✅ Working |
| Add/Remove sources | ✅ Working |
| View engagement metrics | ✅ Working |
| On-demand fetching | ✅ Working |
| Discovery (AI suggestions) | ✅ Working |
| Scheduled posts view | ✅ Working |
| Semantic search | ⏳ TODO |
| Content generation | ⏳ TODO |
| Auto-publishing | ⏳ TODO |

---

## 🌐 URLs Summary

| Page | URL | Purpose |
|------|-----|---------|
| **Home** | http://localhost:8000/ | Redirects to dashboard |
| **Dashboard** | http://localhost:8000/dashboard | Main control panel |
| **Discovery** | http://localhost:8000/discovery/ui | AI account suggestions |
| **Scheduled** | http://localhost:8000/dashboard/scheduled | View drafts & scheduled posts |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health** | http://localhost:8000/health | Server health check |

---

## 🎨 Design

- Modern, clean UI with FuelAI brand colors
- Responsive tables and stats
- Real-time actions (fetch, delete)
- Modal forms for adding accounts
- Color-coded badges for platforms and types

---

## 🐛 Troubleshooting

### Server not responding?
```bash
# Check if running
ps aux | grep uvicorn

# View logs
cd /Users/jaredshillingburg/Jared-Repos/fb_scraper/fuelaiagents
cat server.log
```

### Need to restart?
```bash
cd /Users/jaredshillingburg/Jared-Repos/fb_scraper/fuelaiagents
pkill -f uvicorn
./run_server.sh
```

### Database not working?
```bash
cd /Users/jaredshillingburg/Jared-Repos/fb_scraper/fuelaiagents
docker compose ps    # Check if postgres is running
docker compose up -d postgres redis
```

---

## 🎯 Next Steps

1. ✅ Dashboard is live and working
2. Try adding more Instagram accounts
3. Fetch posts to build your content library
4. Use Discovery to find competitor accounts
5. Wait for content generation features (coming next!)

---

**Enjoy your new dashboard!** 🚀

