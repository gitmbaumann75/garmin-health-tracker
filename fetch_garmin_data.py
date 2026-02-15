"""
Garmin Data Fetcher - DEBUG VERSION (Fixed)
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
    log("Authenticated successfully!")
    log("")

def main():
    log("=" * 60)
    log("DEBUG MODE - Testing API Responses")
    log("=" * 60)
    log("")
    
    setup_and_authenticate()
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    log(f"Testing endpoints for dates: {yesterday} and {today}")
    log("")
    
    # Test different endpoints with different date formats
    endpoints_to_test = [
        # User summary endpoints
        (f"/usersummary-service/usersummary/daily/{today}", "User Summary Today"),
        (f"/usersummary-service/usersummary/daily/{yesterday}", "User Summary Yesterday"),
        
        # Wellness endpoints
        (f"/wellness-service/wellness/dailyHeartRate/{today}", "Heart Rate Today"),
        (f"/wellness-service/wellness/dailySleepData/{today}", "Sleep Data Today"),
        
        # Activity endpoints
        ("/activitylist-service/activities/search/activities?limit=5", "Recent Activities"),
        
        # Stats endpoint
        (f"/usersummary-service/stats/daily/{today}", "Daily Stats"),
    ]
    
    for endpoint, description in endpoints_to_test:
        log("-" * 60)
        log(f"TEST: {description}")
        log(f"Endpoint: {endpoint}")
        try:
            response = garth.connectapi(endpoint)
            log(f"SUCCESS!")
            log(f"Response type: {type(response)}")
            
            if isinstance(response, dict):
                log(f"Keys found: {list(response.keys())}")
                # Show first level of data
                for key, value in list(response.items())[:10]:  # First 10 keys
                    if isinstance(value, (dict, list)):
                        log(f"  {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        log(f"  {key}: {value}")
                
                # If there's a totalSteps field, show it
                if 'totalSteps' in response:
                    log(f">>> FOUND STEPS: {response['totalSteps']}")
                
                # Show full JSON for small responses
                json_str = json.dumps(response, indent=2, default=str)
                if len(json_str) < 2000:
                    log("Full response:")
                    log(json_str)
                else:
                    log(f"(Response too large: {len(json_str)} chars, showing first 1000)")
                    log(json_str[:1000])
                    
            elif isinstance(response, list):
                log(f"List with {len(response)} items")
                if response and len(response) > 0:
                    log(f"First item type: {type(response[0])}")
                    if isinstance(response[0], dict):
                        log(f"First item keys: {list(response[0].keys())}")
                        log(f"First item preview:")
                        log(json.dumps(response[0], indent=2, default=str)[:500])
            else:
                log(f"Response: {str(response)[:500]}")
                
        except Exception as e:
            log(f"ERROR: {e}")
            import traceback
            log(traceback.format_exc()[:500])
        
        log("")
    
    log("=" * 60)
    log("DEBUG COMPLETE")
    log("Next: Look at which endpoint returned your step count")
    log("=" * 60)

if __name__ == '__main__':
    main()
