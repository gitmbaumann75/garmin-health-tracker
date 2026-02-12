"""
Garmin Health Tracker - Main Web Application
This file runs your web server and displays your health data
"""

from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database file location
DATABASE = 'health.db'

def get_db_connection():
    """Connect to the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn

def init_db():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for daily health metrics
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
    
    # Table for activities
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
    
    # Table for detailed heart rate data during activities
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_heart_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            heart_rate INTEGER,
            FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
        )
    ''')
    
    # Table for sport-specific metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sport_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id TEXT NOT NULL,
            metric_name TEXT,
            metric_value REAL,
            FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when app starts
init_db()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/daily-stats')
def get_daily_stats():
    """API endpoint to get last 30 days of daily health data"""
    conn = get_db_connection()
    
    # Get last 30 days of data
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    daily_data = conn.execute('''
        SELECT * FROM daily_health 
        WHERE date >= ? 
        ORDER BY date DESC
    ''', (thirty_days_ago,)).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for row in daily_data:
        result.append({
            'date': row['date'],
            'steps': row['steps'],
            'distance_km': round(row['distance_meters'] / 1000, 2) if row['distance_meters'] else 0,
            'resting_hr': row['resting_heart_rate'],
            'max_hr': row['max_heart_rate'],
            'sleep_hours': round(row['sleep_duration_seconds'] / 3600, 1) if row['sleep_duration_seconds'] else 0,
            'sleep_score': row['sleep_score'],
            'body_battery': row['body_battery'],
            'respiration': row['respiration_rate'],
            'spo2': row['spo2_avg'],
            'vo2_max': row['vo2_max']
        })
    
    return jsonify(result)

@app.route('/api/recent-activities')
def get_recent_activities():
    """API endpoint to get last 20 activities"""
    conn = get_db_connection()
    
    activities = conn.execute('''
        SELECT * FROM activities 
        ORDER BY start_time DESC 
        LIMIT 20
    ''').fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for row in activities:
        result.append({
            'id': row['activity_id'],
            'type': row['activity_type'],
            'start_time': row['start_time'],
            'duration_minutes': round(row['duration_seconds'] / 60, 1) if row['duration_seconds'] else 0,
            'distance_km': round(row['distance_meters'] / 1000, 2) if row['distance_meters'] else 0,
            'avg_hr': row['average_hr'],
            'max_hr': row['max_hr'],
            'calories': row['calories'],
            'elevation_gain': row['elevation_gain'],
            'elevation_loss': row['elevation_loss']
        })
    
    return jsonify(result)

@app.route('/api/activity-detail/<activity_id>')
def get_activity_detail(activity_id):
    """API endpoint to get detailed heart rate data for a specific activity"""
    conn = get_db_connection()
    
    # Get activity info
    activity = conn.execute('''
        SELECT * FROM activities WHERE activity_id = ?
    ''', (activity_id,)).fetchone()
    
    # Get heart rate data
    hr_data = conn.execute('''
        SELECT timestamp, heart_rate 
        FROM activity_heart_rate 
        WHERE activity_id = ? 
        ORDER BY timestamp
    ''', (activity_id,)).fetchall()
    
    # Get sport-specific metrics
    metrics = conn.execute('''
        SELECT metric_name, metric_value 
        FROM sport_metrics 
        WHERE activity_id = ?
    ''', (activity_id,)).fetchall()
    
    conn.close()
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    result = {
        'activity': dict(activity),
        'heart_rate_data': [{'timestamp': row['timestamp'], 'hr': row['heart_rate']} for row in hr_data],
        'sport_metrics': {row['metric_name']: row['metric_value'] for row in metrics}
    }
    
    return jsonify(result)

@app.route('/api/export-csv')
def export_csv():
    """Export all health data as CSV in wide format (each metric as a column)"""
    import csv
    from io import StringIO
    from flask import make_response
    
    conn = get_db_connection()
    
    # Get all daily health data
    daily_data = conn.execute('''
        SELECT * FROM daily_health 
        ORDER BY date ASC
    ''').fetchall()
    
    # Get all body composition data (if table exists)
    try:
        body_comp_data = conn.execute('''
            SELECT * FROM body_composition 
            ORDER BY date ASC
        ''').fetchall()
        # Convert to dict for easy lookup
        body_comp_dict = {row['date']: row for row in body_comp_data}
    except:
        body_comp_dict = {}
    
    # Calculate daily activity summaries
    activity_summaries = {}
    try:
        activities = conn.execute('''
            SELECT DATE(start_time) as date, 
                   SUM(CASE WHEN average_hr >= 140 THEN duration_seconds ELSE 0 END) as intense_seconds
            FROM activities 
            GROUP BY DATE(start_time)
        ''').fetchall()
        activity_summaries = {row['date']: row['intense_seconds'] for row in activities}
    except:
        pass
    
    conn.close()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header row with all metrics
    writer.writerow([
        'Date',
        'Resting HR (bpm)',
        'Max HR (bpm)',
        'Avg HR (bpm)',
        'HRV (ms)',
        'Pulse Ox (%)',
        'Sleep Duration (hours)',
        'Sleep Score',
        'Weight (kg)',
        'Body Fat (%)',
        'Skeletal Muscle (%)',
        'Minutes Intense Activity',
        'VO2 Max',
        'Steps',
        'Distance (km)',
        'Body Battery',
        'Respiration Rate (breaths/min)',
        'Body Water (%)',
        'Bone Mass (kg)',
        'BMR (kcal)'
    ])
    
    # Write data rows
    for row in daily_data:
        date = row['date']
        
        # Get body comp data for this date if available
        body_comp = body_comp_dict.get(date, {})
        
        # Get activity data for this date
        intense_minutes = round(activity_summaries.get(date, 0) / 60, 1) if activity_summaries.get(date) else ''
        
        # Calculate average HR (placeholder - we'll need to add this to data collection)
        avg_hr = ''  # Will be populated when we add average HR tracking
        
        # Calculate HRV (placeholder - we'll need to add this to data collection)
        hrv = ''  # Will be populated when we add HRV tracking
        
        writer.writerow([
            date,
            row['resting_heart_rate'] if row['resting_heart_rate'] else '',
            row['max_heart_rate'] if row['max_heart_rate'] else '',
            avg_hr,
            hrv,
            row['spo2_avg'] if row['spo2_avg'] else '',
            round(row['sleep_duration_seconds'] / 3600, 1) if row['sleep_duration_seconds'] else '',
            row['sleep_score'] if row['sleep_score'] else '',
            body_comp.get('weight_kg', ''),
            body_comp.get('body_fat_pct', ''),
            round(body_comp.get('skeletal_muscle_kg', 0) / body_comp.get('weight_kg', 1) * 100, 1) if body_comp.get('weight_kg') and body_comp.get('skeletal_muscle_kg') else '',
            intense_minutes,
            row['vo2_max'] if row['vo2_max'] else '',
            row['steps'] if row['steps'] else '',
            round(row['distance_meters'] / 1000, 2) if row['distance_meters'] else '',
            row['body_battery'] if row['body_battery'] else '',
            row['respiration_rate'] if row['respiration_rate'] else '',
            body_comp.get('body_water_pct', ''),
            body_comp.get('bone_mass_kg', ''),
            body_comp.get('bmr_calories', '')
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=health_trends_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

@app.route('/health')
def health_check():
    """Simple health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
