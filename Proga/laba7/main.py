import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
import warnings

warnings.filterwarnings('ignore')

# ======================== ЭТАП 0-1: ИНИЦИАЛИЗАЦИЯ ========================
df_raw: Optional[pd.DataFrame] = None
df_work: Optional[pd.DataFrame] = None
fig: plt.Figure
canvas: Optional[FigureCanvasTkAgg] = None
current_chart: str = "line"

root = tk.Tk()
root.title("Дашборд: Интерактивный анализ")
root.geometry("1100x750")
root.configure(bg="#f0f2f5")

filter_var = tk.StringVar(value="Все")
agg_var = tk.StringVar(value="mean")

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")

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

# ======================== ЭТАП 2: ПРЕДОБРАБОТКА ========================
def preprocess_data() -> pd.DataFrame:
    if df_raw is None:
        raise ValueError("Данные не загружены")
    
    df = df_raw.copy()
    
    for col in ['turb', 'ph', 'cl', 'flow']:
        clean_col = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = clean_col.fillna(clean_col.median())
    
    df['turb'] = df['turb'].clip(lower=0)
    df['cl'] = df['cl'].clip(lower=0)
    df['ph'] = df['ph'].clip(lower=6.5, upper=8.5)
    
    df['dt'] = pd.to_datetime(df['ts'], unit='s')
    
    df['ph_status'] = pd.cut(
        df['ph'], bins=[0, 6.5, 8.5, 14],
        labels=['ниже нормы', 'норма', 'выше нормы']
    ).astype('category')
    
    df['season'] = pd.cut(
        df['dt'].dt.month, bins=[0, 3, 6, 9, 12],
        labels=['зима', 'весна', 'лето', 'осень']
    ).astype('category')
    
    df = df.sort_values(['filter_id', 'ts']).reset_index(drop=True)
    
    # Оптимизация: редкие фильтры → 0
    threshold = int(0.01 * len(df))
    counts = df['filter_id'].value_counts()
    rare_ids = counts[counts < threshold].index
    df.loc[df['filter_id'].isin(rare_ids), 'filter_id'] = 0
    
    df['filter_id'] = df['filter_id'].astype('category')
    return df

# ======================== ЭТАП 3: GUI ========================
plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

fig = plt.Figure(figsize=(10, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

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
    
    # Агрегация по неделям для производительности
    df_plot['week'] = df_plot['dt'].dt.to_period('W').dt.start_time
    agg_df = df_plot.groupby(['week', 'filter_id'])['turb'].mean().reset_index()
    
    # Показываем только топ-10 фильтров + "0"
    top_filters = df_plot['filter_id'].value_counts().nlargest(10).index.tolist()
    if 0 not in top_filters:
        top_filters.append(0)
    agg_df = agg_df[agg_df['filter_id'].isin(top_filters)]
    
    # Группируем по filter_id для цветов
    for f_id, group in agg_df.groupby('filter_id'):
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
    
    # Явные цвета для сезонов
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
    
    scatter = sns.scatterplot(data=df_plot, x='ph', y='turb', 
                              hue='ph_status', ax=ax, alpha=0.5, s=30,
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
    
    # Показываем общую гистограмму + KDE
    sns.histplot(data=df_work, x='turb', kde=True, ax=ax, 
                 bins=50, color='steelblue', alpha=0.7)
    
    ax.set_title("Распределение турбидности")
    ax.set_xlabel("Турбидность (NTU)")
    ax.set_ylabel("Количество")
    fig.tight_layout()
    canvas.draw_idle()

# ======================== ЭТАП 5-6: УПРАВЛЕНИЕ ========================
def apply_filters_and_redraw() -> None:
    global df_work
    if df_raw is None:
        return
    
    df_work = preprocess_data()
    f_id = filter_var.get()
    
    if f_id != "Все":
        mask = df_work['filter_id'] == f_id
        df_work = df_work.loc[mask].copy()
    
    globals()[f"plot_{current_chart}"]()

def set_chart_type(chart_type: str) -> None:
    global current_chart
    current_chart = chart_type
    globals()[f"plot_{chart_type}"]()

def export_plot() -> None:
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
    )
    if filepath:
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Экспорт", "График сохранён")

# Панель управления
ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=8)

tk.Label(ctrl_frame, text="Фильтр:", bg="#f0f2f5").pack(side=tk.LEFT, padx=5)
unique_ids = ["Все"] + [str(i) for i in sorted(df_raw['filter_id'].unique()) if i != 0][:20]
ttk.Combobox(ctrl_frame, textvariable=filter_var, values=unique_ids, 
             width=10, state="readonly").pack(side=tk.LEFT, padx=5)
filter_var.trace_add("write", lambda *_: apply_filters_and_redraw())

tk.Label(ctrl_frame, text="Агрегация:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(15, 5))
for agg in ["mean", "median", "sum"]:
    tk.Radiobutton(ctrl_frame, text=agg.capitalize(), variable=agg_var, 
                   value=agg, bg="#f0f2f5",
                   command=apply_filters_and_redraw).pack(side=tk.LEFT, padx=2)

tk.Button(ctrl_frame, text="Линейный", command=lambda: set_chart_type("line"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=lambda: set_chart_type("bar"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Точечный", command=lambda: set_chart_type("scatter"), 
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Гистограмма", command=lambda: set_chart_type("histogram"), 
          width=10).pack(side=tk.LEFT, padx=4)

tk.Button(ctrl_frame, text="🔄 Обновить", command=apply_filters_and_redraw, 
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text="💾 Экспорт", command=export_plot, 
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)

# ======================== ЗАПУСК ========================
if __name__ == '__main__':
    df_work = preprocess_data()
    plot_line()
    root.mainloop()