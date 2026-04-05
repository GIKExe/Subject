// === ВИЗУАЛИЗАТОР НОРМАЛЬНОГО РАСПРЕДЕЛЕНИЯ ===
// Генерация 10 000 точек · Гистограмма (40 bins) + теоретическая кривая
// Используется метод Бокса – Мюллера

(function() {
    // DOM элементы
    const muInput = document.getElementById('mu-input');
    const sigmaInput = document.getElementById('sigma-input');
    const generateBtn = document.getElementById('generate-btn');
    const errorDiv = document.getElementById('error-message');
    const canvas = document.getElementById('distribution-chart');
    
    let chartInstance = null;   // для уничтожения старого графика
    
    // === 1. Генерация нормальных случайных чисел (Box–Muller) ===
    function generateNormalSamples(mean, stdDev, count) {
        const samples = [];
        // Box–Muller возвращает два независимых стандартных нормальных числа за итерацию
        for (let i = 0; i < count / 2; i++) {
            let u = 0, v = 0;
            // избегаем нулевых значений для логарифма (математическая защита)
            while (u === 0) u = Math.random();
            while (v === 0) v = Math.random();
            
            const z0 = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
            const z1 = Math.sqrt(-2.0 * Math.log(u)) * Math.sin(2.0 * Math.PI * v);
            
            samples.push(mean + stdDev * z0);
            samples.push(mean + stdDev * z1);
        }
        // если count нечётный (но 10000 чётное, оставляем на всякий случай)
        if (count % 2 !== 0) {
            let u = 0, v = 0;
            while (u === 0) u = Math.random();
            while (v === 0) v = Math.random();
            const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
            samples.push(mean + stdDev * z);
        }
        return samples.slice(0, count);
    }
    
    // === 2. Построение гистограммы (40 bins) и теоретической кривой ===
    function buildHistogramAndCurve(data, mean, stdDev, binsCount = 40) {
        if (!data.length) return { labels: [], histogramCounts: [], expectedCounts: [] };
        
        const N = data.length;
        let minVal = Math.min(...data);
        let maxVal = Math.max(...data);
        
        // Доп. защита: если все значения совпадают (binWidth = 0)
        let binWidth = (maxVal - minVal) / binsCount;
        if (binWidth === 0 || !isFinite(binWidth)) {
            console.warn('⚠️ Все сгенерированные числа идентичны. Принудительно расширяем диапазон, binWidth = 1');
            minVal = minVal - 0.5;
            maxVal = maxVal + 0.5;
            binWidth = (maxVal - minVal) / binsCount;
            if (binWidth === 0) binWidth = 1; // крайний случай
        }
        
        // Массив для подсчёта частот
        const counts = new Array(binsCount).fill(0);
        
        // Заполнение гистограммы
        for (let value of data) {
            let idx = Math.floor((value - minVal) / binWidth);
            if (idx === binsCount) idx = binsCount - 1;   // защита от погрешности double
            if (idx >= 0 && idx < binsCount) {
                counts[idx]++;
            }
        }
        
        // Метки (центры интервалов)
        const labels = [];
        const binCenters = [];
        for (let i = 0; i < binsCount; i++) {
            const center = minVal + (i + 0.5) * binWidth;
            binCenters.push(center);
            labels.push(center.toFixed(3));
        }
        
        // === Теоретическая кривая нормального распределения ===
        // Плотность нормального распределения f(x) = (1/(σ√(2π))) * exp(-0.5*((x-μ)/σ)^2)
        // Ожидаемое количество точек в каждом бине = N * binWidth * f(центр)
        const expectedCounts = [];
        const sqrt2pi = Math.sqrt(2 * Math.PI);
        for (let i = 0; i < binsCount; i++) {
            const x = binCenters[i];
            const z = (x - mean) / stdDev;
            const pdf = (1 / (stdDev * sqrt2pi)) * Math.exp(-0.5 * z * z);
            let expected = N * binWidth * pdf;
            expectedCounts.push(expected);
        }
        
        return { labels, histogramCounts: counts, expectedCounts };
    }
    
    // === 3. Отрисовка через Chart.js (уничтожение предыдущего) ===
    function renderChart(labels, histogramData, expectedData, mean, sigma) {
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
        
        const ctx = canvas.getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: `Гистограмма (10 000 точек, μ=${mean}, σ=${sigma})`,
                        data: histogramData,
                        type: 'bar',
                        backgroundColor: 'rgba(76, 217, 100, 0.55)',
                        borderColor: '#4cd964',
                        borderWidth: 1,
                        borderRadius: 6,
                        barPercentage: 0.9,
                        categoryPercentage: 1.0,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Теоретическая кривая нормального распределения',
                        data: expectedData,
                        type: 'line',
                        borderColor: '#ffb347',
                        backgroundColor: 'rgba(255, 180, 71, 0.05)',
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 3,
                        fill: false,
                        tension: 0.3,
                        borderDash: [5, 4],
                        yAxisID: 'y',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#0f0f1a',
                        titleColor: '#e2e8ff',
                        bodyColor: '#b9c7ff',
                        borderColor: '#4cd964',
                        borderWidth: 1
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#cfdfff',
                            font: { size: 12, weight: '500' },
                            boxWidth: 14,
                            padding: 12
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Значение переменной',
                            color: '#9aa9d6',
                            font: { weight: 'bold', size: 12 }
                        },
                        ticks: {
                            color: '#bdc7f0',
                            maxRotation: 45,
                            autoSkip: true,
                            maxTicksLimit: 12
                        },
                        grid: { color: 'rgba(70, 80, 120, 0.2)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Частота (количество точек)',
                            color: '#9aa9d6',
                            font: { weight: 'bold', size: 12 }
                        },
                        ticks: { color: '#bdc7f0', stepSize: 'auto' },
                        grid: { color: 'rgba(70, 80, 120, 0.25)' },
                        beginAtZero: true
                    }
                },
                elements: {
                    bar: { backgroundColor: 'rgba(76, 217, 100, 0.65)' }
                }
            }
        });
    }
    
    // === 4. Валидация, генерация и построение графика ===
    function generateAndPlot() {
        // Очищаем предыдущее сообщение об ошибке
        errorDiv.innerHTML = '';
        
        // Получаем значения
        let muRaw = muInput.value.trim();
        let sigmaRaw = sigmaInput.value.trim();
        
        if (muRaw === '') {
            errorDiv.innerHTML = '❌ Ошибка: поле "Среднее (μ)" не может быть пустым.';
            return;
        }
        if (sigmaRaw === '') {
            errorDiv.innerHTML = '❌ Ошибка: поле "Стандартное отклонение (σ)" не может быть пустым.';
            return;
        }
        
        const mu = parseFloat(muRaw);
        const sigma = parseFloat(sigmaRaw);
        
        if (isNaN(mu)) {
            errorDiv.innerHTML = '❌ Ошибка: среднее (μ) должно быть числом.';
            return;
        }
        if (isNaN(sigma) || sigma <= 0) {
            errorDiv.innerHTML = '❌ Ошибка: стандартное отклонение (σ) должно быть положительным числом (> 0).';
            return;
        }
        
        // Дополнительное предупреждение при очень большом σ
        if (sigma > 1000) {
            errorDiv.innerHTML = '⚠️ Предупреждение: σ > 1000. Гистограмма может быть неинформативной из-за слишком широкого разброса.';
            // продолжаем выполнение (только предупреждение)
        } else {
            // если предупреждения нет, но мог остаться старый текст — оставляем очищенным
            if (errorDiv.innerHTML.includes('⚠️')) errorDiv.innerHTML = '';
        }
        
        // Генерация 10000 нормальных случайных чисел
        const sampleCount = 10000;
        let generatedData;
        try {
            generatedData = generateNormalSamples(mu, sigma, sampleCount);
        } catch (err) {
            errorDiv.innerHTML = '❌ Критическая ошибка при генерации случайных чисел: ' + err.message;
            return;
        }
        
        if (!generatedData.length) {
            errorDiv.innerHTML = '❌ Ошибка генерации: массив данных пуст.';
            return;
        }
        
        // Построение гистограммы с 40 интервалами (bins)
        const bins = 40;
        const { labels, histogramCounts, expectedCounts } = buildHistogramAndCurve(generatedData, mu, sigma, bins);
        
        // Дополнительная проверка на бины (защита от некорректной ширины)
        if (histogramCounts.length === 0 || labels.length === 0) {
            errorDiv.innerHTML = '❌ Ошибка расчёта гистограммы: пустые бины. Попробуйте другие параметры.';
            return;
        }
        
        // Отрисовка графика
        renderChart(labels, histogramCounts, expectedCounts, mu, sigma);
    }
    
    // Обработчик кнопки
    generateBtn.addEventListener('click', () => {
        generateAndPlot();
    });
    
    // Инициализация при загрузке: построить график для значений по умолчанию (μ=0, σ=1)
    window.addEventListener('DOMContentLoaded', () => {
        // Валидация полей по умолчанию: значения уже подставлены (0 и 1)
        generateAndPlot();
    });
    
    // Дополнительно: если пользователь нажал Enter в любом поле, можно тоже строить
    const inputs = [muInput, sigmaInput];
    inputs.forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                generateAndPlot();
            }
        });
    });
})();