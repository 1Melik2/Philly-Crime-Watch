from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
