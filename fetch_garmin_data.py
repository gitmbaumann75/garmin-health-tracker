"""
Garmin Data Fetcher - Using Garth's Built-in Classes
These handle user IDs automatically
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
    """Setup tokens and authenticate"""
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
    log("AUTHENTICATION SUCCESSFUL!")
    log("")

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
    """Main function using garth's built-in classes"""
    log("")
    log("=" * 60)
    log("Starting Garmin Data Sync")
    log("=" * 60)
    log("")
    
    init_database()
    log("")
    setup_and_authenticate()
    
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
            # Use garth's built-in DailySteps class
            steps_data = garth.DailySteps.get(date_str)
            steps = steps_data.steps if hasattr(steps_data, 'steps') else 0
            distance = steps_data.distance if hasattr(steps_data, 'distance') else 0
            
            # Get heart rate
            resting_hr = None
            max_hr = None
            try:
                hr_data = garth.DailyHeartRate.get(date_str)
                if hr_data:
                    resting_hr = hr_data.resting_heart_rate if hasattr(hr_data, 'resting_heart_rate') else None
                    max_hr = hr_data.max_heart_rate if hasattr(hr_data, 'max_heart_rate') else None
            except:
                pass
            
            # Get sleep data
            sleep_score = None
            sleep_duration = None
            try:
                sleep_data = garth.SleepData.get(date_str)
                if sleep_data:
                    sleep_score = sleep_data.sleep_scores.get('overall', {}).get('value') if hasattr(sleep_data, 'sleep_scores') else None
                    sleep_duration = sleep_data.sleep_time_seconds if hasattr(sleep_data, 'sleep_time_seconds') else None
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
                log(f"  {date_str}: {steps:,} steps, HR {resting_hr or 'N/A'}")
            
            time.sleep(0.5)
            
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
