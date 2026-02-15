"""
Use garminconnect library after loading tokens with garth
The library might know the right endpoints/methods
"""

from datetime import datetime, timedelta
import sqlite3
import os
import sys
import json
import base64
import garth
from garminconnect import Garmin

TOKEN_ENV_VAR = 'GARMIN_TOKENS_BASE64'
TOKEN_DIR = '/tmp/.garminconnect'
DATABASE = 'health.db'
DAYS_TO_FETCH = int(os.environ.get('DAYS_TO_FETCH', '7'))  # Just 7 for testing

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_health (
            date TEXT PRIMARY KEY, steps INTEGER, distance_meters REAL,
            resting_heart_rate INTEGER, max_heart_rate INTEGER,
            sleep_duration_seconds INTEGER, sleep_score INTEGER,
            body_battery INTEGER, respiration_rate REAL,
            spo2_avg REAL, vo2_max REAL
        )
    ''')
    conn.commit()
    conn.close()

def main():
    log("=" * 70)
    log("Testing garminconnect library with pre-loaded tokens")
    log("=" * 70)
    log("")
    
    # Load tokens with garth first
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    json_str = base64.b64decode(encoded_tokens).decode()
    tokens = json.loads(json_str)
    
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    with open(os.path.join(TOKEN_DIR, 'oauth1_token.json'), 'w') as f:
        json.dump(tokens['oauth1_token'], f)
    
    with open(os.path.join(TOKEN_DIR, 'oauth2_token.json'), 'w') as f:
        json.dump(tokens['oauth2_token'], f)
    
    # Resume garth session
    log("Loading tokens with garth...")
    garth.resume(TOKEN_DIR)
    log("Garth session loaded")
    log("")
    
    # Now create Garmin client
    # It should automatically use the tokens from ~/.garminconnect
    log("Creating Garmin client...")
    try:
        client = Garmin()
        log("Garmin client created!")
        log("")
        
        # Try to get stats directly
        log("Attempting to get user stats...")
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            stats = client.get_stats(today)
            log(f"SUCCESS! Got stats: {stats}")
        except Exception as e:
            log(f"get_stats failed: {e}")
        
        try:
            steps = client.get_steps_data(today)
            log(f"SUCCESS! Got steps: {steps}")
        except Exception as e:
            log(f"get_steps_data failed: {e}")
        
        try:
            heart = client.get_heart_rates(today)
            log(f"SUCCESS! Got heart rate: {heart}")
        except Exception as e:
            log(f"get_heart_rates failed: {e}")
            
    except Exception as e:
        log(f"ERROR creating Garmin client: {e}")
        import traceback
        log(traceback.format_exc())
    
    log("")
    log("=" * 70)
    log("COMPLETE")
    log("=" * 70)

if __name__ == '__main__':
    main()
