// Initialize the map centered on Philadelphia
var map = L.map('mapid').setView([39.9526, -75.1652], 12);

// Add the OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Fetch recent crime data (limit to 200 for performance)
fetch("https://phl.carto.com/api/v2/sql?q=SELECT text_general_code,dispatch_date,point_x,point_y FROM incidents_part1_part2 WHERE dispatch_date > '2025-10-01' LIMIT 200")
  .then(response => response.json())
  .then(data => {
    data.rows.forEach(crime => {
      // Only plot if coordinates exist
      if (crime.point_y && crime.point_x) {
        const marker = L.circleMarker([crime.point_y, crime.point_x], {
          radius: 5,
          color: 'red',
          fillColor: '#f03',
          fillOpacity: 0.6
        }).addTo(map);

        marker.bindPopup(`
          <b>${crime.text_general_code}</b><br>
          Date: ${crime.dispatch_date}
        `);
      }
    });
  })
  .catch(error => console.error("Error fetching data:", error));
