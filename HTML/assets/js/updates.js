async function loadLatestCrime(days = 1) {
	try {
		const response = await fetch(`http://127.0.0.1:5000/api/latest`);

		if (!response.ok) {
			throw new Error('Network response was not ok');
		}

		const data = await response.json();

		const elem = document.getElementById('latest-crime');
		if (data && data.type) {
			elem.textContent = `${data.type} at ${data.block} at ${data.time}`;
		} else {
			elem.textContent = 'No data available.';
		}
	} catch (error) {
		console.error('Error loading latest crime:', error);
		const elem = document.getElementById('latest-crime');
		elem.textContent = 'Error loading crime data.';
	}
}

async function loadMonthlyCrimes() {
	try {
		// Fetch crime data for last 30 days
		const response = await fetch(`http://127.0.0.1:5000/api/crime?days=30`);

		if (!response.ok) {
			throw new Error('Network response was not ok');
		}

		const data = await response.json();

		// Sum up all the counts
		const totalCrimes = data.reduce((sum, crime) => sum + crime.count, 0);

		// Update the HTML
		const elem = document.getElementById('monthly-crimes');
		if (elem) {
			elem.innerHTML = `<strong>${totalCrimes}</strong> incidents reported`;
		}
	} catch (error) {
		console.error('Error loading monthly crimes:', error);
	}
}

async function loadNeighborhoodCount() {
	try {
		const response = await fetch(`http://127.0.0.1:5000/api/neighborhoods`);

		if (!response.ok) {
			throw new Error('Network response was not ok');
		}

		const data = await response.json();

		const elem = document.getElementById('neighborhood-count');
		if (elem) {
			elem.innerHTML = `<strong>${data.count}</strong> active areas`;
		}
	} catch (error) {
		console.error('Error loading neighborhood count:', error);
	}
}

// Call it on page load
document.addEventListener('DOMContentLoaded', () => {
	loadLatestCrime(1);
	loadMonthlyCrimes();
	loadNeighborhoodCount();

	setInterval(loadLatestCrime, 60000, 1);
	setInterval(loadMonthlyCrimes, 60000);
});
