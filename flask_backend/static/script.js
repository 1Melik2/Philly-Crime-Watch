async function loadCrimeData() {
	const response = await fetch('/api/crime');
	const data = await response.json();

	// Show data in  list
	const list = document.getElementById('crime-list');
	list.innerHTML = '';
	data.forEach((crime) => {
		const item = document.createElement('li');
		item.textContent = `${crime.text_general_code} — ${crime.count} incidents`;
		list.appendChild(item);
	});

	// Get crime label and number of specific crime from data
	const labels = data.map((crime) => crime.text_general_code);
	const counts = data.map((crime) => crime.count);

	// Create the chart
	const ctx = document.getElementById('crimeChart').getContext('2d');
	new Chart(ctx, {
		type: 'bar',
		data: {
			labels: labels,
			datasets: [
				{
					label: 'Top 5 Crimes (Past 30 Days)',
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
				y: {
					beginAtZero: true,
				},
			},
		},
	});
}

document.addEventListener('DOMContentLoaded', loadCrimeData);
