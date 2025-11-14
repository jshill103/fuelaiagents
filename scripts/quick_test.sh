#!/bin/bash

# Quick test script - no .env file needed
# Usage: ./quick_test.sh YOUR_APIFY_TOKEN [YOUR_IG_SESSIONID]

if [ -z "$1" ]; then
    echo "Usage: ./quick_test.sh YOUR_APIFY_TOKEN [YOUR_IG_SESSIONID]"
    echo ""
    echo "Example:"
    echo "  ./quick_test.sh apify_api_AbCdEf123456"
    echo "  ./quick_test.sh apify_api_AbCdEf123456 your_instagram_sessionid"
    exit 1
fi

export APIFY_TOKEN="$1"

if [ -n "$2" ]; then
    export IG_SESSIONID="$2"
    echo "✓ Using Instagram session cookie"
fi

echo "Testing Apify integration..."
echo ""

# Activate venv
source venv/bin/activate

# Run test
python3 test_apify.py

