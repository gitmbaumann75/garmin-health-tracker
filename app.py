import os
import io
import csv
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, Response

app = Flask(__name__)

# Database configuration
DATABASE = 'health.db'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create daily health table
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_health (
            date TEXT PRIMARY KEY,
            steps INTEGER,
            distance_meters INTEGER,
            resting_heart_rate INTEGER,
            max_heart_rate INTEGER,
            sleep_duration_seconds INTEGER,
            sleep_score INTEGER,
            body_battery INTEGER,
            respiration_rate INTEGER,
            spo2_avg INTEGER,
            vo2_max REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Receive health data from local sync script"""
    from flask import request
    
    # Verify API secret
    api_secret = request.headers.get('X-API-Secret')
    expected_secret = os.environ.get('API_SECRET', 'my-super-secret-key-12345')
    
    if api_secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'health_data' not in data:
        return jsonify({'error': 'No data provided'}), 400
    
    health_data = data['health_data']
    
    # Insert data into database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    saved_count = 0
    for record in health_data:
        try:
            c.execute('''
                INSERT OR REPLACE INTO daily_health 
                (date, steps, distance_meters, resting_heart_rate, max_heart_rate,
                 sleep_duration_seconds, sleep_score, body_battery, respiration_rate,
                 spo2_avg, vo2_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            print(f"Error saving record: {e}")
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'saved': saved_count})

@app.route('/api/health-data')
def api_health_data():
    """Get health data for specified number of days"""
    from flask import request
    days = int(request.args.get('days', 30))
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM daily_health 
        ORDER BY date DESC 
        LIMIT ?
    ''', (days,))
    
    rows = c.fetchall()
    conn.close()
    
    # Convert to list of dicts with abbreviated field names for dashboard
    data = []
    for row in rows:
        data.append({
            'date': row['date'],
            'steps': row['steps'],
            'distance': row['distance_meters'],
            'resting_hr': row['resting_heart_rate'],
            'max_hr': row['max_heart_rate'],
            'sleep_duration': row['sleep_duration_seconds'],
            'sleep_score': row['sleep_score'],
            'body_battery': row['body_battery'],
            'respiration': row['respiration_rate'],
            'spo2_avg': row['spo2_avg'],
            'vo2_max': row['vo2_max']
        })
    
    return jsonify(data)

@app.route('/api/daily-stats')
def api_daily_stats():
    """Alias for health-data endpoint (for dashboard compatibility)"""
    return api_health_data()

@app.route('/api/export-csv')
def export_csv():
    """Export health data as CSV with Average HR and sleep in hours"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM daily_health 
        ORDER BY date DESC
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return "No data available", 404
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header with Average HR and sleep in hours
    writer.writerow([
        'Date', 'Steps', 'Distance (meters)', 'Resting HR', 'Average HR', 'Max HR',
        'Sleep Duration (hours)', 'Sleep Score', 'Body Battery',
        'Respiration Rate', 'SpO2 Avg', 'VO2 Max'
    ])
    
    # Write data
    for row in rows:
        # Calculate Average HR (average of resting and max)
        avg_hr = None
        if row['resting_heart_rate'] and row['max_heart_rate']:
            avg_hr = round((row['resting_heart_rate'] + row['max_heart_rate']) / 2)
        
        # Convert sleep from seconds to hours
        sleep_hours = None
        if row['sleep_duration_seconds']:
            sleep_hours = round(row['sleep_duration_seconds'] / 3600, 1)
        
        writer.writerow([
            row['date'],
            row['steps'],
            row['distance_meters'],
            row['resting_heart_rate'],
            avg_hr,  # NEW: Average HR column
            row['max_heart_rate'],
            sleep_hours,  # FIXED: Sleep in hours instead of seconds
            row['sleep_score'],
            row['body_battery'],
            row['respiration_rate'],
            row['spo2_avg'],
            row['vo2_max']
        ])
    
    # Generate response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=health_data_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
