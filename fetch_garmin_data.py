"""
Garmin Data Fetcher - Direct garth Implementation
Bypasses garminconnect wrapper, uses garth library directly
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
DAYS_TO_FETCH = int(os.environ.get('DAYS_TO_FETCH', '90'))

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def setup_and_authenticate():
    """Setup tokens and authenticate using garth directly"""
    log("=" * 60)
    log("Setting up Garmin authentication")
    log("=" * 60)
    
    # Get encoded tokens from environment
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    
    if not encoded_tokens:
        log(f"ERROR: {TOKEN_ENV_VAR} environment variable not set!")
        sys.exit(1)
    
    log(f"Found {TOKEN_ENV_VAR} ({len(encoded_tokens)} characters)")
    
    # Decode from base64
    try:
        json_str = base64.b64decode(encoded_tokens).decode()
        tokens = json.loads(json_str)
        log("Decoded tokens successfully")
    except Exception as e:
        log(f"ERROR: Failed to decode tokens: {e}")
        sys.exit(1)
    
    # Create token directory
    os.makedirs(TOKEN_DIR, exist_ok=True)
    log(f"Created token directory: {TOKEN_DIR}")
    
    # Write token files
    try:
        oauth1_path = os.path.join(TOKEN_DIR, 'oauth1_token.json')
        with open(oauth1_path, 'w') as f:
            json.dump(tokens['oauth1_token'], f)
        
        oauth2_path = os.path.join(TOKEN_DIR, 'oauth2_token.json')
        with open(oauth2_path, 'w') as f:
            json.dump(tokens['oauth2_token'], f)
        
        log("Wrote token files")
    except Exception as e:
        log(f"ERROR: Failed to write token files: {e}")
        sys.exit(1)
    
    # Load tokens using garth
    try:
        log("")
        log("Loading session with garth...")
        garth.resume(TOKEN_DIR)
        log("Tokens loaded successfully")
        
        # Test with a simple API call
        log("Testing API connection...")
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Use garth's connectapi method directly
        stats = garth.connectapi(f"/usersummary-service/usersummary/daily/{today}")
        
        log("AUTHENTICATION SUCCESSFUL!")
        log("")
        
    except Exception as e:
        log(f"ERROR: Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def get_db_connection():
    """Connect to SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def save_daily_health(conn, date_str, data):
    """Save daily health metrics to database"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO daily_health (
                date, steps, distance_meters, resting_heart_rate, max_heart_rate,
                sleep_duration_seconds, sleep_score, body_battery, respiration_rate,
                spo2_avg, vo2_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date_str,
            data.get('steps'),
            data.get('distance_meters'),
            data.get('resting_hr'),
            data.get('max_hr'),
            data.get('sleep_duration'),
            data.get('sleep_score'),
            data.get('body_battery'),
            data.get('respiration'),
            data.get('spo2'),
            data.get('vo2_max')
        ))
        conn.commit()
        return True
    except Exception as e:
        log(f"Error saving daily health for {date_str}: {e}")
        return False

def fetch_garmin_data():
    """Main function using garth API directly"""
    log("")
    log("=" * 60)
    log("Starting Garmin Data Sync")
    log("=" * 60)
    log("")
    
    # Setup and authenticate
    setup_and_authenticate()
    
    log("-" * 60)
    
    # Connect to database
    conn = get_db_connection()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TO_FETCH)
    
    log(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    log(f"Time period: {DAYS_TO_FETCH} days")
    log("")
    
    # Fetch daily health data
    log("Fetching daily health metrics...")
    current_date = start_date
    daily_count = 0
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            # Get daily stats using garth directly
            stats = garth.connectapi(f"/usersummary-service/usersummary/daily/{date_str}")
            
            # Get heart rate data
            hr_data = garth.connectapi(f"/wellness-service/wellness/dailyHeartRate/{date_str}")
            
            # Extract data from responses
            steps = stats.get('totalSteps', 0) if stats else 0
            distance = stats.get('totalDistanceMeters', 0) if stats else 0
            resting_hr = hr_data.get('restingHeartRate') if hr_data else None
            max_hr = hr_data.get('maxHeartRate') if hr_data else None
            
            # Get sleep data
            sleep_score = None
            sleep_duration = None
            try:
                sleep_data = garth.connectapi(f"/wellness-service/wellness/dailySleepData/{date_str}")
                if sleep_data and 'dailySleepDTO' in sleep_data:
                    sleep_score = sleep_data['dailySleepDTO'].get('sleepScores', {}).get('overall', {}).get('value')
                    sleep_duration = sleep_data['dailySleepDTO'].get('sleepTimeSeconds')
            except:
                pass
            
            # Get body battery
            body_battery = None
            try:
                bb_data = garth.connectapi(f"/wellness-service/wellness/bodyBattery/reports/daily/{date_str}")
                if bb_data and isinstance(bb_data, list) and len(bb_data) > 0:
                    body_battery = bb_data[0].get('charged')
            except:
                pass
            
            # Get respiration
            respiration = None
            try:
                resp_data = garth.connectapi(f"/wellness-service/wellness/daily/respiration/{date_str}")
                if resp_data:
                    respiration = resp_data.get('avgWakingRespirationValue')
            except:
                pass
            
            # Get SpO2
            spo2 = None
            try:
                spo2_data = garth.connectapi(f"/wellness-service/wellness/daily/spo2/{date_str}")
                if spo2_data:
                    spo2 = spo2_data.get('averageSpo2')
            except:
                pass
            
            # Compile data
            daily_data = {
                'steps': steps,
                'distance_meters': distance,
                'resting_hr': resting_hr,
                'max_hr': max_hr,
                'sleep_duration': sleep_duration,
                'sleep_score': sleep_score,
                'body_battery': body_battery,
                'respiration': respiration,
                'spo2': spo2,
                'vo2_max': None  # Would need different endpoint
            }
            
            # Save to database
            if save_daily_health(conn, date_str, daily_data):
                daily_count += 1
                log(f"  {date_str}: {steps:,} steps, HR {resting_hr or 'N/A'}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            log(f"  {date_str}: Could not fetch data - {e}")
        
        current_date += timedelta(days=1)
    
    log("")
    log(f"Saved {daily_count} days of health data")
    
    # Close database
    conn.close()
    
    log("")
    log("=" * 60)
    log("Sync Complete!")
    log(f"   {daily_count} days of health data")
    log("=" * 60)
    log("")

if __name__ == '__main__':
    try:
        fetch_garmin_data()
    except KeyboardInterrupt:
        log("")
        log("Sync interrupted by user")
        sys.exit(0)
    except Exception as e:
        log("")
        log("=" * 60)
        log(f"FATAL ERROR: {e}")
        log("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
