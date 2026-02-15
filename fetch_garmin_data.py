"""
Garmin Data Fetcher - FIXED VERSION
Handles profile endpoint returning list instead of dict
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

def init_database():
    """Initialize database tables"""
    log("Initializing database...")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_health (
            date TEXT PRIMARY KEY,
            steps INTEGER,
            distance_meters REAL,
            resting_heart_rate INTEGER,
            max_heart_rate INTEGER,
            sleep_duration_seconds INTEGER,
            sleep_score INTEGER,
            body_battery INTEGER,
            respiration_rate REAL,
            spo2_avg REAL,
            vo2_max REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    log("Database initialized")

def setup_and_authenticate():
    """Setup tokens, authenticate, and get user profile"""
    log("=" * 60)
    log("Setting up Garmin authentication")
    log("=" * 60)
    
    encoded_tokens = os.environ.get(TOKEN_ENV_VAR)
    if not encoded_tokens:
        log("ERROR: No tokens found!")
        sys.exit(1)
    
    log(f"Found GARMIN_TOKENS_BASE64 ({len(encoded_tokens)} characters)")
    
    json_str = base64.b64decode(encoded_tokens).decode()
    tokens = json.loads(json_str)
    log("Decoded tokens successfully")
    
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    with open(os.path.join(TOKEN_DIR, 'oauth1_token.json'), 'w') as f:
        json.dump(tokens['oauth1_token'], f)
    
    with open(os.path.join(TOKEN_DIR, 'oauth2_token.json'), 'w') as f:
        json.dump(tokens['oauth2_token'], f)
    
    log("Wrote token files")
    log("")
    log("Loading session with garth...")
    garth.resume(TOKEN_DIR)
    log("Session loaded successfully!")
    
    # Get user profile to find display name
    log("Fetching user profile...")
    try:
        profile_response = garth.connectapi('/userprofile-service/userprofile')
        
        # Handle response that could be list or dict
        profile = profile_response
        if isinstance(profile_response, list) and len(profile_response) > 0:
            profile = profile_response[0]
        
        display_name = profile.get('displayName')
        user_id = profile.get('profileId')
        
        if not display_name:
            # Try to get from userName or profileId
            display_name = profile.get('userName') or profile.get('profileId')
        
        log(f"Display Name: {display_name}")
        log(f"User ID: {user_id}")
        log("AUTHENTICATION SUCCESSFUL!")
        log("")
        
        return display_name
        
    except Exception as e:
        log(f"ERROR getting profile: {e}")
        import traceback
        log(traceback.format_exc())
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
        log(f"Error saving {date_str}: {e}")
        return False

def fetch_garmin_data():
    """Main function"""
    log("")
    log("=" * 60)
    log("Starting Garmin Data Sync")
    log("=" * 60)
    log("")
    
    init_database()
    log("")
    display_name = setup_and_authenticate()
    
    log("-" * 60)
    
    conn = get_db_connection()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TO_FETCH)
    
    log(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    log(f"Time period: {DAYS_TO_FETCH} days")
    log("")
    
    log("Fetching daily health metrics...")
    current_date = start_date
    daily_count = 0
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            # Get daily summary with displayName in URL
            summary_url = f"/usersummary-service/usersummary/daily/{display_name}?calendarDate={date_str}"
            summary = garth.connectapi(summary_url)
            
            # Extract steps and distance
            steps = 0
            distance = 0
            if summary:
                steps = summary.get('totalSteps', 0)
                distance = summary.get('totalDistanceMeters', 0)
            
            # Get heart rate data
            resting_hr = None
            max_hr = None
            try:
                hr_url = f"/wellness-service/wellness/dailyHeartRate/{display_name}?date={date_str}"
                hr_data = garth.connectapi(hr_url)
                if hr_data:
                    resting_hr = hr_data.get('restingHeartRate')
                    max_hr = hr_data.get('maxHeartRate')
            except:
                pass
            
            # Get sleep data
            sleep_score = None
            sleep_duration = None
            try:
                sleep_url = f"/wellness-service/wellness/dailySleepData/{display_name}?date={date_str}"
                sleep_data = garth.connectapi(sleep_url)
                if sleep_data and 'dailySleepDTO' in sleep_data:
                    sleep_dto = sleep_data['dailySleepDTO']
                    if 'sleepScores' in sleep_dto and 'overall' in sleep_dto['sleepScores']:
                        sleep_score = sleep_dto['sleepScores']['overall'].get('value')
                    sleep_duration = sleep_dto.get('sleepTimeSeconds')
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
                'body_battery': None,
                'respiration': None,
                'spo2': None,
                'vo2_max': None
            }
            
            # Save to database
            if save_daily_health(conn, date_str, daily_data):
                daily_count += 1
                if steps > 0 or resting_hr:
                    log(f"  {date_str}: {steps:,} steps, HR {resting_hr or 'N/A'}")
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            log(f"  {date_str}: Error - {e}")
        
        current_date += timedelta(days=1)
    
    log("")
    log(f"Saved {daily_count} days of health data")
    
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
        log("Sync interrupted")
        sys.exit(0)
    except Exception as e:
        log("=" * 60)
        log(f"FATAL ERROR: {e}")
        log("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
