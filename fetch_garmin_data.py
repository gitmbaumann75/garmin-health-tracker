"""
Garmin Data Fetcher - Environment Variable Method
Sets GARMINTOKENS env var and lets garminconnect auto-load tokens
"""

from garminconnect import Garmin
from datetime import datetime, timedelta
import sqlite3
import os
import sys
import json
import base64
import time

# Configuration
TOKEN_ENV_VAR = 'GARMIN_TOKENS_BASE64'
TOKEN_DIR = '/tmp/.garminconnect'
DATABASE = 'health.db'
DAYS_TO_FETCH = int(os.environ.get('DAYS_TO_FETCH', '90'))

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def setup_token_directory():
    """Create token directory from environment variable"""
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
        log(f"Wrote oauth1_token.json")
        
        oauth2_path = os.path.join(TOKEN_DIR, 'oauth2_token.json')
        with open(oauth2_path, 'w') as f:
            json.dump(tokens['oauth2_token'], f)
        log(f"Wrote oauth2_token.json")
        
    except Exception as e:
        log(f"ERROR: Failed to write token files: {e}")
        sys.exit(1)
    
    # CRITICAL: Set GARMINTOKENS environment variable
    # This tells garminconnect library where to find tokens
    os.environ['GARMINTOKENS'] = TOKEN_DIR
    log(f"Set GARMINTOKENS={TOKEN_DIR}")
    
    log("Token directory setup complete")
    return TOKEN_DIR

def authenticate():
    """
    Authenticate by setting GARMINTOKENS and creating Garmin client
    The library automatically loads tokens when it sees GARMINTOKENS env var
    """
    log("")
    log("Authenticating with Garmin...")
    
    try:
        # Just create the client - it will auto-load from GARMINTOKENS
        client = Garmin()
        log("Created Garmin client")
        
        # Test with an API call to verify authentication works
        log("Testing authentication with API call...")
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            stats = client.get_stats(today)
            log(f"AUTHENTICATION SUCCESSFUL!")
        except Exception as e:
            log(f"ERROR: API test call failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        return client
        
    except Exception as e:
        log(f"Authentication failed: {e}")
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

def save_activity(conn, activity_data):
    """Save activity summary to database"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO activities (
                activity_id, activity_type, start_time, duration_seconds,
                distance_meters, average_hr, max_hr, calories,
                average_speed, max_speed, elevation_gain, elevation_loss
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            activity_data.get('activity_id'),
            activity_data.get('activity_type'),
            activity_data.get('start_time'),
            activity_data.get('duration'),
            activity_data.get('distance'),
            activity_data.get('avg_hr'),
            activity_data.get('max_hr'),
            activity_data.get('calories'),
            activity_data.get('avg_speed'),
            activity_data.get('max_speed'),
            activity_data.get('elevation_gain'),
            activity_data.get('elevation_loss')
        ))
        conn.commit()
        return True
    except Exception as e:
        log(f"Error saving activity {activity_data.get('activity_id')}: {e}")
        return False

def fetch_garmin_data():
    """Main function"""
    log("")
    log("=" * 60)
    log("Starting Garmin Data Sync")
    log("=" * 60)
    log("")
    
    # Setup token directory from environment variable
    token_dir = setup_token_directory()
    
    # Authenticate
    client = authenticate()
    
    log("")
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
            # Get daily stats
            stats = client.get_stats(date_str)
            
            # Get heart rate data
            hr_data = client.get_heart_rates(date_str)
            
            # Get sleep data
            try:
                sleep_data = client.get_sleep_data(date_str)
                sleep_score = sleep_data.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value')
                sleep_duration = sleep_data.get('dailySleepDTO', {}).get('sleepTimeSeconds')
            except:
                sleep_score = None
                sleep_duration = None
            
            # Get body battery
            try:
                body_battery_data = client.get_body_battery(date_str)
                body_battery = body_battery_data[0].get('charged') if body_battery_data else None
            except:
                body_battery = None
            
            # Get respiration
            try:
                respiration_data = client.get_respiration_data(date_str)
                respiration = respiration_data.get('avgWakingRespirationValue')
            except:
                respiration = None
            
            # Get SpO2
            try:
                spo2_data = client.get_pulse_ox(date_str)
                spo2 = spo2_data.get('averageSpo2')
            except:
                spo2 = None
            
            # Compile data
            daily_data = {
                'steps': stats.get('totalSteps'),
                'distance_meters': stats.get('totalDistanceMeters'),
                'resting_hr': hr_data.get('restingHeartRate'),
                'max_hr': hr_data.get('maxHeartRate'),
                'sleep_duration': sleep_duration,
                'sleep_score': sleep_score,
                'body_battery': body_battery,
                'respiration': respiration,
                'spo2': spo2,
                'vo2_max': stats.get('vo2Max')
            }
            
            # Save to database
            if save_daily_health(conn, date_str, daily_data):
                daily_count += 1
                steps = daily_data.get('steps', 0)
                hr = daily_data.get('resting_hr', 'N/A')
                log(f"  {date_str}: {steps:,} steps, HR {hr}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            log(f"  {date_str}: Could not fetch data - {e}")
        
        current_date += timedelta(days=1)
    
    log("")
    log(f"Saved {daily_count} days of health data")
    
    # Fetch activities
    log("")
    log("Fetching activities...")
    activity_count = 0
    
    try:
        activities = client.get_activities(0, 50)
        
        for activity in activities:
            activity_id = str(activity.get('activityId'))
            activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')
            
            activity_data = {
                'activity_id': activity_id,
                'activity_type': activity_type,
                'start_time': activity.get('startTimeLocal'),
                'duration': activity.get('duration'),
                'distance': activity.get('distance'),
                'avg_hr': activity.get('averageHR'),
                'max_hr': activity.get('maxHR'),
                'calories': activity.get('calories'),
                'avg_speed': activity.get('averageSpeed'),
                'max_speed': activity.get('maxSpeed'),
                'elevation_gain': activity.get('elevationGain'),
                'elevation_loss': activity.get('elevationLoss')
            }
            
            if save_activity(conn, activity_data):
                activity_count += 1
                distance_km = round(activity.get('distance', 0) / 1000, 2) if activity.get('distance') else 0
                log(f"  {activity_type} - {activity.get('startTimeLocal', '')} - {distance_km}km")
            
            time.sleep(0.5)
    
    except Exception as e:
        log(f"Error fetching activities: {e}")
    
    log("")
    log(f"Saved {activity_count} activities")
    
    # Close database
    conn.close()
    
    log("")
    log("=" * 60)
    log("Sync Complete!")
    log(f"   {daily_count} days of health data")
    log(f"   {activity_count} activities")
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
