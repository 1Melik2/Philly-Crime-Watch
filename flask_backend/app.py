from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/crime')
def crime_data():
    # get "days" query parameter from the frontend (default: 1)
    days = request.args.get('days', default=1, type=int)

    # dynamically insert the days into the SQL query
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
    crimes = data.get('rows', [])
    return jsonify(crimes)

@app.route('/api/latest')
def latest_crime():
    # Get the most recent incident that actually has data (not null)
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
def neighborhood_count():
    # Get count of distinct neighborhoods (PSA = Police Service Area)
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