let crimeChart = null;

async function loadCrimeData(days = 1) {
	const response = await fetch(`/api/crime?days=${days}`);
	const data = await response.json();

	// Show data in a list - temp
	const list = document.getElementById('crime-list');
	list.innerHTML = '';
	data.forEach((crime) => {
		const item = document.createElement('li');
		item.textContent = `${crime.text_general_code} — ${crime.count} incidents`;
		list.appendChild(item);
	});

	const labels = data.map((crime) => crime.text_general_code);
	const counts = data.map((crime) => crime.count);

	// Create chart
	if (!crimeChart) {
		const ctx = document.getElementById('crimeChart').getContext('2d');
		crimeChart = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [
					{
						label: `Top Crimes (Past ${days} Days)`,
						data: counts,
						backgroundColor: 'rgba(54, 162, 235, 0.6)',
						borderColor: 'rgba(54, 162, 235, 1)',
						borderWidth: 1,
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
	} else {
		crimeChart.data.labels = labels;
		crimeChart.data.datasets[0].data = counts;
		crimeChart.data.datasets[0].label = `Top Crimes (Past ${days} Days)`;
		crimeChart.update();
	}
}

// Run when page loads
document.addEventListener('DOMContentLoaded', () => {
	loadCrimeData(1);

	// Add event listener for options
	const timeRange = document.getElementById('timeRange');
	timeRange.addEventListener('change', async (e) => {
		const days = e.target.value;
		loadCrimeData(days);
	});
});
