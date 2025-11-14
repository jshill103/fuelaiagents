#!/usr/bin/env python3
"""
Advanced Apify Instagram test with multiple strategies.
"""

import os
import httpx
import json
import time

APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
IG_SESSION = os.environ.get("IG_SESSIONID")

def test_actor(actor_name, payload, test_name):
    """Test a specific Apify actor with given payload."""
    print(f"\n{'='*60}")
    print(f"🧪 Test: {test_name}")
    print(f"   Actor: {actor_name}")
    print(f"{'='*60}")
    
    url = f"https://api.apify.com/v2/acts/{actor_name}/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("\n⏳ Sending request...")
        resp = httpx.post(url, json=payload, timeout=120)
        print(f"✓ HTTP Status: {resp.status_code}")
        
        if resp.status_code not in (200, 201):
            print(f"❌ Error: Non-200/201 status")
            print(f"Response: {resp.text[:500]}")
            return None
        
        items = resp.json()
        
        # Check for error response
        if isinstance(items, list) and items:
            if isinstance(items[0], dict) and "error" in items[0]:
                print(f"❌ Apify error: {items[0].get('error')}")
                print(f"   Description: {items[0].get('errorDescription', 'N/A')}")
                return None
        
        if not items:
            print(f"⚠️  Empty response (no items)")
            return None
        
        print(f"✅ SUCCESS! Got {len(items)} items")
        
        # Show first item details
        if items and isinstance(items[0], dict):
            first = items[0]
            print(f"\n📝 First item keys: {list(first.keys())[:10]}")
            if 'caption' in first or 'captionText' in first:
                caption = first.get('caption') or first.get('captionText', '')
                print(f"   Caption preview: {caption[:100]}...")
            if 'likesCount' in first:
                print(f"   Likes: {first.get('likesCount')}")
        
        return items
        
    except httpx.TimeoutException:
        print(f"❌ Timeout after 120 seconds")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    if not APIFY_TOKEN:
        print("❌ APIFY_TOKEN not set")
        return
    
    print("="*60)
    print("  Advanced Apify Instagram Scraper Test")
    print("="*60)
    print(f"✓ Token: {APIFY_TOKEN[:15]}...")
    if IG_SESSION:
        print(f"✓ Session: {IG_SESSION[:20]}...")
    
    # Test 1: Standard instagram-scraper with different account
    test_actor(
        "apify~instagram-scraper",
        {
            "usernames": ["natgeo"],  # Try National Geographic
            "resultsLimit": 3,
            "searchType": "user",
            "addParentData": False,
        },
        "Standard scraper - natgeo (no session)"
    )
    
    time.sleep(2)
    
    # Test 2: With session cookie
    if IG_SESSION:
        test_actor(
            "apify~instagram-scraper",
            {
                "usernames": ["nike"],
                "resultsLimit": 3,
                "searchType": "user",
                "sessionCookie": IG_SESSION,
            },
            "Standard scraper - nike (with session)"
        )
        time.sleep(2)
    
    # Test 3: Try direct profile URL
    test_actor(
        "apify~instagram-scraper",
        {
            "directUrls": ["https://www.instagram.com/nasa/"],
            "resultsLimit": 3,
            "addParentData": False,
        },
        "Direct URL - NASA"
    )
    
    time.sleep(2)
    
    # Test 4: Try alternative actor (instagram-profile-scraper)
    test_actor(
        "apify~instagram-profile-scraper",
        {
            "usernames": ["redbull"],
            "resultsType": "posts",
            "resultsLimit": 3,
        },
        "Profile scraper - redbull"
    )
    
    time.sleep(2)
    
    # Test 5: Hashtag search instead of user
    test_actor(
        "apify~instagram-scraper",
        {
            "hashtags": ["saas"],
            "resultsLimit": 3,
            "searchType": "hashtag",
        },
        "Hashtag search - #saas"
    )
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)


if __name__ == "__main__":
    main()

