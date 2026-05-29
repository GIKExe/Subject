import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# ======================== ЭТАП 0-1: ИНИЦИАЛИЗАЦИЯ ========================
df_raw: Optional[pd.DataFrame] = None
df_processed: Optional[pd.DataFrame] = None  # Обработанные данные (ОДИН РАЗ)
df_work: Optional[pd.DataFrame] = None       # Рабочая копия для графика
fig: plt.Figure
canvas: Optional[FigureCanvasTkAgg] = None
current_chart: str = "line"
available_filters: List[int] = []  # Список НЕ редких фильтров

root = tk.Tk()
root.title("Дашборд: Интерактивный анализ")
root.geometry("1100x750")
root.configure(bg="#f0f2f5")

filter_var = tk.StringVar(value="Все")
agg_var = tk.StringVar(value="mean")

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")

# ======================== ЗАГРУЗКА ДАННЫХ ========================
def load_data() -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv('data.csv', parse_dates=False)
        if df.empty:
            messagebox.showerror("Ошибка", "Файл data.csv пуст.")
            return None
        return df
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить CSV: {e}")
        return None

df_raw = load_data()
if df_raw is None:
    raise SystemExit("Данные недоступны")

# ======================== ЭТАП 2: ПРЕДОБРАБОТКА (ОДИН РАЗ) ========================
def preprocess_data(df_input: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
    """
    Общая предобработка данных (выполняется ОДИН РАЗ при старте)
    Возвращает: (обработанный DataFrame, список НЕ редких фильтров)
    """
    df = df_input.copy()
    
    # 1. Безопасная замена NaN/Inf медианами
    for col in ['turb', 'ph', 'cl', 'flow']:
        clean_col = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = clean_col.fillna(clean_col.median())
    
    # Ограничение физических диапазонов
    df['turb'] = df['turb'].clip(lower=0)
    df['cl'] = df['cl'].clip(lower=0)
    df['ph'] = df['ph'].clip(lower=6.5, upper=8.5)
    
    # 2. Feature Engineering
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
    
    df = df.sort_values(['filter_id', 'ts']).reset_index(drop=True)
    
    # Скользящее среднее и тренд
    df['turb_ma'] = df.groupby('filter_id')['turb'].transform(
        lambda x: x.rolling(window=35, min_periods=1).mean()
    )
    df['turb_diff'] = df.groupby('filter_id')['turb_ma'].transform(lambda x: x.diff().fillna(0))
    df['turb_trend'] = np.sign(df['turb_diff']).map(
        {-1: 'снижается', 0: 'стабильно', 1: 'растёт'}
    ).astype('category')
    
    # 3. Обрезка выбросов (IQR)
    grp = df.groupby('filter_id')['turb']
    q1 = grp.transform(lambda x: x.quantile(0.25))
    q3 = grp.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    median_grp = grp.transform('median')
    
    is_outlier = (df['turb'] < lower_bound) | (df['turb'] > upper_bound)
    df.loc[is_outlier, 'turb'] = median_grp[is_outlier]
    
    # 4. Оптимизация: редкие фильтры → 0
    threshold = int(0.01 * len(df))
    counts = df['filter_id'].value_counts()
    rare_ids = counts[counts < threshold].index
    
    # СОХРАНЯЕМ список НЕ редких фильтров ДО замены
    non_rare_filters = sorted([f for f in df['filter_id'].unique() if f not in rare_ids and f != 0])
    
    # Заменяем редкие на 0
    df.loc[df['filter_id'].isin(rare_ids), 'filter_id'] = 0
    
    df['filter_id'] = df['filter_id'].astype('category')
    df['dt'] = df['dt'].astype('datetime64[ns]')
    
    return df, non_rare_filters

# ======================== ОДНОКРАТНАЯ ОБРАБОТКА ========================
df_processed, available_filters = preprocess_data(df_raw)
print(f"✓ Загружено {len(df_processed)} записей")
print(f"✓ Доступные фильтры (не редкие): {available_filters}")
print(f"✓ Всего уникальных фильтров в df_processed: {df_processed['filter_id'].nunique()}")

# ======================== ЭТАП 3: GUI ========================
plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

fig = plt.Figure(figsize=(10, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
toolbar.pack(side=tk.TOP, fill=tk.X)

# ======================== ЭТАП 4: ОТРИСОВКА ========================
def clear_figure() -> plt.Axes:
    fig.clear()
    return fig.add_subplot(111)

def plot_line() -> None:
    """Линейный график с агрегацией по неделям"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    df_plot = df_work.copy()
    
    # Агрегация по неделям
    df_plot['week'] = df_plot['dt'].dt.to_period('W').dt.start_time
    agg_df = df_plot.groupby(['week', 'filter_id'])['turb'].mean().reset_index()
    
    # Показываем ТОЛЬКО фильтры из текущего df_work
    current_filters = sorted(agg_df['filter_id'].unique())
    
    for f_id in current_filters:
        group = agg_df[agg_df['filter_id'] == f_id]
        ax.plot(group['week'], group['turb'], label=f'Фильтр {int(f_id)}', 
                linewidth=1.5, alpha=0.7)
    
    ax.set_title("Динамика турбидности (агрегация по неделям)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Турбидность (NTU)")
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), ncol=2, fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_bar() -> None:
    """Столбчатая диаграмма по сезонам"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    agg_method = agg_var.get()
    agg_df = df_work.groupby('season')['turb'].agg(agg_method).reset_index()
    agg_df.columns = ['season', f'turb_{agg_method}']
    
    colors = ['#4A90E2', '#7ED321', '#F5A623', '#BD10E0']
    
    sns.barplot(data=agg_df, x='season', y=f'turb_{agg_method}', 
                palette=colors, ax=ax, errorbar=None)
    
    ax.set_title(f"Турбидность по сезонам ({agg_method})")
    ax.set_xlabel("Сезон")
    ax.set_ylabel(f"Турбидность ({agg_method})")
    ax.tick_params(axis='x', rotation=0)
    fig.tight_layout()
    canvas.draw_idle()

def plot_scatter() -> None:
    """Точечная диаграмма pH vs Turbidity"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    df_plot = df_work.copy()
    
    # Сэмплирование для производительности
    if len(df_plot) > 5000:
        df_plot = df_plot.sample(n=5000, random_state=42)
    
    sns.scatterplot(data=df_plot, x='ph', y='turb', 
                    hue='ph_status', ax=ax, alpha=0.6, s=30,
                    palette={'ниже нормы': 'blue', 'норма': 'orange', 'выше нормы': 'red'})
    
    ax.set_title("Зависимость турбидности от pH")
    ax.set_xlabel("pH")
    ax.set_ylabel("Турбидность (NTU)")
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1))
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_histogram() -> None:
    """Гистограмма распределения турбидности"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    sns.histplot(data=df_work, x='turb', kde=True, ax=ax, 
                 bins=50, color='steelblue', alpha=0.7)
    
    ax.set_title("Распределение турбидности")
    ax.set_xlabel("Турбидность (NTU)")
    ax.set_ylabel("Количество")
    fig.tight_layout()
    canvas.draw_idle()

# ======================== ЭТАП 5-6: УПРАВЛЕНИЕ ========================
def apply_filters_and_redraw() -> None:
    """
    Применяет фильтры к УЖЕ ОБРАБОТАННЫМ данным (df_processed).
    НЕ вызывает preprocess_data() повторно!
    """
    global df_work
    
    if df_processed is None:
        return
    
    # 1. Создаём копию уже обработанных данных (БЫСТРО!)
    df_work = df_processed.copy()
    
    # 2. Применяем фильтр по filter_id
    selected_filter = filter_var.get()
    if selected_filter != "Все":
        filter_value = int(selected_filter)
        mask = df_work['filter_id'] == filter_value
        df_work = df_work.loc[mask].copy()
        print(f"✓ Фильтр применён: ID={filter_value}, строк={len(df_work)}")
    else:
        print("✓ Фильтр: Все данные")
    
    # 3. Перерисовываем текущий график
    if current_chart == "line":
        plot_line()
    elif current_chart == "bar":
        plot_bar()
    elif current_chart == "scatter":
        plot_scatter()
    elif current_chart == "histogram":
        plot_histogram()

def set_chart_type(chart_type: str):
    """Переключает тип графика"""
    global current_chart
    current_chart = chart_type
    apply_filters_and_redraw()

def export_plot() -> None:
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
    )
    if filepath:
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Экспорт", "График сохранён")

# ======================== ПАНЕЛЬ УПРАВЛЕНИЯ ========================
ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=8)

# Фильтр по ID - ТОЛЬКО НЕ РЕДКИЕ ФИЛЬТРЫ
tk.Label(ctrl_frame, text="Фильтр:", bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

# available_filters содержит только НЕ редкие фильтры (без 0)
filter_values = ["Все", 0] + [str(f) for f in available_filters]
filter_combo = ttk.Combobox(ctrl_frame, textvariable=filter_var, values=filter_values, 
                            width=10, state="readonly")
filter_combo.pack(side=tk.LEFT, padx=5)

# Отслеживаем изменения
filter_var.trace_add("write", lambda *_: apply_filters_and_redraw())

# Агрегация
tk.Label(ctrl_frame, text="Агрегация:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(15, 5))
for agg in ["mean", "median", "sum"]:
    tk.Radiobutton(ctrl_frame, text=agg.capitalize(), variable=agg_var, 
                   value=agg, bg="#f0f2f5",
                   command=apply_filters_and_redraw).pack(side=tk.LEFT, padx=2)

# Кнопки типов графиков
tk.Button(ctrl_frame, text="Линейный", command=lambda: set_chart_type("line"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=lambda: set_chart_type("bar"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Точечный", command=lambda: set_chart_type("scatter"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Гистограмма", command=lambda: set_chart_type("histogram"), 
          width=10).pack(side=tk.LEFT, padx=4)

# Служебные кнопки
tk.Button(ctrl_frame, text="🔄 Обновить", command=apply_filters_and_redraw, 
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text="💾 Экспорт", command=export_plot, 
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)

# ======================== ЗАПУСК ========================
if __name__ == '__main__':
    # Инициализация рабочей копии
    df_work = df_processed.copy()
    plot_line()
    root.mainloop()