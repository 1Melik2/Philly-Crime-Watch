from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/crime')
def crime_data():
    url = "https://phl.carto.com/api/v2/sql?q=SELECT%20dispatch_date_time,%20text_general_code,%20location_block%20FROM%20incidents_part1_part2%20LIMIT%2025"
    response = requests.get(url).json()
    crimes = response['rows']
    return crimes

if __name__ == "__main__":
    app.run(debug=True)