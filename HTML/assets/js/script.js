let crimeMarkers = [];
let crimeHeatMap = [];
let heatPoints = [];
let crimes;

//Fetch data from python
async function loadCrimeData(days = 10) {
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

		// Log the data from the fetch

		crimes = await response.json();
		console.log('Raw API Response:', crimes);
	} catch (error) {
		console.error('Error loading crime markers:', error);
	}
}

//Create the pins using the data from the fetched data
function createMarker(crimes) {
	crimes.forEach((crime, index) => {
		if (!crime.lat || !crime.lon) {
			console.warn(`Crime #${index + 1} missing coordinates:`, crime);
			return;
		}
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
	});
}

function createHeatMap(crimes) {
	heatPoints = crimes
		.filter((crime) => crime.lat && crime.lon)
		.map((crime) => [crime.lat, crime.lon, 1]);
	L.heatLayer(heatPoints, { radius: 25 }).addTo(map);
	console.log(heatPoints);
}

//remove previous markers/points when the button is clicked or when a function is ran
// add a loading/wait thingy for when data is being fetched, ex. fetching data... or animation

//Load map with pins when page is loaded
document.addEventListener('DOMContentLoaded', () => {
	console.log('DOM loaded, initializing crime data...');
	loadCrimeData(10);

	setInterval(() => {
		console.log('Auto-refreshing crime data...');
		loadCrimeData(10);
	}, 1860000);
});

//Add event listeners to buttons to toggle pins or heatmap
const pins = document
	.getElementById('pinsbtn')
	.addEventListener('click', () => {
		createMarker(crimes);
	});
const heatmap = document
	.getElementById('heatmapbtn')
	.addEventListener('click', () => {
		createHeatMap(crimes);
	});
