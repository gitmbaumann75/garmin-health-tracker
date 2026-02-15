"""
Garmin Data Fetcher - DEBUG VERSION
Shows what API responses actually contain
"""

from datetime import datetime, timedelta
import sqlite3
import os
import sys
import json
import base64
import time
import garth

# Configuration
TOKEN_ENV_VAR = 'GARMIN_TOKENS_BASE64'
TOKEN_DIR = '/tmp/.garminconnect'
DATABASE = 'health.db'
DAYS_TO_FETCH = 7  # Just 7 days for debugging

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def setup_and_authenticate():
    """Setup tokens and authenticate"""
    log("Setting up authentication...")
    
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    if not encoded_tokens:
        log("ERROR: No tokens found!")
        sys.exit(1)
    
    json_str = base64.b64decode(encoded_tokens).decode()
    tokens = json.loads(json_str)
    
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    with open(os.path.join(TOKEN_DIR, 'oauth1_token.json'), 'w') as f:
        json.dump(tokens['oauth1_token'], f)
    
    with open(os.path.join(TOKEN_DIR, 'oauth2_token.json'), 'w') as f:
        json.dump(tokens['oauth2_token'], f)
    
    garth.resume(TOKEN_DIR)
    
    # Get profile info
    profile = garth.client.profile
    log(f"Authenticated!")
    if profile:
        log(f"Display Name: {profile.get('displayName')}")
        log(f"Profile ID: {profile.get('profileId')}")
    log("")

def main():
    log("=" * 60)
    log("DEBUG MODE - Testing API Responses")
    log("=" * 60)
    log("")
    
    setup_and_authenticate()
    
    today = datetime.now().strftime('%Y-%m-%d')
    log(f"Testing endpoints for date: {today}")
    log("")
    
    # Test different endpoints
    endpoints = [
        f"/usersummary-service/usersummary/daily/{today}",
        f"/wellness-service/wellness/dailyHeartRate/{today}",
        f"/activitylist-service/activities/search/activities?limit=1",
    ]
    
    for endpoint in endpoints:
        log("-" * 60)
        log(f"Testing: {endpoint}")
        try:
            response = garth.connectapi(endpoint)
            log(f"SUCCESS!")
            log(f"Response type: {type(response)}")
            
            if isinstance(response, dict):
                log(f"Keys: {list(response.keys())}")
                log(f"Full response:")
                log(json.dumps(response, indent=2, default=str)[:1000])  # First 1000 chars
            elif isinstance(response, list):
                log(f"List with {len(response)} items")
                if response:
                    log(f"First item: {json.dumps(response[0], indent=2, default=str)[:500]}")
            else:
                log(f"Response: {str(response)[:500]}")
        except Exception as e:
            log(f"ERROR: {e}")
        log("")
    
    log("=" * 60)
    log("DEBUG COMPLETE")
    log("=" * 60)

if __name__ == '__main__':
    main()
