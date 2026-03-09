// Keep chart reference so we can destroy it before re-rendering
let crimeChartInstance = null;
let yearlyChartInstance = null;

function formatDate(date) {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, '0');
	const day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`;
}

// Calculate date ranges based on selected days
function calculateDateRanges(days) {
	const today = new Date();

	// Current period
	const currentEnd = new Date(today);
	const currentStart = new Date(today);
	currentStart.setDate(today.getDate() - days);

	// Previous period (same length before current)
	const previousEnd = new Date(currentStart);
	const previousStart = new Date(currentStart);
	previousStart.setDate(currentStart.getDate() - days);

	return {
		currentStart: formatDate(currentStart),
		currentEnd: formatDate(currentEnd),
		previousStart: formatDate(previousStart),
		previousEnd: formatDate(previousEnd),
	};
}

// Fetch data from Flask
async function fetchCrimeComparison(
	currentStart,
	currentEnd,
	previousStart,
	previousEnd,
	psa = null
) {
	try {
		let url =
			`http://127.0.0.1:5000/api/crime_compare?` +
			`current_start=${currentStart}&` +
			`current_end=${currentEnd}&` +
			`previous_start=${previousStart}&` +
			`previous_end=${previousEnd}`;

		if (psa) {
			url += `&psa=${psa}`;
		}

		const response = await fetch(url);

		if (!response.ok) {
			throw new Error('Failed to fetch comparison data');
		}

		return await response.json();
	} catch (error) {
		console.error('Error fetching comparison data:', error);
		return null;
	}
}

function renderMonthlyForecastChart(data) {
	if (!data || !data.historical || !data.forecast) return;

	const labels = data.historical.map(
		(row) =>
			new Date(row.dispatch_date_time).getFullYear() +
			'-' +
			String(new Date(row.dispatch_date_time).getMonth() + 1).padStart(2, '0')
	);

	// Add forecast label
	labels.push('Next Month');

	const historicalCounts = data.historical.map((row) => row.count);
	const forecastCounts = data.forecast;

	const canvas = document.getElementById('yearlyTrendChart');
	if (!canvas) return;

	const ctx = canvas.getContext('2d');

	if (yearlyChartInstance) {
		yearlyChartInstance.destroy();
	}

	yearlyChartInstance = new Chart(ctx, {
		type: 'line',
		data: {
			labels: labels,
			datasets: [
				{
					label: 'Historical (Last 12 Months)',
					data: historicalCounts.concat([null]),
					tension: 0.3,
				},
				{
					label: 'Forecast (Next Month)',
					data: Array(historicalCounts.length)
						.fill(null)
						.concat(forecastCounts),
					borderDash: [6, 6],
				},
			],
		},
		options: {
			responsive: true,
			scales: {
				y: { beginAtZero: true },
			},
		},
	});
}
function renderYearlyTrendChart(labels, values) {
	const canvas = document.getElementById('yearlyTrendChart');
	if (!canvas) return;

	const ctx = canvas.getContext('2d');

	// Destroy previous yearly chart
	if (yearlyChartInstance) {
		yearlyChartInstance.destroy();
	}

	yearlyChartInstance = new Chart(ctx, {
		type: 'line',
		data: {
			labels: labels,
			datasets: [
				{
					label: 'Total Crimes Per Year',
					data: values,
					tension: 0.3,
				},
			],
		},
		options: {
			responsive: true,
			scales: {
				y: { beginAtZero: true },
			},
		},
	});
}

// Main loader
async function loadComparison(days = 30, psa = null) {
	const ranges = calculateDateRanges(days);
	//wont load chart
	const data = await fetchCrimeComparison(
		ranges.currentStart,
		ranges.currentEnd,
		ranges.previousStart,
		ranges.previousEnd,
		psa
	);
}

async function fetchMonthlyForecast(crimeType) {
	try {
		const response = await fetch(
			`http://127.0.0.1:5000/api/monthly_forecast?crime_type=${crimeType}`
		);

		if (!response.ok) {
			throw new Error('Failed to fetch forecast data');
		}

		return await response.json();
	} catch (error) {
		console.error('Forecast fetch error:', error);
		return null;
	}
}
async function loadMonthlyForecast(crimeType = 'Thefts') {
	const data = await fetchMonthlyForecast(crimeType);
	renderMonthlyForecastChart(data);
}

document.addEventListener('DOMContentLoaded', function () {
	const dropdown = document.getElementById('timeRange');

	// Load default comparison chart
	if (dropdown) {
		loadComparison(parseInt(dropdown.value));

		dropdown.addEventListener('change', function () {
			const selectedDays = parseInt(this.value);
			loadComparison(selectedDays);
		});
	}

	// Load monthly forecast into Yearly Trends section
	loadMonthlyForecast('Thefts');
});
