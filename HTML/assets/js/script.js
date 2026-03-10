let crimeMarkers = [];
let heatPoints = [];
let heatLayer = null;
let crimes;

// Filter / view tracking
let currentFilter = 'all';
let currentView = 'pins'; 

const violentCrimes = new Set([
	'Robbery Firearm',
	'Robbery No Firearm',
	'Rape',
	'Aggravated Assault Firearm',
	'Aggravated Assault No Firearm',
	'Other Assaults',
	'Homicide - Criminal',
	'Homicide - Gross Negligence',
	'Homicide - Justifiable',
]);

const crimeSeverity = new Map([
	['Thefts', 0.3],
	['Theft from Vehicle', 0.4],
	['Motor Vehicle Theft', 0.5],
	['DRIVING UNDER THE INFLUENCE', 0.6],
	['Robbery No Firearm', 0.5],
	['Robbery Firearm', 0.8],
	['Burglary Non-Residential', 0.3],
	['Burglary Residential', 0.4],
	['Rape', 1.0],
	['Aggravated Assault No Firearm', 0.9],
	['Aggravated Assault Firearm', 0.8],
	['Other Assaults', 0.7],
	['Arson', 0.7],
	['Other Sex Offenses (Not Commercialized)', 0.8],
	['All Other Offenses', 0.3],
	['Homicide - Criminal', 1.0],
	['Homicide - Gross Negligence', 0.9],
	['Homicide - Justifiable', 0.8],
]);


// Crime filtering helper functions (Violent vs Non-Violent)
function filterByViolence(crimes, filter) {
	if (filter === 'all') return crimes;

	return crimes.filter((crime) => {
		const isViolent = violentCrimes.has(crime.text_general_code);
		return filter === 'violent' ? isViolent : !isViolent;
	});
}

//Fetch data from python
async function loadCrimeData(days = 30) {
	try {
		console.log(`Fetching crime data for last ${days} day(s)...`);
		const response = await fetch(
			`http://127.0.0.1:5000/api/crime_locations?days=${days}`
		);

		if (!response.ok) {
			console.error(`HTTP Error: ${response.status} ${response.statusText}`);
			return;
		}

		crimes = await response.json();
		console.log('Raw API Response:', crimes);
	} catch (error) {
		console.error('Error loading crime markers:', error);
	}
}

//Create the pins using the data from the fetched data
function createMarker(crimes) {
	clearMap();
	crimes.forEach((crime, index) => {
		if (!crime.lat || !crime.lon) return;

		// Determine if the crime is violent or not
const isViolent = violentCrimes.has(crime.text_general_code);
const markerColor = isViolent ? 'red' : 'blue';

const marker = L.circleMarker([crime.lat, crime.lon], {
	radius: 5,
	color: markerColor,     
	fillColor: markerColor,   
	fillOpacity: 0.6,
}).addTo(map);

// Show violent/non-violent in the popup
marker.bindPopup(`
   <b>${crime.text_general_code || 'Unknown'}</b><br>
   Type: ${isViolent ? 'Violent' : 'Non-violent'}<br>
   Date: ${crime.dispatch_date_time || 'N/A'}<br>
   Lat: ${crime.lat}<br>
   Lon: ${crime.lon}
`);

		marker.bindPopup(`
           <b>${crime.text_general_code || 'Unknown'}</b><br>
           Date: ${crime.dispatch_date_time || 'N/A'}<br>
           Lat: ${crime.lat}<br>
           Lon: ${crime.lon}
       `);
		crimeMarkers.push(marker);
	});
}
// create heatmap on the map
function createHeatMap(crimes) {
	clearMap();
	heatPoints = crimes
		.filter((crime) => crime.lat && crime.lon) //filter data from api
		.map((crime) => {
			const intensity = crimeSeverity.get(crime.text_general_code) ?? 0.3;
			return [crime.lat, crime.lon, intensity];
		});
	heatLayer = L.heatLayer(heatPoints, {
		radius: 25,
		blur: 10,
		maxZoom: 17,
	}).addTo(map);
}
// Clear the markers from the map
function clearMarkers() {
	crimeMarkers.forEach((marker) => map.removeLayer(marker));
	crimeMarkers = [];
}
// Clear the heatmap from the  map
function clearHeatMap() {
	if (heatLayer) {
		map.removeLayer(heatLayer);
		heatLayer = null;
	}
	heatPoints = [];
}

function clearMap() {
	clearHeatMap();
	clearMarkers();
}

// Pins / HeatMap button listeners (respect current filter)
document.getElementById('pinsbtn').addEventListener('click', () => {
	currentView = 'pins';
	const filteredCrimes = filterByViolence(crimes, currentFilter);
	createMarker(filteredCrimes);
});

document.getElementById('heatmapbtn').addEventListener('click', () => {
	currentView = 'heatmap';
	const filteredCrimes = filterByViolence(crimes, currentFilter);
	createHeatMap(filteredCrimes);
});

// Dropdown listener for violent / non-violent filter
document.getElementById('crimeFilter').addEventListener('change', (e) => {
	currentFilter = e.target.value;

	if (!crimes || crimes.length === 0) return; // wait until crimes are loaded

	const filteredCrimes = filterByViolence(crimes, currentFilter);

	if (currentView === 'pins') {
		createMarker(filteredCrimes);
	} else if (currentView === 'heatmap') {
		createHeatMap(filteredCrimes);
	}
});

//Load map with pins when page is loaded
document.addEventListener('DOMContentLoaded', () => {
	console.log('DOM loaded, initializing crime data...');
	loadCrimeData(30);

	setInterval(() => {
		console.log('Auto-refreshing crime data...');
		loadCrimeData(30);
	}, 1860000);
});

// --- ZIP CODE SEARCH ADDITIONS ---

async function searchZipCode() {
    const zip = document.getElementById('zipInput').value.trim();
    
    // Validate Philly zip codes
    if (!zip || !zip.startsWith('191')) {
        alert("Please enter a valid Philadelphia Zip Code (e.g., 19104)");
        return;
    }

    try {
        // Fetch coordinates from Nominatim
        const response = await fetch(`https://nominatim.openstreetmap.org/search?postalcode=${zip}&country=US&format=json`);
        const data = await response.json();

        if (data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);

            // Move the map to the found location
            map.setView([lat, lon], 14); 

            // Add a temporary popup to confirm location
            L.popup()
                .setLatLng([lat, lon])
                .setContent(`Viewing Zip Code: ${zip}`)
                .openOn(map);
        } else {
            alert("Zip code not found. Please try another.");
        }
    } catch (error) {
        console.error("Error fetching zip code:", error);
    }
}

// Event Listeners for new UI elements
document.getElementById('searchBtn').addEventListener('click', searchZipCode);

document.getElementById('zipInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchZipCode();
});

document.getElementById('resetBtn').addEventListener('click', () => {
    // Returns map to default Philly view
    map.setView([39.9526, -75.1652], 12);
    document.getElementById('zipInput').value = '';
});