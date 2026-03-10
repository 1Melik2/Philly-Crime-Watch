from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests
import asyncio
import os
from dotenv import load_dotenv
from notificationapi_python_server_sdk import notificationapi
from model import monthly_linear_regression

load_dotenv()

app = Flask(__name__, 
            template_folder='../HTML', 
            static_folder='../HTML', 
            static_url_path='')
CORS(app)

# Initialize NotificationAPI
notificationapi.init(
    os.getenv("NOTIFICATIONAPI_CLIENT_ID"), 
    os.getenv("NOTIFICATIONAPI_CLIENT_SECRET")
)

@app.route("/")
def home():
    return render_template("index.html")

# --- Notification Routes ---

@app.route('/send-notification', methods=['POST'])
def send_notification_route():
    try:
        notification_payload = {
            "notificationId": "crime_dashboard",
            "user": {
               "id": "mailemail.761@gmail.com",
               "email": "mailemail.761@gmail.com",
               "number": "+16104158141" 
            },
            "mergeVariables": {
                "comment": "testComment"
            }
        }
        asyncio.run(notificationapi.send(notification_payload))
        return jsonify({
            "success": True,
            "message": "Notification request processed"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# --- Crime Statistics API ---

@app.route('/api/crime')
def crime_data():
    days = request.args.get('days', default=1, type=int)
    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT text_general_code, COUNT(*) as count "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"GROUP BY text_general_code "
        f"ORDER BY count DESC "
        f"LIMIT 10"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data', 'details': response.text}), 500
    data = response.json()
    return jsonify(data.get('rows', []))

@app.route('/api/crime_by_hour')
def crime_by_hour():
    days = request.args.get('days', default=30, type=int)
    query = (
        f"SELECT "
        f"EXTRACT(HOUR FROM dispatch_date_time) as hour, "
        f"COUNT(*) as count "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"AND dispatch_date_time IS NOT NULL "
        f"GROUP BY EXTRACT(HOUR FROM dispatch_date_time) "
        f"ORDER BY hour"
    )
    try:
        response = requests.get("https://phl.carto.com/api/v2/sql", params={'q': query})
        if response.status_code != 200:
            return jsonify({'error': 'Carto API error', 'details': response.text}), 500
        data = response.json()
        return jsonify(data.get('rows', []))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crime_by_day')
def crime_by_day():
    days = request.args.get('days', default=30, type=int)
    # DOW: 0=Sun, 1=Mon, ..., 6=Sat
    query = (
        f"SELECT "
        f"EXTRACT(DOW FROM dispatch_date_time) as day, "
        f"COUNT(*) as count "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"AND dispatch_date_time IS NOT NULL "
        f"GROUP BY EXTRACT(DOW FROM dispatch_date_time) "
        f"ORDER BY day"
    )
    try:
        response = requests.get("https://phl.carto.com/api/v2/sql", params={'q': query})
        if response.status_code != 200:
            return jsonify({'error': 'Carto API error', 'details': response.text}), 500
        data = response.json()
        return jsonify(data.get('rows', []))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crime_violent_ratio')
def crime_violent_ratio():
    days = request.args.get('days', default=30, type=int)
    violent_types = [
        'Robbery Firearm', 'Robbery No Firearm', 'Rape',
        'Aggravated Assault Firearm', 'Aggravated Assault No Firearm',
        'Other Assaults', 'Homicide - Criminal', 'Homicide - Gross Negligence',
        'Homicide - Justifiable'
    ]
    violent_list = ", ".join(f"'{v}'" for v in violent_types)
    query = (
        f"SELECT "
        f"SUM(CASE WHEN text_general_code IN ({violent_list}) THEN 1 ELSE 0 END) as violent, "
        f"SUM(CASE WHEN text_general_code NOT IN ({violent_list}) THEN 1 ELSE 0 END) as non_violent "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"AND dispatch_date_time IS NOT NULL"
    )
    try:
        response = requests.get("https://phl.carto.com/api/v2/sql", params={'q': query})
        if response.status_code != 200:
            return jsonify({'error': 'Carto API error', 'details': response.text}), 500
        data = response.json()
        rows = data.get('rows', [])
        return jsonify(rows[0] if rows else {'violent': 0, 'non_violent': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crime_prediction')
def crime_prediction():
    try:
        query = (
            "SELECT "
            "  DATE_TRUNC('week', dispatch_date_time)::date as week_start, "
            "  COUNT(*) as count "
            "FROM incidents_part1_part2 "
            "WHERE dispatch_date_time >= NOW() - INTERVAL '56 days' "
            "AND dispatch_date_time IS NOT NULL "
            "GROUP BY DATE_TRUNC('week', dispatch_date_time) "
            "ORDER BY week_start"
        )
        response = requests.get("https://phl.carto.com/api/v2/sql", params={'q': query})
        if response.status_code != 200:
            return jsonify({'error': 'Carto API error', 'details': response.text}), 500
        data = response.json()
        rows = data.get('rows', [])
        weeks = [r['week_start'] for r in rows]
        counts = [r['count'] for r in rows]
        if len(counts) >= 2:
            avg_change = sum(counts[i] - counts[i-1] for i in range(1, len(counts))) / (len(counts) - 1)
            predicted = max(0, int(counts[-1] + avg_change))
        else:
            predicted = counts[-1] if counts else 0
        return jsonify({'weeks': weeks, 'counts': counts, 'predicted': predicted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crime_locations')
def crime_locations():
    days = request.args.get('days', default=1, type=int)
    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT "
        f" text_general_code, "
        f" point_x as lon, "
        f" point_y as lat, "
        f" dispatch_date_time "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"LIMIT 500"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data", 'details': response.text}), 500
    data = response.json()
    return jsonify(data.get("rows", []))

@app.route('/api/latest')
def latest_crime():
    url = (
        "https://phl.carto.com/api/v2/sql?"
        "q=SELECT text_general_code, dispatch_date_time, location_block "
        "FROM incidents_part1_part2 "
        "WHERE text_general_code IS NOT NULL "
        "AND dispatch_date_time IS NOT NULL "
        "ORDER BY dispatch_date_time DESC "
        "LIMIT 1"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch latest crime', 'details': response.text}), 500
    data = response.json()
    rows = data.get('rows', [])
    if rows:
        crime = rows[0]
        return jsonify({
            "type": crime.get("type", crime.get("text_general_code", "Unknown")),
            "time": crime.get("time", crime.get("dispatch_date_time", "Unknown")),
            "block": crime.get("block", crime.get("location_block", "Unknown"))
        })
    else:
        return jsonify({'error': 'No data found'}), 404

@app.route('/api/neighborhoods')
def neighborhood_data():
    days = request.args.get('days', default=30, type=int)
    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT "
        f"psa, "
        f"text_general_code, "
        f"dispatch_date_time "
        f"FROM incidents_part1_part2 "
        f"WHERE psa IS NOT NULL "
        f"AND text_general_code IS NOT NULL "
        f"AND dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"ORDER BY dispatch_date_time DESC "
        f"LIMIT 1000"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch neighborhood data', 'details': response.text}), 500
    data = response.json()
    rows = data.get('rows', [])
    return jsonify({
        "neighborhood_count": len(set(row["psa"] for row in rows)),
        "data": rows
    })

@app.route('/api/crime_compare')
def crime_compare():
    current_start = request.args.get('current_start')
    current_end = request.args.get('current_end')
    previous_start = request.args.get('previous_start')
    previous_end = request.args.get('previous_end')
    psa = request.args.get('psa')
    where_conditions = ["text_general_code IS NOT NULL"]
    if psa:
        where_conditions.append(f"psa = '{psa}'")
    where_clause = " AND ".join(where_conditions)
    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT "
        f"text_general_code AS crime_type, "
        f"SUM(CASE WHEN dispatch_date_time BETWEEN '{current_start}' AND '{current_end}' THEN 1 ELSE 0 END) AS current_count, "
        f"SUM(CASE WHEN dispatch_date_time BETWEEN '{previous_start}' AND '{previous_end}' THEN 1 ELSE 0 END) AS previous_count "
        f"FROM incidents_part1_part2 "
        f"WHERE {where_clause} "
        f"GROUP BY text_general_code "
        f"ORDER BY current_count DESC"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data', 'details': response.text}), 500
    data = response.json()
    rows = data.get('rows', [])
    return jsonify({
        "psa": psa if psa else "All",
        "current_period": f"{current_start} to {current_end}",
        "previous_period": f"{previous_start} to {previous_end}",
        "data": rows
    })

@app.route("/api/monthly_forecast")
def monthly_forecast():
    crime_type = request.args.get("crime_type", "Thefts")
    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT dispatch_date_time "
        f"FROM incidents_part1_part2 "
        f"WHERE text_general_code = '{crime_type}' "
        f"AND dispatch_date_time >= NOW() - INTERVAL '3 years'"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data", 'details': response.text}), 500
    data = response.json()
    rows = data.get("rows", [])
    result = monthly_linear_regression(rows)
    if not result:
        return jsonify({"error": "Not enough data"}), 400
    return jsonify(result)

@app.route("/api/contact", methods=["POST"])
def contact_placeholder():
    return jsonify({"success": True, "message": "Message received! We will get back to you soon."}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
