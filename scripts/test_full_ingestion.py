#!/usr/bin/env python3
"""
Full end-to-end test: Add brand, add sources, ingest posts.
"""

import os
import sys
import psycopg2
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required credentials are set
if not os.environ.get("APIFY_TOKEN"):
    print("❌ ERROR: APIFY_TOKEN not set in environment or .env file")
    print("Please create a .env file with your API keys. See SETUP_GUIDE.md")
    sys.exit(1)

from app.services.instagram_scraper import fetch_instagram_posts
from app.services.ingestion_service import upsert_posts

def get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )

def setup_test_brand():
    """Create FuelAI brand if it doesn't exist."""
    print("="*60)
    print("Setting up FuelAI brand...")
    print("="*60)
    
    conn = get_db_conn()
    cur = conn.cursor()
    
    # Check if brand already exists
    cur.execute("SELECT id, name FROM brands WHERE name = 'FuelAI'")
    row = cur.fetchone()
    
    if row:
        brand_id = row[0]
        print(f"✓ Brand 'FuelAI' already exists (ID: {brand_id})")
    else:
        # Use the hardcoded UUID from the code
        brand_id = "4c91c352-66f0-4c50-8466-dbaf4dfbff04"
        cur.execute(
            """
            INSERT INTO brands (id, name, account_handles)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                brand_id,
                "FuelAI",
                json.dumps({
                    "instagram": "getfuelai",
                    "facebook": "Fuel AI",
                    "linkedin": "fuelAI"
                })
            )
        )
        conn.commit()
        print(f"✓ Created brand 'FuelAI' (ID: {brand_id})")
    
    cur.close()
    conn.close()
    return brand_id


def add_source(platform, handle, is_competitor=False):
    """Add a source account."""
    conn = get_db_conn()
    cur = conn.cursor()
    
    # Check if exists
    cur.execute(
        "SELECT id FROM sources WHERE platform = %s AND handle = %s",
        (platform, handle)
    )
    row = cur.fetchone()
    
    if row:
        source_id = row[0]
        print(f"  ✓ Source @{handle} already exists (ID: {source_id})")
    else:
        cur.execute(
            """
            INSERT INTO sources (platform, handle, is_competitor, fetch_schedule)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (platform, handle, is_competitor, "daily")
        )
        source_id = cur.fetchone()[0]
        conn.commit()
        print(f"  ✓ Added source @{handle} (ID: {source_id})")
    
    cur.close()
    conn.close()
    return str(source_id)


def count_posts(source_id):
    """Count posts for a source."""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM posts_raw WHERE source_id = %s",
        (source_id,)
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def main():
    print("="*60)
    print("  Full End-to-End Ingestion Test")
    print("="*60)
    print()
    
    # Step 1: Setup brand
    brand_id = setup_test_brand()
    print()
    
    # Step 2: Add test sources
    print("="*60)
    print("Adding Instagram sources...")
    print("="*60)
    
    test_sources = [
        ("instagram", "nasa", False),
        ("instagram", "nike", True),  # competitor
        ("instagram", "salesforce", True),  # competitor
    ]
    
    source_ids = {}
    for platform, handle, is_competitor in test_sources:
        source_id = add_source(platform, handle, is_competitor)
        source_ids[handle] = source_id
    
    print()
    
    # Step 3: Fetch and ingest posts
    print("="*60)
    print("Fetching and ingesting posts...")
    print("="*60)
    print()
    
    for handle in ["nasa", "nike", "salesforce"]:
        source_id = source_ids[handle]
        print(f"--- @{handle} ---")
        
        # Count before
        before = count_posts(source_id)
        print(f"  Posts before: {before}")
        
        # Fetch posts
        posts = fetch_instagram_posts(handle, limit=5)
        print(f"  Fetched: {len(posts)} posts from Apify")
        
        if posts:
            # Ingest
            upsert_posts(
                platform="instagram",
                source_id=source_id,
                posts=posts
            )
            
            # Count after
            after = count_posts(source_id)
            print(f"  Posts after: {after}")
            print(f"  ✅ Ingested {after - before} new posts")
        else:
            print(f"  ⚠️  No posts to ingest")
        
        print()
    
    # Step 4: Summary
    print("="*60)
    print("Summary")
    print("="*60)
    
    conn = get_db_conn()
    cur = conn.cursor()
    
    # Total posts
    cur.execute("SELECT COUNT(*) FROM posts_raw")
    total = cur.fetchone()[0]
    print(f"Total posts in database: {total}")
    
    # By source
    cur.execute("""
        SELECT s.handle, s.platform, COUNT(p.id)
        FROM sources s
        LEFT JOIN posts_raw p ON p.source_id = s.id
        GROUP BY s.handle, s.platform
        ORDER BY COUNT(p.id) DESC
    """)
    
    print("\nPosts by source:")
    for handle, platform, count in cur.fetchall():
        print(f"  @{handle} ({platform}): {count} posts")
    
    cur.close()
    conn.close()
    
    print("\n🎉 Full ingestion test complete!")
    print("\nNext steps:")
    print("  1. Start web server: uvicorn app.main:app --reload")
    print("  2. Visit discovery UI: http://localhost:8000/discovery/ui")
    print("  3. Generate content drafts (API to be added)")


if __name__ == "__main__":
    main()

