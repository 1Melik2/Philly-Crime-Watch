from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/crime')
def crime_data():
    url = ("https://phl.carto.com/api/v2/sql?"
           "q=SELECT text_general_code, COUNT(*) as count "
           "FROM incidents_part1_part2 "
           "WHERE dispatch_date_time >= NOW() - INTERVAL '30 days' "
           "GROUP BY text_general_code "
           "ORDER BY count DESC "
           "LIMIT 5")
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data'}), 500

    data = response.json()
    crimes = data.get('rows', [])
    return jsonify(crimes)

if __name__ == "__main__":
    app.run(debug=True)
