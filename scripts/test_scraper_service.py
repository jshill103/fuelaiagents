#!/usr/bin/env python3
"""
Test the fixed instagram_scraper service directly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required credentials are set
if not os.environ.get("APIFY_TOKEN"):
    print("❌ ERROR: APIFY_TOKEN not set in environment or .env file")
    print("Please create a .env file with your API keys. See SETUP_GUIDE.md")
    sys.exit(1)

# Now import the service
from app.services.instagram_scraper import fetch_instagram_posts

def test_account(handle, limit=5):
    """Test scraping a specific Instagram account."""
    print("="*60)
    print(f"Testing: @{handle}")
    print("="*60)
    
    try:
        posts = fetch_instagram_posts(handle, limit=limit)
        
        if not posts:
            print(f"❌ No posts returned for @{handle}")
            return False
        
        print(f"\n✅ SUCCESS! Got {len(posts)} posts for @{handle}")
        
        # Show details of first post
        if posts:
            first = posts[0]
            print(f"\n📝 First Post Details:")
            print(f"   Post ID: {first.get('post_id')}")
            print(f"   Caption: {first.get('caption', '')[:100]}...")
            print(f"   Hashtags: {first.get('hashtags', [])[:5]}")
            print(f"   Media URLs: {len(first.get('media_urls', []))} images/videos")
            print(f"   Posted At: {first.get('posted_at')}")
            print(f"   Engagement: {first.get('engagement')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("  Testing Fixed Instagram Scraper Service")
    print("="*60)
    print()
    
    # Test with some popular accounts
    test_accounts = [
        "nasa",
        "natgeo", 
        "nike",
    ]
    
    results = {}
    for handle in test_accounts:
        success = test_account(handle, limit=3)
        results[handle] = success
        print()
    
    print("="*60)
    print("  Summary")
    print("="*60)
    for handle, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} @{handle}")
    
    all_success = all(results.values())
    if all_success:
        print("\n🎉 All tests passed! Instagram scraper is working!")
    else:
        print("\n⚠️  Some tests failed - check errors above")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())

