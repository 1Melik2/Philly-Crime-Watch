from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

# CRIME STATISTICS (for your chart)
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

# CRIME LOCATIONS (for map)
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

# LATEST CRIME
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

# NEIGHBORHOODS Tracked
@app.route('/api/neighborhoods')
def neighborhood_count():
    url = (
        "https://phl.carto.com/api/v2/sql?"
        "q=SELECT COUNT(DISTINCT psa) as neighborhood_count "
        "FROM incidents_part1_part2 "
        "WHERE psa IS NOT NULL"
    )
    
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch neighborhood count'}), 500
    
    data = response.json()
    rows = data.get('rows', [])
    
    if rows:
        return jsonify({
            "count": rows[0].get("neighborhood_count", 0)
        })
    else:
        return jsonify({'error': 'No data found'}), 404

if __name__ == "__main__":
    app.run(debug=True)