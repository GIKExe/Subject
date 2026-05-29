import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# =============================================================================
# Этап 1. Инициализация и загрузка данных
# =============================================================================
df_raw = None			# Исходные данные
df_work = None			# Рабочая копия
fig = plt.Figure(figsize=(9, 5.5), dpi=100)
canvas = None
current_chart = "line"
VARIANT_NUMBER = 20

# Настройка шрифтов для кириллицы
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

if not os.path.exists('data.csv'):
	raise FileNotFoundError("Файл data.csv не найден в директории скрипта.")

df_raw = pd.read_csv('data.csv')
print(f"✅ Этап 1: Загружено {df_raw.shape[0]} строк из data.csv")

# =============================================================================
# Этап 2. Предобработка и Feature Engineering + Этап 0 (4 признака)
# =============================================================================
def preprocess_data():
	global df_raw, df_work
	df_work = df_raw.copy()	# Правило 6.3: Изоляция изменений через .copy()

	# 1. Фильтрация по условию варианта
	df_work['turb'] = df_work['turb'].clip(lower=0)				# turb < 0 → 0
	df_work['cl'] = df_work['cl'].clip(lower=0)				# cl < 0 → 0
	df_work['ph'] = df_work['ph'].clip(lower=6.5, upper=8.5)	# pH в норме [6.5; 8.5]

	# 2. Безопасное вычисление производного признака (4 категории по ТЗ)
	df_work['dt'] = pd.to_datetime(df_work['ts'], unit='s')

	df_work['ph_status'] = pd.cut(
		df_work['ph'],
		bins=[0, 6.5, 8.5, 14],
		labels=['ниже нормы', 'норма', 'выше нормы'],
		include_lowest=True
	).astype('category')

	df_work['season'] = pd.cut(
		df_work['dt'].dt.month,
		bins=[0, 3, 6, 9, 12],
		labels=['зима', 'весна', 'лето', 'осень'],
		include_lowest=True
	).astype('category')

	df_work['compliance_flag'] = (
		(df_work['turb'] <= 1.5) &
		df_work['ph'].between(6.5, 8.5) &
		df_work['cl'].between(0.3, 0.5)
	)

	# Окно k=35: Moving avg turb + np.diff(flow)
	df_work = df_work.sort_values(['filter_id', 'ts']).reset_index(drop=True)
	df_work['turb_ma'] = df_work.groupby('filter_id')['turb'].transform(
		lambda x: x.rolling(window=35, min_periods=1).mean()
	)
	df_work['flow_diff'] = df_work.groupby('filter_id')['flow'].transform(
		lambda x: x.diff().prepend(x.iloc[0])
	)

	# 3. Вычисление тренда турбидности (правило 6.6: pd.cut / rolling)
	df_work['turb_diff'] = df_work.groupby('filter_id')['turb_ma'].transform(
		lambda x: x.diff().fillna(0)
	)
	df_work['turb_trend'] = np.sign(df_work['turb_diff']).map({
		-1: 'снижается',
		 0: 'стабильно',
		 1: 'растёт'
	}).astype('category')

	# 4. Оптимизация категориальных полей
	df_work.drop(columns=['dt', 'turb_ma', 'turb_diff'], inplace=True)
	df_work['filter_id'] = df_work['filter_id'].astype('category')

	return df_work

# Сохранение в формат pandas (.parquet - нативный, сжатый, быстрый)
print("⏳ Выполняется предобработка...")
df_work = preprocess_data()
df_work.to_parquet('data_prepared.parquet', index=False)
print(f"💾 Этап 0/2: Данные сохранены в data_prepared.parquet")

# =============================================================================
# Этап 3. Встраивание Figure в Tkinter
# =============================================================================
root = tk.Tk()
root.title(f"Дашборд: Вариант {VARIANT_NUMBER}")
root.geometry("1000x700")
root.configure(bg="#f0f2f5")

plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
toolbar.pack(side=tk.TOP, fill=tk.X)

# =============================================================================
# Этап 4. Функции отрисовки графиков (Seaborn)
# =============================================================================
def clear_figure():
	fig.clear()  # Полная очистка осей перед новой отрисовкой

def plot_line():
	clear_figure()
	ax = fig.add_subplot(111)
	# Правило 6.1: Фильтрация выполняется ДО передачи в Seaborn
	df_plot = df_work.copy()
	sns.lineplot(data=df_plot, x='ts', y='turb', hue='filter_id', ax=ax)
	ax.set_title('Динамика турбидности по фильтрам (Скользящее окно k=35 учтено)')
	fig.tight_layout()
	canvas.draw_idle()

def plot_bar():
	clear_figure()
	ax = fig.add_subplot(111)
	# Правило 6.2: Агрегация выполняется внутри callback
	df_agg = df_work.groupby('filter_id').agg({'turb': 'mean', 'flow': 'max'}).reset_index()
	sns.barplot(data=df_agg, x='filter_id', y='turb', palette='viridis', ax=ax)
	ax.set_title('Средняя турбидность vs Макс. расход по фильтрам')
	fig.tight_layout()
	canvas.draw_idle()

def plot_scatter():
	clear_figure()
	ax = fig.add_subplot(111)
	sns.scatterplot(data=df_work, x='ph', y='turb', hue='ph_status', style='season', s=80, ax=ax)
	ax.set_title('Зависимость мутности от кислотности (группировка по сезонам и статусу pH)')
	fig.tight_layout()
	canvas.draw_idle()

def plot_heat_map():
	clear_figure()
	ax = fig.add_subplot(111)
	# Правило 6.6: pivot_table() для подготовки матрицы heatmap
	pivot = df_work.pivot_table(values='flow', index='season', columns='ph_status', aggfunc='mean', fill_value=0)
	sns.heatmap(data=pivot, annot=True, cmap='YlGnBu', fmt=".1f", ax=ax)
	ax.set_title('Средний расход воды: Сезоны × Статус pH')
	fig.tight_layout()
	canvas.draw_idle()

# =============================================================================
# Этап 5. Панель управления и интерактивность
# =============================================================================
def set_chart(chart_type):
	global current_chart
	current_chart = chart_type
	refresh_chart()

def refresh_chart():
	if current_chart == "line":
		plot_line()
	elif current_chart == "bar":
		plot_bar()
	elif current_chart == "scatter":
		plot_scatter()
	elif current_chart == "heatmap":
		plot_heat_map()

def refresh_data():
	global df_work
	print("🔄 Пересчёт данных...")
	df_work = preprocess_data()
	refresh_chart()

def export_plot():
	filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
	if filepath:
		fig.savefig(filepath, dpi=300, bbox_inches='tight')
		messagebox.showinfo("Успех", f"График сохранён в:\n{filepath}")

ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Button(ctrl_frame, text="Линейный", command=lambda: set_chart('line'), width=14).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=lambda: set_chart('bar'), width=14).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Точечный", command=lambda: set_chart('scatter'), width=14).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Тепловая", command=lambda: set_chart('heatmap'), width=14).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Обновить", command=refresh_data, width=12, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text="Экспорт", command=export_plot, width=12, bg="#2196F3", fg="white").pack(side=tk.RIGHT, padx=4)

# Инициализация при запуске
refresh_chart()

# =============================================================================
# Запуск событийного цикла GUI
# =============================================================================
print("🚀 Дашборд запущен. Закрытие окна завершит скрипт.")
root.mainloop()