#!/usr/bin/env python3
"""
Quick test script to check if Apify Instagram scraper is working.
"""

import os
import sys
import httpx
import json

def test_apify_instagram():
    """Test the Apify Instagram scraper with a known public account."""
    
    # Check for API token
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("❌ ERROR: APIFY_TOKEN environment variable not set")
        print("\nPlease set it with:")
        print("  export APIFY_TOKEN='your_token_here'")
        return False
    
    print(f"✓ Found APIFY_TOKEN: {token[:10]}...")
    
    # Test with a known public account
    test_username = "instagram"  # Instagram's official account
    
    url = (
        "https://api.apify.com/v2/acts/"
        "apify~instagram-scraper/run-sync-get-dataset-items"
        f"?token={token}"
    )
    
    payload = {
        "usernames": [test_username],
        "resultsLimit": 5,
        "includeStories": False,
        "searchType": "user",
        "addParentData": True,
    }
    
    # Add session cookie if available
    session_cookie = os.environ.get("IG_SESSIONID") or os.environ.get("IG_SESSION_COOKIE")
    if session_cookie:
        payload["sessionCookie"] = session_cookie
        print(f"✓ Using Instagram session cookie")
    else:
        print("⚠ Warning: No IG_SESSIONID set - may have rate limits")
    
    print(f"\n🔍 Testing Apify scraper with @{test_username}...")
    print(f"   Requesting up to 5 posts...")
    
    try:
        resp = httpx.post(url, json=payload, timeout=60)
        print(f"   HTTP Status: {resp.status_code}")
        
        if resp.status_code not in (200, 201):
            print(f"\n❌ Error: Unexpected status code")
            print(f"Response body (first 500 chars):")
            print(resp.text[:500])
            return False
        
        try:
            items = resp.json()
        except json.JSONDecodeError:
            print(f"\n❌ Error: Invalid JSON response")
            print(f"Response body (first 500 chars):")
            print(resp.text[:500])
            return False
        
        # Check for Apify-level errors
        if isinstance(items, list) and items and isinstance(items[0], dict) and "error" in items[0]:
            print(f"\n❌ Apify returned an error:")
            print(json.dumps(items[0], indent=2))
            return False
        
        if not items:
            print(f"\n⚠ Warning: No items returned (empty list)")
            return False
        
        print(f"\n✅ SUCCESS! Retrieved {len(items)} posts")
        
        # Show details of first post
        if items:
            first = items[0]
            print(f"\n📝 Sample Post Details:")
            print(f"   Post ID: {first.get('id') or first.get('shortCode')}")
            print(f"   Caption: {(first.get('caption') or first.get('captionText') or '')[:100]}...")
            print(f"   Likes: {first.get('likesCount', 'N/A')}")
            print(f"   Comments: {first.get('commentsCount', 'N/A')}")
            print(f"   Timestamp: {first.get('timestamp') or first.get('takenAtTimestamp')}")
            
            print(f"\n📋 Available fields in response:")
            print(f"   {', '.join(sorted(first.keys())[:10])}...")
        
        return True
        
    except httpx.TimeoutException:
        print(f"\n❌ Error: Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  Apify Instagram Scraper Test")
    print("=" * 60)
    
    success = test_apify_instagram()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test PASSED - Apify integration is working!")
        print("\nNext steps:")
        print("  1. Set up Docker services: make up")
        print("  2. Initialize database: make init")
        print("  3. Add sources and run ingestion")
    else:
        print("❌ Test FAILED - Check the errors above")
        print("\nTroubleshooting:")
        print("  1. Verify APIFY_TOKEN is valid")
        print("  2. Check Apify dashboard for quota/errors")
        print("  3. Try setting IG_SESSIONID for authenticated access")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

