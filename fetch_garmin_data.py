"""
PURE DEBUG - See What Garmin API Actually Returns
No assumptions, just print raw responses
"""

from datetime import datetime, timedelta
import os
import sys
import json
import base64
import garth

TOKEN_ENV_VAR = 'GARMIN_TOKENS_BASE64'
TOKEN_DIR = '/tmp/.garminconnect'

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def main():
    log("=" * 70)
    log("PURE DEBUG MODE - Dumping Raw API Responses")
    log("=" * 70)
    log("")
    
    # Setup tokens
    log("Setting up authentication...")
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    if not encoded_tokens:
        log("ERROR: No tokens!")
        sys.exit(1)
    
    json_str = base64.b64decode(encoded_tokens).decode()
    tokens = json.loads(json_str)
    
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    with open(os.path.join(TOKEN_DIR, 'oauth1_token.json'), 'w') as f:
        json.dump(tokens['oauth1_token'], f)
    
    with open(os.path.join(TOKEN_DIR, 'oauth2_token.json'), 'w') as f:
        json.dump(tokens['oauth2_token'], f)
    
    garth.resume(TOKEN_DIR)
    log("Authenticated!")
    log("")
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Test different profile endpoints
    profile_endpoints = [
        '/userprofile-service/userprofile',
        '/userprofile-service/socialProfile',
        '/userprofile-service/userprofile/personal-information',
    ]
    
    for endpoint in profile_endpoints:
        log("=" * 70)
        log(f"TESTING: {endpoint}")
        log("=" * 70)
        try:
            response = garth.connectapi(endpoint)
            log(f"Type: {type(response)}")
            
            if isinstance(response, list):
                log(f"List with {len(response)} items")
                if response:
                    log("First item:")
                    log(json.dumps(response[0], indent=2, default=str))
            else:
                log("Full response:")
                log(json.dumps(response, indent=2, default=str))
        except Exception as e:
            log(f"ERROR: {e}")
        log("")
    
    # Try to find display name in token data
    log("=" * 70)
    log("CHECKING: Token data for user info")
    log("=" * 70)
    log(f"OAuth1 keys: {list(tokens['oauth1_token'].keys())}")
    log(f"OAuth2 keys: {list(tokens['oauth2_token'].keys())}")
    log("")
    
    # Test data endpoints WITHOUT display name
    log("=" * 70)
    log("TESTING: Data endpoints without display name")
    log("=" * 70)
    
    data_endpoints = [
        f"/wellness-service/wellness/dailySummaryChart/{yesterday}",
        f"/userstats-service/statistics/{yesterday}",
        "/activitylist-service/activities/search/activities?limit=1",
    ]
    
    for endpoint in data_endpoints:
        log(f"Testing: {endpoint}")
        try:
            response = garth.connectapi(endpoint)
            log(f"  Type: {type(response)}")
            if isinstance(response, list):
                log(f"  List with {len(response)} items")
                if response:
                    log(f"  First item keys: {list(response[0].keys()) if isinstance(response[0], dict) else 'Not a dict'}")
            elif isinstance(response, dict):
                log(f"  Dict keys: {list(response.keys())}")
                # Look for step data
                if 'steps' in str(response).lower():
                    log("  >>> FOUND 'steps' in response!")
                    log(f"  {json.dumps(response, indent=2, default=str)[:500]}")
            else:
                log(f"  Response: {str(response)[:200]}")
        except Exception as e:
            log(f"  ERROR: {e}")
        log("")
    
    log("=" * 70)
    log("DEBUG COMPLETE")
    log("Look above for any endpoint that returned actual data")
    log("=" * 70)

if __name__ == '__main__':
    main()
