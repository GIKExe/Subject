// Глобальная переменная для хранения экземпляра чарта
let distributionChart = null;

document.getElementById('generate-btn').addEventListener('click', () => {
	const muInput = document.getElementById('mu-input');
	const sigmaInput = document.getElementById('sigma-input');
	const errorBlock = document.getElementById('error-message');
	
	// 1. Валидация
	const mu = parseFloat(muInput.value);
	const sigma = parseFloat(sigmaInput.value);

	if (isNaN(mu) || isNaN(sigma)) {
		showError('Пожалуйста, заполните оба поля корректными числами.');
		return;
	}

	if (sigma <= 0) {
		showError('Стандартное отклонение (?) должно быть больше 0.');
		return;
	}

	errorBlock.hidden = true; // Скрываем ошибки, если всё ок

	// 2. Генерация данных (Бокс-Мюллер)
	const samples = 10000;
	const data = [];
	for (let i = 0; i < samples; i++) {
		data.push(generateNormal(mu, sigma));
	}

	// 3. Подготовка данных для гистограммы (Bins)
	const binCount = 40;
	const { labels, counts, theoretical } = prepareHistogramData(data, mu, sigma, binCount);

	// 4. Отрисовка
	renderChart(labels, counts, theoretical);
});

/**
 * Преобразование Бокса — Мюллера
 */
function generateNormal(mu, sigma) {
	let u = 0, v = 0;
	while (u === 0) u = Math.random(); 
	while (v === 0) v = Math.random();
	
	// Стандартное нормальное распределение
	const z0 = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
	
	// Масштабирование под заданные параметры
	return z0 * sigma + mu;
}

/**
 * Группировка данных по столбцам и расчет теории
 */
function prepareHistogramData(data, mu, sigma, binCount) {
	const min = Math.min(...data);
	const max = Math.max(...data);
	const range = max - min;
	const binWidth = range / binCount;
	
	const bins = new Array(binCount).fill(0);
	const labels = [];

	// Наполняем корзины
	data.forEach(val => {
		let index = Math.floor((val - min) / binWidth);
		if (index >= binCount) index = binCount - 1;
		bins[index]++;
	});

	const theoreticalPoints = [];
	for (let i = 0; i < binCount; i++) {
		const x = min + (i + 0.5) * binWidth;
		labels.push(x.toFixed(2));

		// Формула плотности вероятности нормального распределения
		const exponent = Math.exp(-Math.pow(x - mu, 2) / (2 * Math.pow(sigma, 2)));
		const pdf = (1 / (sigma * Math.sqrt(2 * Math.PI))) * exponent;
		
		// Масштабируем теорию под количество образцов и ширину корзины
		theoreticalPoints.push(pdf * data.length * binWidth);
	}

	return { labels, counts: bins, theoretical: theoreticalPoints };
}

/**
 * Инициализация или обновление Chart.js
 */
function renderChart(labels, counts, theoretical) {
	const ctx = document.getElementById('distribution-chart').getContext('2d');

	// Удаляем старый график, если он есть
	if (distributionChart) {
		distributionChart.destroy();
	}

	distributionChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: labels,
			datasets: [
				{
					label: 'Частота (Гистограмма)',
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
			scales: {
				x: {
					ticks: { color: '#b3b3b3', maxRotation: 45 },
					grid: { color: 'rgba(255, 255, 255, 0.05)' }
				},
				y: {
					ticks: { color: '#b3b3b3' },
					grid: { color: 'rgba(255, 255, 255, 0.05)' }
				}
			},
			plugins: {
				legend: {
					labels: { color: '#ffffff' }
				}
			}
		}
	});
}

function showError(text) {
	const errorBlock = document.getElementById('error-message');
	errorBlock.textContent = text;
	errorBlock.hidden = false;
}