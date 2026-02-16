"""
Garmin Health Tracker - Main Web Application
Now includes API endpoint to receive data from local sync script
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import os
import hashlib
import hmac

app = Flask(__name__)

# Database file location
DATABASE = 'health.db'

# API Security - Simple secret key
API_SECRET = os.environ.get('API_SECRET', 'your-secret-key-change-this')

def get_db_connection():
    """Connect to the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            steps INTEGER,
            distance_meters REAL,
            resting_heart_rate INTEGER,
            max_heart_rate INTEGER,
            sleep_duration_seconds INTEGER,
            sleep_score INTEGER,
            body_battery INTEGER,
            respiration_rate REAL,
            spo2_avg REAL,
            vo2_max REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id TEXT UNIQUE NOT NULL,
            activity_type TEXT,
            start_time TEXT,
            duration_seconds INTEGER,
            distance_meters REAL,
            average_hr INTEGER,
            max_hr INTEGER,
            calories INTEGER,
            average_speed REAL,
            max_speed REAL,
            elevation_gain REAL,
            elevation_loss REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ============================================================================
# API ENDPOINT - Receives data from local sync script
# ============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """
    Receive health data from local sync script
    Expects JSON with 'secret' and 'data' fields
    """
    try:
        # Get JSON data
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No data provided'}), 400
        
        # Verify API secret
        provided_secret = payload.get('secret')
        if not provided_secret or provided_secret != API_SECRET:
            return jsonify({'error': 'Invalid API secret'}), 401
        
        # Get the health data
        health_data = payload.get('data', [])
        
        if not health_data:
            return jsonify({'error': 'No health data in payload'}), 400
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        for record in health_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_health (
                        date, steps, distance_meters, resting_heart_rate, max_heart_rate,
                        sleep_duration_seconds, sleep_score, body_battery, respiration_rate,
                        spo2_avg, vo2_max
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.get('date'),
                    record.get('steps'),
                    record.get('distance_meters'),
                    record.get('resting_heart_rate'),
                    record.get('max_heart_rate'),
                    record.get('sleep_duration_seconds'),
                    record.get('sleep_score'),
                    record.get('body_battery'),
                    record.get('respiration_rate'),
                    record.get('spo2_avg'),
                    record.get('vo2_max')
                ))
                saved_count += 1
            except Exception as e:
                print(f"Error saving record for {record.get('date')}: {e}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Saved {saved_count} records',
            'count': saved_count
        }), 200
        
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DASHBOARD ROUTES (Existing)
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health-data')
def get_health_data():
    """API endpoint to get health data for the dashboard"""
    try:
        # Get timeframe from query params (default: 30 days)
        days = request.args.get('days', default=30, type=int)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_health 
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        # NOTE: Using abbreviated field names to match dashboard expectations
        data = []
        for row in rows:
            data.append({
                'date': row['date'],
                'steps': row['steps'],
                'distance_meters': row['distance_meters'],
                'resting_hr': row['resting_heart_rate'],  # Dashboard expects 'resting_hr'
                'max_hr': row['max_heart_rate'],  # Dashboard expects 'max_hr'
                'sleep_duration': row['sleep_duration_seconds'],
                'sleep_score': row['sleep_score'],
                'body_battery': row['body_battery'],
                'respiration_rate': row['respiration_rate'],
                'spo2_avg': row['spo2_avg'],
                'vo2_max': row['vo2_max']
            })
        
        return jsonify(data)
        
    except Exception as e:
        print(f"Error fetching health data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily-stats')
def get_daily_stats():
    """API endpoint for daily stats (same as health-data, for backward compatibility)"""
    return get_health_data()

@app.route('/api/recent-activities')
def get_recent_activities():
    """API endpoint for recent activities"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM activities 
            ORDER BY start_time DESC
            LIMIT 10
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        activities = []
        for row in rows:
            activities.append({
                'activity_id': row['activity_id'],
                'activity_type': row['activity_type'],
                'start_time': row['start_time'],
                'duration_seconds': row['duration_seconds'],
                'distance_meters': row['distance_meters'],
                'average_hr': row['average_hr'],
                'max_hr': row['max_hr'],
                'calories': row['calories']
            })
        
        return jsonify(activities)
        
    except Exception as e:
        print(f"Error fetching activities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-csv')
def export_csv():
    """Export data as CSV"""
    from flask import make_response
    import csv
    from io import StringIO
    
    try:
        days = request.args.get('days', default=90, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_health 
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Date', 'Steps', 'Distance (meters)', 'Resting HR', 'Max HR',
            'Sleep Duration (seconds)', 'Sleep Score', 'Body Battery',
            'Respiration Rate', 'SpO2 Avg', 'VO2 Max'
        ])
        
        # Data rows
        for row in rows:
            writer.writerow([
                row['date'],
                row['steps'],
                row['distance_meters'],
                row['resting_heart_rate'],
                row['max_heart_rate'],
                row['sleep_duration_seconds'],
                row['sleep_score'],
                row['body_battery'],
                row['respiration_rate'],
                row['spo2_avg'],
                row['vo2_max']
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=garmin_health_data_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
