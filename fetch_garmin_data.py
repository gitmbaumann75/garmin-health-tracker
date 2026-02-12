"""
Garmin Data Fetcher
This script logs into Garmin and downloads your health data
It runs automatically every day via Render's cron job
"""

from garminconnect import Garmin
from datetime import datetime, timedelta
import sqlite3
import os
import sys
import time

# Get Garmin credentials from environment variables (for security)
GARMIN_EMAIL = os.environ.get('GARMIN_EMAIL')
GARMIN_PASSWORD = os.environ.get('GARMIN_PASSWORD')

# Database file
DATABASE = 'health.db'

# How many days back to fetch (90 days for initial sync)
DAYS_TO_FETCH = int(os.environ.get('DAYS_TO_FETCH', '90'))

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

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

def save_activity_heart_rate(conn, activity_id, hr_data):
    """Save detailed heart rate data for an activity"""
    cursor = conn.cursor()
    
    try:
        # Delete existing data for this activity
        cursor.execute('DELETE FROM activity_heart_rate WHERE activity_id = ?', (activity_id,))
        
        # Insert new data
        for data_point in hr_data:
            cursor.execute('''
                INSERT INTO activity_heart_rate (activity_id, timestamp, heart_rate)
                VALUES (?, ?, ?)
            ''', (activity_id, data_point['timestamp'], data_point['hr']))
        
        conn.commit()
        return True
    except Exception as e:
        log(f"Error saving heart rate data for activity {activity_id}: {e}")
        return False

def save_sport_metrics(conn, activity_id, metrics):
    """Save sport-specific metrics"""
    cursor = conn.cursor()
    
    try:
        # Delete existing metrics for this activity
        cursor.execute('DELETE FROM sport_metrics WHERE activity_id = ?', (activity_id,))
        
        # Insert new metrics
        for metric_name, metric_value in metrics.items():
            cursor.execute('''
                INSERT INTO sport_metrics (activity_id, metric_name, metric_value)
                VALUES (?, ?, ?)
            ''', (activity_id, metric_name, metric_value))
        
        conn.commit()
        return True
    except Exception as e:
        log(f"Error saving sport metrics for activity {activity_id}: {e}")
        return False

def fetch_garmin_data():
    """Main function to fetch data from Garmin"""
    
    # Check credentials
    if not GARMIN_EMAIL or not GARMIN_PASSWORD:
        log("❌ ERROR: GARMIN_EMAIL and GARMIN_PASSWORD environment variables must be set!")
        sys.exit(1)
    
    log("=" * 60)
    log("Starting Garmin Data Sync")
    log("=" * 60)
    
    # Login to Garmin
    log("🔄 Connecting to Garmin Connect...")
    try:
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        log("✅ Logged in successfully!")
    except Exception as e:
        log(f"❌ Login failed: {e}")
        sys.exit(1)
    
    # Connect to database
    conn = get_db_connection()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TO_FETCH)
    
    log(f"📅 Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Fetch daily health data
    log("\n📊 Fetching daily health metrics...")
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
                log(f"  ✓ {date_str}: {daily_data.get('steps', 0)} steps, HR {daily_data.get('resting_hr', 'N/A')}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            log(f"  ⚠️  {date_str}: Could not fetch data - {e}")
        
        current_date += timedelta(days=1)
    
    log(f"✅ Saved {daily_count} days of health data")
    
    # Fetch activities
    log("\n🏃 Fetching activities...")
    activity_count = 0
    hr_detail_count = 0
    
    try:
        # Get activities for the date range
        activities = client.get_activities(0, 100)  # Get last 100 activities
        
        for activity in activities:
            activity_id = str(activity.get('activityId'))
            activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')
            
            # Get activity details
            try:
                details = client.get_activity(activity_id)
                
                # Prepare activity data
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
                
                # Save activity
                if save_activity(conn, activity_data):
                    activity_count += 1
                    log(f"  ✓ {activity_type} - {activity.get('startTimeLocal', '')} - {round(activity.get('distance', 0)/1000, 2)}km")
                
                # Get detailed heart rate data (second-by-second if available)
                try:
                    hr_detail = client.get_activity_hr_in_timezones(activity_id)
                    
                    # Parse heart rate data
                    hr_data_points = []
                    if hr_detail and 'heartRateValues' in hr_detail:
                        for hr_entry in hr_detail['heartRateValues']:
                            if hr_entry:
                                for timestamp, hr_value in hr_entry:
                                    if hr_value:
                                        hr_data_points.append({
                                            'timestamp': timestamp,
                                            'hr': hr_value
                                        })
                    
                    if hr_data_points:
                        save_activity_heart_rate(conn, activity_id, hr_data_points)
                        hr_detail_count += 1
                        log(f"    → Saved {len(hr_data_points)} heart rate data points")
                
                except Exception as e:
                    log(f"    ⚠️  Could not fetch HR detail: {e}")
                
                # Extract sport-specific metrics
                sport_metrics = {}
                
                # Swimming metrics
                if 'lap_swimming' in activity_type.lower() or 'open_water' in activity_type.lower():
                    sport_metrics['strokes'] = details.get('strokes')
                    sport_metrics['avg_stroke_distance'] = details.get('avgStrokeDistance')
                    sport_metrics['swolf'] = details.get('swolfAverage')
                
                # Cycling metrics
                if 'cycling' in activity_type.lower():
                    sport_metrics['avg_cadence'] = details.get('averageBikingCadenceInRevPerMinute')
                    sport_metrics['max_cadence'] = details.get('maxBikingCadenceInRevPerMinute')
                    sport_metrics['avg_power'] = details.get('avgPower')
                
                # Rowing metrics
                if 'rowing' in activity_type.lower():
                    sport_metrics['avg_stroke_rate'] = details.get('averageStrokeRate')
                    sport_metrics['max_stroke_rate'] = details.get('maxStrokeRate')
                
                if sport_metrics:
                    save_sport_metrics(conn, activity_id, sport_metrics)
                    log(f"    → Saved {len(sport_metrics)} sport-specific metrics")
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                log(f"  ⚠️  Could not fetch details for activity {activity_id}: {e}")
    
    except Exception as e:
        log(f"❌ Error fetching activities: {e}")
    
    log(f"✅ Saved {activity_count} activities with {hr_detail_count} detailed HR datasets")
    
    # Close database connection
    conn.close()
    
    log("\n" + "=" * 60)
    log("✨ Sync Complete!")
    log(f"   • {daily_count} days of health data")
    log(f"   • {activity_count} activities")
    log(f"   • {hr_detail_count} detailed heart rate datasets")
    log("=" * 60)

if __name__ == '__main__':
    fetch_garmin_data()
