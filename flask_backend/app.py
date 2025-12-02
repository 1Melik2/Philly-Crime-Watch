from flask import Flask, jsonify, render_template, request
import requests


app = Flask(__name__)

# ---------------------------------------------------------
# HOME PAGE ROUTE
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------
# CRIME STATISTICS (for your chart)
# /api/crime?days=1
# ---------------------------------------------------------
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
        return jsonify({"error": "Failed to fetch data"}), 500

    data = response.json()
    return jsonify(data.get("rows", []))


# ---------------------------------------------------------
# CRIME LOCATIONS (for your map)
# /api/crime_locations?days=1
# ---------------------------------------------------------
@app.route('/api/crime_locations')
def crime_locations():
    days = request.args.get('days', default=1, type=int)

    url = (
        "https://phl.carto.com/api/v2/sql?"
        f"q=SELECT "
        f"  text_general_code, "
        f"  point_x as lon, "
        f"  point_y as lat, "
        f"  dispatch_date_time "
        f"FROM incidents_part1_part2 "
        f"WHERE dispatch_date_time >= NOW() - INTERVAL '{days} days' "
        f"LIMIT 500"
    )

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data"}), 500

    data = response.json()
    return jsonify(data.get("rows", []))


# ---------------------------------------------------------
# RUN APP
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
