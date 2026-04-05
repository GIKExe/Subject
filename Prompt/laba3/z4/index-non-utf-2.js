// Глобальная переменная для хранения экземпляра чарта
let distributionChart = null;

document.getElementById('generate-btn').addEventListener('click', () => {
	const muInput = document.getElementById('mu-input');
	const sigmaInput = document.getElementById('sigma-input');
	const errorBlock = document.getElementById('error-message');
	
	// 1. Предварительная очистка ошибок перед новой итерацией
	errorBlock.textContent = '';
	errorBlock.hidden = true;

	const mu = parseFloat(muInput.value);
	const sigma = parseFloat(sigmaInput.value);

	// 2. Валидация полей
	if (isNaN(mu) || isNaN(sigma)) {
		showError('Пожалуйста, заполните оба поля корректными числами.');
		return;
	}

	if (sigma <= 0) {
		showError('Стандартное отклонение (?) должно быть больше 0.');
		return;
	}

	// 3. Предупреждение о слишком большом ?
	if (sigma > 1000) {
		console.warn('Внимание: Высокое значение ? (>1000) может сделать гистограмму неинформативной из-за огромного разброса данных.');
		// Можно также вывести мягкое предупреждение в UI, не блокируя выполнение
		showError('Предупреждение: При ? > 1000 график может выглядеть слишком плоским.');
	}

	// 4. Генерация данных (Бокс-Мюллер)
	const samples = 10000;
	const data = [];
	for (let i = 0; i < samples; i++) {
		data.push(generateNormal(mu, sigma));
	}

	// 5. Подготовка данных с защитой от нулевого диапазона
	const binCount = 40;
	const histogramData = prepareHistogramData(data, mu, sigma, binCount);
	
	if (histogramData) {
		renderChart(histogramData.labels, histogramData.counts, histogramData.theoretical);
	}
});

function generateNormal(mu, sigma) {
	let u = 0, v = 0;
	while (u === 0) u = Math.random(); 
	while (v === 0) v = Math.random();
	const z0 = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
	return z0 * sigma + mu;
}

function prepareHistogramData(data, mu, sigma, binCount) {
	const min = Math.min(...data);
	const max = Math.max(...data);
	let range = max - min;
	
	// ЗАЩИТА: Если все числа совпали (range === 0)
	if (range === 0) {
		console.error('Ошибка вычисления: диапазон данных равен 0 (все числа идентичны). Установлено значение по умолчанию.');
		range = 1; 
	}

	const binWidth = range / binCount;
	const bins = new Array(binCount).fill(0);
	const labels = [];
	const theoreticalPoints = [];

	data.forEach(val => {
		let index = Math.floor((val - min) / binWidth);
		if (index >= binCount) index = binCount - 1;
		bins[index]++;
	});

	for (let i = 0; i < binCount; i++) {
		const x = min + (i + 0.5) * binWidth;
		labels.push(x.toFixed(2));

		const exponent = Math.exp(-Math.pow(x - mu, 2) / (2 * Math.pow(sigma, 2)));
		const pdf = (1 / (sigma * Math.sqrt(2 * Math.PI))) * exponent;
		theoreticalPoints.push(pdf * data.length * binWidth);
	}

	return { labels, counts: bins, theoretical: theoreticalPoints };
}

function renderChart(labels, counts, theoretical) {
	const ctx = document.getElementById('distribution-chart').getContext('2d');
	if (distributionChart) {
		distributionChart.destroy();
	}

	distributionChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: labels,
			datasets: [
				{
					label: 'Гистограмма (10к чисел)',
					data: counts,
					backgroundColor: 'rgba(46, 204, 113, 0.4)',
					borderColor: '#2ecc71',
					borderWidth: 1,
					barPercentage: 1,
					categoryPercentage: 1,
					order: 2
				},
				{
					label: 'Теоретическая кривая',
					data: theoretical,
					type: 'line',
					borderColor: '#ffffff',
					borderWidth: 2,
					pointRadius: 0,
					fill: false,
					tension: 0.4,
					order: 1
				}
			]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: { labels: { color: '#ffffff' } }
			},
			scales: {
				x: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
				y: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
			}
		}
	});
}

function showError(text) {
	const errorBlock = document.getElementById('error-message');
	errorBlock.textContent = text;
	errorBlock.hidden = false;
}