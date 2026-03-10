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

# --- Crime Statistics API (from main) ---

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
        return jsonify({'error': 'Failed to fetch data'}), 500
    data = response.json()
    return jsonify(data.get('rows', []))

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
        return jsonify({"error": "Failed to fetch data"}), 500
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
        return jsonify({'error': 'Failed to fetch latest crime'}), 500
    data = response.json()
    rows = data.get('rows', [])
    if rows:
        crime = rows[0]
        return jsonify({
            "type": crime.get("text_general_code", "Unknown"),
            "time": crime.get("dispatch_date_time", "Unknown"),
            "block": crime.get("location_block", "Unknown")
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
        return jsonify({'error': 'Failed to fetch neighborhood data'}), 500
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
        return jsonify({'error': 'Failed to fetch data'}), 500
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
        return jsonify({"error": "Failed to fetch data"}), 500
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
