let crimeMarkers = [];

async function loadCrimeMarkers(days = 3) {
	try {
		console.log(`Fetching crime data for last ${days} day(s)...`);
		const response = await fetch(
			`http://127.0.0.1:5000/api/crime_locations?days=${days}`
		);

		if (!response.ok) {
			console.error(`HTTP Error: ${response.status} ${response.statusText}`);
			return;
		}

		const crimes = await response.json();

		// Log the raw response
		console.log('Raw API Response:', crimes);
		console.log(`Total crimes received: ${crimes.length}`);

		// Remove existing markers
		crimeMarkers.forEach((marker) => map.removeLayer(marker));
		crimeMarkers = [];

		// Log each crime with its coordinates
		crimes.forEach((crime, index) => {
			console.log(`Crime #${index + 1}:`, {
				type: crime.text_general_code,
				latitude: crime.lat,
				longitude: crime.lon,
				date: crime.dispatch_date_time,
				hasValidCoords: !!(crime.lat && crime.lon),
			});

			// Skip if missing coordinates or invalid
			if (
				!crime.lat ||
				!crime.lon ||
				crime.lat === null ||
				crime.lon === null
			) {
				console.warn(`Crime #${index + 1} missing coordinates:`, crime);
				return;
			}

			// Create marker
			const marker = L.circleMarker([crime.lat, crime.lon], {
				radius: 5,
				color: 'red',
				fillColor: '#f03',
				fillOpacity: 0.6,
			}).addTo(map);

			marker.bindPopup(`
				<b>${crime.text_general_code || 'Unknown'}</b><br>
				Date: ${crime.dispatch_date_time || 'N/A'}<br>
				Lat: ${crime.lat}<br>
				Lon: ${crime.lon}
			`);

			crimeMarkers.push(marker);
		});

		console.log(
			`Successfully loaded ${crimeMarkers.length} crime markers on map`
		);
		console.log(
			`Skipped ${
				crimes.length - crimeMarkers.length
			} crimes due to missing coordinates`
		);
	} catch (error) {
		console.error('Error loading crime markers:', error);
	}
}

document.addEventListener('DOMContentLoaded', () => {
	console.log('DOM loaded, initializing crime data...');
	loadCrimeMarkers(3);

	// Refresh every 30 mins
	setInterval(() => {
		console.log('Auto-refreshing crime data...');
		loadCrimeMarkers(3);
	}, 1860000);
});
