from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/crime')
def crime_data():
    url = (
        "https://phl.carto.com/api/v2/sql?"
        "q=SELECT dispatch_date_time, text_general_code, location_block "
        "FROM incidents_part1_part2 "
        "ORDER BY dispatch_date_time DESC "
        "LIMIT 50"
    )
    response = requests.get(url).json()
    crimes = response['rows']
    return crimes


if __name__ == "__main__":
    app.run(debug=True)