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

# ======================== ЭТАП 1: ИНИЦИАЛИЗАЦИЯ ========================
df_raw: Optional[pd.DataFrame] = None
df_work: Optional[pd.DataFrame] = None
fig: plt.Figure
canvas: Optional[FigureCanvasTkAgg] = None
current_chart: str = "line"

# ВАЖНО: root создаётся ДО переменных Tkinter!
root = tk.Tk()
root.title("Дашборд: Интерактивный анализ")
root.geometry("1100x750")
root.configure(bg="#f0f2f5")

filter_var = tk.StringVar(value="Все")
agg_var = tk.StringVar(value="mean")

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")

# ======================== ЭТАП 1: ЗАГРУЗКА ДАННЫХ ========================
def load_data() -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv('data.csv', parse_dates=False)
        if df.empty:
            messagebox.showerror("Ошибка", "Файл data.csv пуст.")
            return None
        return df
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл data.csv не найден.")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", str(e))
        return None

df_raw = load_data()
if df_raw is None:
    raise SystemExit("Приложение остановлено.")

# ======================== ЭТАП 2: ПРЕДОБРАБОТКА ========================
def preprocess_data() -> pd.DataFrame:
    if df_raw is None:
        raise ValueError("Данные не загружены")
    
    df = df_raw.copy()
    
    # 1. Безопасная замена NaN/Inf
    for col in ['turb', 'ph', 'cl', 'flow']:
        clean_col = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = clean_col.fillna(clean_col.median())
        
    # Ограничение диапазонов
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
    
    # 4. Оптимизация категориальных полей (ИСПРАВЛЕНО)
    # Мы НЕ заменяем редкие ID на 0, так как это ломает интерактивный фильтр.
    # Оставляем оригинальные ID, но приводим к категории для экономии памяти.
    df['filter_id'] = df['filter_id'].astype('category')
    
    return df

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
    ax = clear_figure()
    if df_work is None or df_work.empty: return
    
    df_plot = df_work.copy()
    df_plot['week'] = df_plot['dt'].dt.to_period('W').dt.start_time
    agg_df = df_plot.groupby(['week', 'filter_id'])['turb'].mean().reset_index()
    
    # Ограничиваем легенду для читаемости
    unique_f = agg_df['filter_id'].unique()
    display_f = unique_f[:10] if len(unique_f) > 10 else unique_f
    agg_df = agg_df[agg_df['filter_id'].isin(display_f)]
    
    for f_id, group in agg_df.groupby('filter_id'):
        ax.plot(group['week'], group['turb'], label=f'Фильтр {f_id}', linewidth=1.5, alpha=0.8)
        
    ax.set_title("Динамика турбидности (агрегация по неделям)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Турбидность (NTU)")
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_bar() -> None:
    ax = clear_figure()
    if df_work is None or df_work.empty: return
    
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
    ax = clear_figure()
    if df_work is None or df_work.empty: return
    
    df_plot = df_work.copy()
    if len(df_plot) > 5000:
        df_plot = df_plot.sample(n=5000, random_state=42)
        
    sns.scatterplot(data=df_plot, x='ph', y='turb', hue='ph_status', 
                    ax=ax, alpha=0.6, s=30,
                    palette={'ниже нормы': 'blue', 'норма': 'orange', 'выше нормы': 'red'})
                    
    ax.set_title("Зависимость турбидности от уровня pH")
    ax.set_xlabel("pH")
    ax.set_ylabel("Турбидность (NTU)")
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1))
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_histogram() -> None:
    ax = clear_figure()
    if df_work is None or df_work.empty: return
    
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
    if df_raw is None: return
    
    # Предобработка всегда идёт от сырых данных
    df_work = preprocess_data()
    f_id = filter_var.get()
    
    if f_id != "Все":
        # ИСПРАВЛЕНИЕ: Явное приведение типа для безопасного сравнения
        # Pandas category иногда капризничает со строками, приводим к типу столбца
        target_type = type(df_work['filter_id'].cat.categories[0])
        try:
            filter_val = target_type(f_id)
        except ValueError:
            filter_val = f_id
            
        mask = df_work['filter_id'] == filter_val
        df_work = df_work.loc[mask].copy()
        print(f"Фильтр применён: ID={f_id}, строк={len(df_work)}")
    else:
        print("Фильтр: Все данные")
        
    globals()[f"plot_{current_chart}"]()

def set_chart_type(chart_type: str) -> None:
    global current_chart
    current_chart = chart_type
    apply_filters_and_redraw()  # Перерисовка с учётом текущих фильтров

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
# ИСПРАВЛЕНИЕ: Берём уникальные ID из ИСХОДНЫХ данных, чтобы список был полным
unique_ids = ["Все"] + [str(i) for i in sorted(df_raw['filter_id'].unique()) if i != 0]
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