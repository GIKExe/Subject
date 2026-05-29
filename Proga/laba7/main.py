import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns


# Этап 1. Инициализация и загрузка данных
df_raw: pd.DataFrame
df_work: pd.DataFrame
fig = plt.Figure(figsize=(9, 5.5), dpi=100) # type: ignore
canvas: FigureCanvasTkAgg
current_chart = "line"
# ________________________Настройка шрифтов для кириллицы__________________
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
# ── Загрузка и диагностика ──
df_raw = pd.read_csv('data.csv')


# Этап 2. Предобработка и Feature Engineering
def preprocess_data():
	df_work = df_raw.copy() # Изолируйте изменения

	# ________________1. Фильтрация по условию варианта________________
	# Векторизованная фильтрация и очистка
	# Предварительная замена NaN/Inf медианами для безопасной работы
	for f in ['turb', 'ph', 'cl', 'flow']:
		col_clean = df_work[f].replace([np.inf, -np.inf], np.nan)
		median_val = col_clean.median()
		df_work[f] = col_clean.fillna(median_val)
	# for f in ['turb', 'ph', 'cl', 'flow']:
	# 	col = df_work[f]
	# 	bad = ~np.isfinite(col)
	# 	if np.any(bad):
	# 		col[bad] = np.nanmedian(col)

	# Очистка согласно заданию (без циклов по строкам)
	df_work['turb'] = df_work['turb'].clip(lower=0)
	df_work['cl'] = df_work['cl'].clip(lower=0)
	df_work['ph'] = df_work['ph'].clip(lower=6.5, upper=8.5)


	# _________________2. Безопасное вычисление производного признака_____
	# Преобразуем timestamp в datetime для работы с датами
	df_work['dt'] = pd.to_datetime(df_work['ts'], unit='s')
	
	# Добавляем признак статуса pH (ниже/выше нормы)
	df_work['ph_status'] = pd.cut(
		df_work['ph'],
		bins=[0, 6.5, 8.5, 14],
		labels=['ниже нормы', 'норма', 'выше нормы'],
		include_lowest=True
	).astype('category')
	
	# Добавляем сезонность по месяцам
	df_work['season'] = pd.cut(
		df_work['dt'].dt.month,
		bins=[0, 3, 6, 9, 12],
		labels=['зима', 'весна', 'лето', 'осень'],
		include_lowest=True
	).astype('category')
	
	# Флаг соответствия всем нормам одновременно
	df_work['compliance_flag'] = (
		(df_work['turb'] <= 1.5) &
		df_work['ph'].between(6.5, 8.5) &
		df_work['cl'].between(0.3, 0.5)
	)

	# Сортируем для корректного расчета трендов по каждому фильтру
	df_work = df_work.sort_values(['filter_id', 'ts']).reset_index(drop=True)
	
	# Считаем скользящее среднее турбидности (окно 35 замеров)
	df_work['turb_ma'] = df_work.groupby('filter_id')['turb'].transform(
		lambda x: x.rolling(window=35, min_periods=1).mean()
	)
	
	# Находим тренд: растет, падает или стабильно
	df_work['turb_diff'] = df_work.groupby('filter_id')['turb_ma'].transform(
		lambda x: x.diff().fillna(0)
	)
	
	df_work['turb_trend'] = np.sign(df_work['turb_diff']).map({ # type: ignore
		-1: 'снижается',
		 0: 'стабильно',
		 1: 'растёт'
	}).astype('category')
	
	# Удаляем технические колонки, которые не нужны в анализе
	df_work.drop(columns=['dt', 'turb_ma', 'turb_diff'], inplace=True)
	
	# Оптимизируем память, переводя ID фильтра в категориальный тип
	df_work['filter_id'] = df_work['filter_id'].astype('category')


	#___________________ 3. Обрезка выбросов (IQR по группам)______________
	grp = df_work.groupby('filter_id')['turb']

	# 1. Векторизованно считаем квантили, границы и медиану для каждой группы
	q1 = grp.transform(lambda x: x.quantile(0.25))
	q3 = grp.transform(lambda x: x.quantile(0.75))
	iqr = q3 - q1
	lower = q1 - 1.5 * iqr
	upper = q3 + 1.5 * iqr
	median = grp.transform('median')

	# 2. Находим выбросы (строгое условие IQR)
	is_outlier = (df_work['turb'] < lower) | (df_work['turb'] > upper)
	# replaced_total = is_outlier.sum()  # Сохраняем счётчик замен

	# 3. Безопасно заменяем выбросы на медиану их группы
	df_work.loc[is_outlier, 'turb'] = median[is_outlier]


	#____________________ 4. Оптимизация категориальных полей_______________
	threshold = 0.01 * len(df_work)

	# 1. Считаем частоту каждого ID
	counts = df_work['filter_id'].value_counts()
	# 2. Находим ID, которые встречаются реже порога
	rare_ids = counts[counts < threshold].index # type: ignore

	# 3. Векторизованно заменяем их на 0
	df_work.loc[df_work['filter_id'].isin(rare_ids), 'filter_id'] = 0

	# 4. Приводим к компактному типу
	df_work['filter_id'] = df_work['filter_id'].astype(np.int16)

	return df_work


# Этап 3. Встраивание Figure в Tkinter
root = tk.Tk()
root.title("Дашборд: Вариант 20")
root.geometry("1000x700")
root.configure(bg="#f0f2f5")
#___________________ Контейнер для графика__________________________
plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
# ____________________Адаптер matplotlib -> Tkinter__________________
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#_________________ Панель инструментов (зум, сохранение, сброс вида)_____
toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
toolbar.pack(side=tk.TOP, fill=tk.X)


# Этап 4. Функции отрисовки графиков
def clear_figure():
	fig.clear() # Полная очистка осей перед новой отрисовкой

def plot_line():
	#_________________Линейный график__________________
	fig.tight_layout()
	canvas.draw_idle() # Асинхронная перерисовка

def plot_bar():
	#_________________Столбчатая диаграмма__________________
	fig.tight_layout()
	canvas.draw_idle()

def plot_scatter():
	#_________________Точечная диаграмма__________________
	fig.tight_layout()
	canvas.draw_idle()

def plot_heat_map():
	#_________________Тепловая карта__________________
	fig.tight_layout()
	canvas.draw_idle()


# Этап 5. Панель управления и интерактивность
def refresh_data():
	global df_work
	df_work = preprocess_data()
	if current_chart == "line":
		plot_line()
	elif current_chart == "bar":
		plot_bar()

def export_plot():
	filepath = filedialog.asksaveasfilename(defaultextension=".png",
	filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
	if filepath:
		fig.savefig(filepath, dpi=300, bbox_inches='tight')

# _____________________Панель кнопок_____________________
ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Button(ctrl_frame, text="Линейный", command=plot_line, width=14).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=plot_bar, width=14).pack(side=tk.LEFT,	padx=4)
tk.Button(ctrl_frame, text="Точечный", command=plot_scatter, width=14).pack(side=tk.LEFT,	padx=4)
tk.Button(ctrl_frame, text="Тепловой", command=plot_heat_map, width=14).pack(side=tk.LEFT,	padx=4)

tk.Button(ctrl_frame, text=" Обновить", command=refresh_data, width=12).pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text=" Экспорт", command=export_plot, width=12).pack(side=tk.RIGHT, padx=4)
	

if __name__ == '__main__':
	df_work = preprocess_data()
	plot_line()
	print(df_work)
	root.mainloop()