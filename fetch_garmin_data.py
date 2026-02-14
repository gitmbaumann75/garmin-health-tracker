"""
Garmin Data Fetcher - DEEP DEBUG VERSION
Shows exactly what's happening at each step
"""

from garminconnect import Garmin
from datetime import datetime
import os
import sys
import json
import base64

TOKEN_ENV_VAR = 'GARMIN_TOKENS_BASE64'
TOKEN_DIR = '/tmp/.garminconnect'

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def debug_log(message):
    """Print debug message"""
    print(f"[DEBUG] {message}")

def setup_and_test_tokens():
    """Setup tokens and test every step"""
    log("=" * 60)
    log("🔍 DEEP DEBUG MODE - Token Authentication")
    log("=" * 60)
    
    # Step 1: Check environment variable
    debug_log("Step 1: Checking for GARMIN_TOKENS_BASE64 environment variable")
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    
    if not encoded_tokens:
        log(f"❌ ERROR: {TOKEN_ENV_VAR} not found in environment")
        sys.exit(1)
    
    debug_log(f"✓ Found environment variable")
    debug_log(f"  Length: {len(encoded_tokens)} characters")
    debug_log(f"  First 50 chars: {encoded_tokens[:50]}...")
    debug_log(f"  Last 10 chars: ...{encoded_tokens[-10:]}")
    
    # Step 2: Decode base64
    debug_log("Step 2: Decoding from base64")
    try:
        json_str = base64.b64decode(encoded_tokens).decode()
        debug_log(f"✓ Decoded successfully")
        debug_log(f"  Decoded length: {len(json_str)} characters")
    except Exception as e:
        log(f"❌ ERROR: Failed to decode: {e}")
        sys.exit(1)
    
    # Step 3: Parse JSON
    debug_log("Step 3: Parsing JSON")
    try:
        tokens = json.loads(json_str)
        debug_log(f"✓ JSON parsed successfully")
        debug_log(f"  Top-level keys: {list(tokens.keys())}")
    except Exception as e:
        log(f"❌ ERROR: Failed to parse JSON: {e}")
        sys.exit(1)
    
    # Step 4: Inspect token structure
    debug_log("Step 4: Inspecting token structure")
    
    if 'oauth1_token' in tokens:
        oauth1 = tokens['oauth1_token']
        debug_log(f"✓ oauth1_token present")
        debug_log(f"  Type: {type(oauth1)}")
        debug_log(f"  Keys: {list(oauth1.keys()) if isinstance(oauth1, dict) else 'Not a dict'}")
        if isinstance(oauth1, dict):
            for key in oauth1.keys():
                value = oauth1[key]
                if isinstance(value, str):
                    debug_log(f"    {key}: {value[:50]}... (length: {len(value)})")
                else:
                    debug_log(f"    {key}: {value}")
    else:
        log(f"❌ ERROR: oauth1_token not found in tokens")
        sys.exit(1)
    
    if 'oauth2_token' in tokens:
        oauth2 = tokens['oauth2_token']
        debug_log(f"✓ oauth2_token present")
        debug_log(f"  Type: {type(oauth2)}")
        debug_log(f"  Keys: {list(oauth2.keys()) if isinstance(oauth2, dict) else 'Not a dict'}")
        if isinstance(oauth2, dict):
            for key in oauth2.keys():
                value = oauth2[key]
                if isinstance(value, str) and len(value) > 50:
                    debug_log(f"    {key}: {value[:50]}... (length: {len(value)})")
                else:
                    debug_log(f"    {key}: {value}")
    else:
        log(f"❌ ERROR: oauth2_token not found in tokens")
        sys.exit(1)
    
    # Step 5: Create token directory
    debug_log("Step 5: Creating token directory")
    try:
        os.makedirs(TOKEN_DIR, exist_ok=True)
        debug_log(f"✓ Directory created: {TOKEN_DIR}")
        debug_log(f"  Directory exists: {os.path.exists(TOKEN_DIR)}")
        debug_log(f"  Directory writable: {os.access(TOKEN_DIR, os.W_OK)}")
    except Exception as e:
        log(f"❌ ERROR: Failed to create directory: {e}")
        sys.exit(1)
    
    # Step 6: Write token files
    debug_log("Step 6: Writing token files")
    
    oauth1_path = os.path.join(TOKEN_DIR, 'oauth1_token.json')
    try:
        with open(oauth1_path, 'w') as f:
            json.dump(tokens['oauth1_token'], f, indent=2)
        debug_log(f"✓ Wrote oauth1_token.json")
        debug_log(f"  File exists: {os.path.exists(oauth1_path)}")
        debug_log(f"  File size: {os.path.getsize(oauth1_path)} bytes")
        
        # Read back and verify
        with open(oauth1_path, 'r') as f:
            verify_oauth1 = json.load(f)
        debug_log(f"  Verified readable: {list(verify_oauth1.keys())}")
    except Exception as e:
        log(f"❌ ERROR: Failed to write oauth1_token.json: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    oauth2_path = os.path.join(TOKEN_DIR, 'oauth2_token.json')
    try:
        with open(oauth2_path, 'w') as f:
            json.dump(tokens['oauth2_token'], f, indent=2)
        debug_log(f"✓ Wrote oauth2_token.json")
        debug_log(f"  File exists: {os.path.exists(oauth2_path)}")
        debug_log(f"  File size: {os.path.getsize(oauth2_path)} bytes")
        
        # Read back and verify
        with open(oauth2_path, 'r') as f:
            verify_oauth2 = json.load(f)
        debug_log(f"  Verified readable: {list(verify_oauth2.keys())}")
    except Exception as e:
        log(f"❌ ERROR: Failed to write oauth2_token.json: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    log("")
    log("✅ Token files created successfully")
    log("")
    
    # Step 7: Test authentication
    debug_log("Step 7: Testing authentication")
    debug_log("  Initializing Garmin client...")
    
    try:
        client = Garmin()
        debug_log(f"✓ Garmin client initialized")
        debug_log(f"  Client type: {type(client)}")
        debug_log(f"  Has garth attribute: {hasattr(client, 'garth')}")
        
        if hasattr(client, 'garth'):
            debug_log(f"  Garth type: {type(client.garth)}")
            debug_log(f"  Garth has oauth1_token: {hasattr(client.garth, 'oauth1_token')}")
            debug_log(f"  Garth has oauth2_token: {hasattr(client.garth, 'oauth2_token')}")
    except Exception as e:
        log(f"❌ ERROR: Failed to initialize client: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 8: Attempt login with token directory
    debug_log("Step 8: Attempting login with token directory")
    debug_log(f"  Token directory path: {TOKEN_DIR}")
    debug_log(f"  Calling client.login('{TOKEN_DIR}')")
    
    try:
        result = client.login(TOKEN_DIR)
        debug_log(f"✓ login() call completed")
        debug_log(f"  Result type: {type(result)}")
        debug_log(f"  Result value: {result}")
        
        # Check client state after login
        if hasattr(client, 'garth'):
            debug_log(f"  After login - oauth1_token: {client.garth.oauth1_token is not None}")
            debug_log(f"  After login - oauth2_token: {client.garth.oauth2_token is not None}")
        
        if hasattr(client, 'display_name'):
            debug_log(f"  Display name: {client.display_name}")
        
        log("")
        log("✅ AUTHENTICATION SUCCESSFUL!")
        log("")
        
        # Try to make an API call to verify it really works
        debug_log("Step 9: Testing API call")
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            debug_log(f"  Calling get_stats('{today}')")
            stats = client.get_stats(today)
            debug_log(f"✓ API call successful")
            debug_log(f"  Stats type: {type(stats)}")
            if isinstance(stats, dict):
                debug_log(f"  Stats keys: {list(stats.keys())[:5]}...")
            log("")
            log("✅ API CALL SUCCESSFUL - AUTHENTICATION VERIFIED!")
            log("")
            
        except Exception as e:
            log(f"⚠️  WARNING: Login succeeded but API call failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        log(f"❌ ERROR: Authentication failed during login()")
        log(f"  Error type: {type(e).__name__}")
        log(f"  Error message: {e}")
        log("")
        debug_log("Full traceback:")
        import traceback
        traceback.print_exc()
        log("")
        
        # Try to get more info about the error
        if hasattr(e, '__dict__'):
            debug_log(f"Error attributes: {e.__dict__}")
        
        if hasattr(e, 'response'):
            debug_log(f"Has response attribute")
            if hasattr(e.response, 'status_code'):
                debug_log(f"  Status code: {e.response.status_code}")
            if hasattr(e.response, 'text'):
                debug_log(f"  Response text (first 500 chars): {e.response.text[:500]}")
        
        sys.exit(1)

if __name__ == '__main__':
    setup_and_test_tokens()
