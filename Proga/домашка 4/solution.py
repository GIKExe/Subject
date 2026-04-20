import numpy as np

np.random.seed(2026)
days = 100

# Температура: нормальное распределение + пропуски + отрицательные
temperature = np.random.normal(loc=12, scale=10, size=days).round(1)
'''Генерируется 100 значений из нормального распределения со средним (loc) = 12°C 
и стандартным отклонением (scale) = 10°C.
.round(1) округляет до одного знака после запятой.'''

nan_indices = np.random.choice(days, 5, replace=False)
'''Выбираются 5 случайных индексов (без повторений)'''
temperature[nan_indices] = np.nan

cold_indices = np.random.choice(days, 8, replace=False)
temperature[cold_indices] = np.random.randint(-30, -14, 8)

# Потребление: гамма-распределение + выбросы
consumption = np.random.gamma(shape=2, scale=8, size=days).astype(int)
outlier_indices = np.random.choice(days, 4, replace=False)
consumption[outlier_indices] = np.random.randint(300, 600, 4)

# Тип дня: 0 – рабочий, 1 – выходной
day_type = np.random.choice([0, 1], size=days, p=[0.7, 0.3])
'''Генерируется массив из 100 значений, каждое – либо 0, либо 1.
Вероятность получить 0  = 70%, 1  = 30%'''



# 1. Количество пропусков (NaN) в temperature
nan_count = np.isnan(temperature).sum()
print(f"1. Количество пропусков (NaN): {nan_count}")

# 2. Замена пропусков на медиану (без учёта NaN)
median_temp = np.nanmedian(temperature)
temperature_clean = np.where(np.isnan(temperature), median_temp, temperature)
print("2. После замены пропусков:")
print(f"   Минимум: {temperature_clean.min():.1f}")
print(f"   Максимум: {temperature_clean.max():.1f}")
print(f"   Среднее: {temperature_clean.mean():.2f}")

# 3. Холодные дни (температура ниже -17) – индексы и количество
cold_days_idx = np.where(temperature_clean < -17)[0]
print(f"3. Количество холодных дней: {len(cold_days_idx)}")
print(f"   Индексы холодных дней: {cold_days_idx}")

# 4. Среднее потребление для рабочих дней (day_type == 0) при температуре > 15
mask_work_warm = (day_type == 0) & (temperature_clean > 15)
mean_consumption_work_warm = np.mean(consumption[mask_work_warm])
print(f"4. Среднее потребление для рабочих дней с температурой > 15°C: {mean_consumption_work_warm:.2f}")

# 5. Категории температуры и подсчёт дней в каждой
conditions = [
    temperature_clean < 0,
    (temperature_clean >= 0) & (temperature_clean <= 20),
    temperature_clean > 20
]
choices = ['cold', 'normal', 'warm']
temp_category = np.select(conditions, choices, default='unknown')

unique, counts = np.unique(temp_category, return_counts=True)
print("5. Количество дней по категориям:")
for cat, cnt in zip(unique, counts):
    print(f"   {cat}: {cnt}")

# 6. Среднее потребление для каждой комбинации day_type (0,1) и temp_category
# Преобразуем категории в числовые индексы: cold->0, normal->1, warm->2
cat_index = np.select(conditions, [0, 1, 2], default=-1)
combined = day_type * 3 + cat_index
sums = np.bincount(combined, weights=consumption, minlength=6)
counts = np.bincount(combined, minlength=6)
means = np.divide(sums, counts, out=np.full_like(sums, np.nan, dtype=float), where=counts>0)
result = means.reshape(2, 3)

print("6. Среднее потребление для (тип дня, категория):")
print("   (строки: day_type=0,1; столбцы: cold, normal, warm)")
print(result)