import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns

from typing import Optional


root = tk.Tk()
root.title("Дашборд: Интерактивный анализ")
root.geometry("1100x750")
root.configure(bg="#f0f2f5")
# ======================== ЭТАП 0-1: ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ========================
# Явное объявление типов для строгой проверки статическими анализаторами
df_raw: Optional[pd.DataFrame] = None
df_work: Optional[pd.DataFrame] = None
fig: plt.Figure 
canvas: Optional[FigureCanvasTkAgg] = None
current_chart: str = "line"

# Переменные состояния для GUI-виджетов
filter_var: tk.StringVar = tk.StringVar(value="Все")
agg_var: tk.StringVar = tk.StringVar(value="mean")

# Настройка шрифтов для корректного отображения кириллицы
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")

def load_data() -> Optional[pd.DataFrame]:
    """Безопасная загрузка CSV с диагностикой."""
    try:
        df = pd.read_csv('data.csv', parse_dates=False)
        if df.empty:
            messagebox.showerror("Ошибка", "Файл data.csv пуст или не найден.")
            return None
        return df
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл data.csv не найден в директории.")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать CSV: {e}")
        return None

# Загрузка данных до создания GUI (блокирующая, но однократная операция)
df_raw = load_data()
if df_raw is None:
    raise SystemExit("Приложение остановлено: данные недоступны.")

# ======================== ЭТАП 2: ПРЕДОБРАБОТКА И FEATURE ENGINEERING ========================
def preprocess_data() -> pd.DataFrame:
    """Векторизованная очистка и обогащение данных. Изолирует изменения через .copy()."""
    if df_raw is None:
        raise ValueError("Исходные данные не загружены.")
        
    df = df_raw.copy()

    # 1. Безопасная замена NaN/Inf медианами
    for col in ['turb', 'ph', 'cl', 'flow']:
        clean_col = df[col].replace([np.inf, -np.inf], np.nan)
        median_val = clean_col.median()
        df[col] = clean_col.fillna(median_val)

    # Ограничение физических диапазонов
    df['turb'] = df['turb'].clip(lower=0)
    df['cl'] = df['cl'].clip(lower=0)
    df['ph'] = df['ph'].clip(lower=6.5, upper=8.5)

    # 2. Feature Engineering
    # Сохраняем dt для временных графиков (не удаляем, как в исходнике)
    df['dt'] = pd.to_datetime(df['ts'], unit='s')

    df['ph_status'] = pd.cut(
        df['ph'], bins=[0, 6.5, 8.5, 14],
        labels=['ниже нормы', 'норма', 'выше нормы']
    ).astype('category')

    df['season'] = pd.cut(
        df['dt'].dt.month, bins=[0, 3, 6, 9, 12],
        labels=['зима', 'весна', 'лето', 'осень']
    ).astype('category')

    df['compliance_flag'] = (
        (df['turb'] <= 1.5) &
        df['ph'].between(6.5, 8.5) &
        df['cl'].between(0.3, 0.5)
    )

    # Сортировка для корректных расчётов трендов
    df = df.sort_values(['filter_id', 'ts']).reset_index(drop=True)

    # Скользящее среднее и тренд (векторизовано через transform)
    df['turb_ma'] = df.groupby('filter_id')['turb'].transform(
        lambda x: x.rolling(window=35, min_periods=1).mean()
    )
    df['turb_diff'] = df.groupby('filter_id')['turb_ma'].transform(lambda x: x.diff().fillna(0))
    df['turb_trend'] = np.sign(df['turb_diff']).map({-1: 'снижается', 0: 'стабильно', 1: 'растёт'}).astype('category')

    # 3. Обрезка выбросов (IQR по группам)
    grp = df.groupby('filter_id')['turb']
    q1 = grp.transform(lambda x: x.quantile(0.25))
    q3 = grp.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    median_grp = grp.transform('median')

    is_outlier = (df['turb'] < lower_bound) | (df['turb'] > upper_bound)
    df.loc[is_outlier, 'turb'] = median_grp[is_outlier]

    # 4. Оптимизация категориальных полей
    threshold = int(0.01 * len(df))
    counts = df['filter_id'].value_counts()
    rare_ids = counts[counts < threshold].index
    df.loc[df['filter_id'].isin(rare_ids), 'filter_id'] = 0

    # Приведение типов для экономии памяти
    df['filter_id'] = df['filter_id'].astype('category')
    df['dt'] = df['dt'].astype('datetime64[ns]')
    
    return df

# ======================== ЭТАП 3: ВСТРАИВАНИЕ FIGURE В TKINTER ========================
# Контейнер для графика
plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Инициализация фигуры Matplotlib
fig = plt.Figure(figsize=(9, 5.5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Панель инструментов (Zoom, Pan, Save, Reset)
toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
toolbar.pack(side=tk.TOP, fill=tk.X)

# ======================== ЭТАП 4: ФУНКЦИИ ОТРИСОВКИ (SEABORN) ========================
def clear_figure() -> plt.Axes:
    """Безопасная очистка фигуры и создание новой области рисования."""
    fig.clear()
    return fig.add_subplot(111)

def plot_line() -> None:
    """Линейный график: динамика турбидности по времени с агрегацией по дням."""
    ax = clear_figure()
    df_plot = df_work.copy()
    if df_plot.empty: return
    
    # Агрегация по дням для снижения шума и повышения производительности отрисовки
    df_plot['date'] = df_plot['dt'].dt.date
    agg_df = df_plot.groupby(['date', 'filter_id'])['turb'].mean().reset_index()
    
    sns.lineplot(data=agg_df, x='date', y='turb', hue='filter_id', ax=ax, 
                 marker='o', markersize=4, linewidth=1.5)
    ax.set_title("Динамика турбидности по времени (среднесуточная)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Турбидность (NTU)")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    fig.autofmt_xdate()
    fig.tight_layout()
    canvas.draw_idle()  # Асинхронная перерисовка без блокировки GUI

def plot_bar() -> None:
    """Столбчатая диаграмма: агрегация по сезонам с динамическим выбором метрики."""
    ax = clear_figure()
    df_plot = df_work.copy()
    if df_plot.empty: return
    
    # Применение выбранной агрегации из RadioButtons
    agg_method = agg_var.get()
    agg_df = df_plot.groupby('season')['turb'].agg(agg_method).reset_index()
    agg_df.columns = ['season', f'turb_{agg_method}']
    
    sns.barplot(data=agg_df, x='season', y=f'turb_{agg_method}', ax=ax, 
                palette='viridis', errorbar=None)
    ax.set_title(f"Турбидность по сезонам (агрегация: {agg_method})")
    ax.set_ylabel(f"Турбидность ({agg_method})")
    fig.tight_layout()
    canvas.draw_idle()

def plot_scatter() -> None:
    """Точечная диаграмма: pH vs Turbidity с кодированием цвета и размера."""
    ax = clear_figure()
    df_plot = df_work.copy()
    if df_plot.empty: return
    
    # Ограничение выборки для плавности интерфейса, если данных > 15к
    if len(df_plot) > 15000:
        df_plot = df_plot.sample(n=15000, random_state=42)
        
    sns.scatterplot(data=df_plot, x='ph', y='turb', hue='ph_status', 
                    size='cl', sizes=(10, 150), ax=ax, alpha=0.7)
    ax.set_title("Зависимость турбидности от уровня pH")
    ax.set_xlabel("pH")
    ax.set_ylabel("Турбидность (NTU)")
    fig.tight_layout()
    canvas.draw_idle()

def plot_histogram() -> None:
    """Гистограмма: распределение турбидности с KDE."""
    ax = clear_figure()
    df_plot = df_work.copy()
    if df_plot.empty: return
    
    sns.histplot(data=df_plot, x='turb', kde=True, hue='filter_id', 
                 bins=50, ax=ax, element='step', stat='density', common_norm=False)
    ax.set_title("Плотность распределения турбидности по фильтрам")
    ax.set_xlabel("Турбидность (NTU)")
    ax.set_ylabel("Плотность")
    fig.tight_layout()
    canvas.draw_idle()

# ======================== ЭТАП 5-6: ПАНЕЛЬ УПРАВЛЕНИЯ И ИНТЕРАКТИВНОСТЬ ========================
def apply_filters_and_redraw() -> None:
    """Применяет фильтры из UI к глобальному датасету и перерисовывает текущий график."""
    global df_work
    if df_raw is None: return
    
    # Фильтрация на уровне Pandas ДО отрисовки (согласно методичке)
    df_work = preprocess_data()
    f_id = filter_var.get()
    if f_id != "Все":
        # Безопасная фильтрация с явным приведением типов
        mask = df_work['filter_id'] == pd.Categorical(f_id).categories[0]
        df_work = df_work.loc[mask].copy()
        
    # Перерисовка активного графика
    globals()[f"plot_{current_chart}"]()

def set_chart_type(chart_type: str) -> None:
    """Переключает тип графика и обновляет отображение."""
    global current_chart
    current_chart = chart_type
    globals()[f"plot_{chart_type}"]()

def export_plot() -> None:
    """Экспорт текущего состояния фигуры в файл."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("PDF Document", "*.pdf")]
    )
    if filepath:
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Экспорт", "График успешно сохранён.")

# --- Создание панели управления ---
ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=8)

# Фильтр по ID фильтра
tk.Label(ctrl_frame, text="Фильтр:", bg="#f0f2f5").pack(side=tk.LEFT, padx=5)
unique_ids = ["Все"] + [str(i) for i in sorted(df_raw['filter_id'].unique()) if i != 0]
ttk.Combobox(ctrl_frame, textvariable=filter_var, values=unique_ids, width=10, state="readonly").pack(side=tk.LEFT, padx=5)
filter_var.trace_add("write", lambda *_: apply_filters_and_redraw())

# Радиокнопки агрегации
tk.Label(ctrl_frame, text="Агрегация:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(15, 5))
for agg in ["mean", "median", "sum"]:
    tk.Radiobutton(ctrl_frame, text=agg.capitalize(), variable=agg_var, value=agg, bg="#f0f2f5",
                   command=apply_filters_and_redraw).pack(side=tk.LEFT, padx=2)

# Кнопки переключения графиков
tk.Button(ctrl_frame, text="Линейный", command=lambda: set_chart_type("line"), width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=lambda: set_chart_type("bar"), width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Точечный", command=lambda: set_chart_type("scatter"), width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Гистограмма", command=lambda: set_chart_type("histogram"), width=10).pack(side=tk.LEFT, padx=4)

# Служебные кнопки (справа)
tk.Button(ctrl_frame, text="🔄 Обновить", command=apply_filters_and_redraw, width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text="💾 Экспорт", command=export_plot, width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)

# ======================== ЗАПУСК ========================
if __name__ == '__main__':
    # Первичная предобработка и отрисовка
    df_work = preprocess_data()
    plot_line()
    
    # Вход в событийный цикл Tkinter
    root.mainloop()