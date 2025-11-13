// Basic Leaflet map setup
const map = L.map('map').setView([39.9526, -75.1652], 12); // Philly coords
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

// Example marker
L.marker([39.9526, -75.1652])
	.addTo(map)
	.bindPopup('Example crime incident in Center City')
	.openPopup();
