import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import Optional, Literal
from pathlib import Path

# ============================================================================
# Константы и глобальные переменные
# ============================================================================

VARIANT_NUMBER: int = 20
CURRENT_CHART: Literal["line", "bar", "scatter", "heatmap"] = "line"

# Хранилище данных
df_raw: Optional[pd.DataFrame] = None
df_work: Optional[pd.DataFrame] = None
fig: Optional[Figure] = None
canvas: Optional[FigureCanvasTkAgg] = None


def setup_matplotlib_style() -> None:
    """Настройка шрифтов matplotlib для корректного отображения кириллицы."""
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['axes.unicode_minus'] = False


def load_data(filepath: str) -> pd.DataFrame:
    """
    Загрузка данных из CSV файла.
    
    Args:
        filepath: Путь к файлу с данными
        
    Returns:
        DataFrame с загруженными данными
        
    Raises:
        FileNotFoundError: Если файл не найден
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не найден в директории скрипта.")
    
    dataframe = pd.read_csv(filepath)
    print(f"Загружено {dataframe.shape[0]} строк из {filepath}")
    return dataframe


# ============================================================================
# Этап 2. Предобработка данных и создание новых признаков
# ============================================================================

def preprocess_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Предобработка данных: фильтрация, создание производных признаков,
    вычисление скользящих средних и трендов.
    
    Args:
        raw_data: Исходный DataFrame
        
    Returns:
        Обработанный DataFrame с новыми признаками
    """
    # Создаём рабочую копию данных
    work_data = raw_data.copy()
    
    # 1. Очистка данных: убираем отрицательные значения и выбросы
    work_data['turb'] = work_data['turb'].clip(lower=0)
    work_data['cl'] = work_data['cl'].clip(lower=0)
    work_data['ph'] = work_data['ph'].clip(lower=6.5, upper=8.5)
    
    # 2. Создание временной метки в формате datetime
    work_data['dt'] = pd.to_datetime(work_data['ts'], unit='s')
    
    # 3. Категоризация уровня pH
    work_data['ph_status'] = pd.cut(
        work_data['ph'],
        bins=[0, 6.5, 8.5, 14],
        labels=['ниже нормы', 'норма', 'выше нормы'],
        include_lowest=True
    ).astype('category')
    
    # 4. Определение сезона по месяцу
    work_data['season'] = pd.cut(
        work_data['dt'].dt.month,
        bins=[0, 3, 6, 9, 12],
        labels=['зима', 'весна', 'лето', 'осень'],
        include_lowest=True
    ).astype('category')
    
    # 5. Флаг соответствия нормативам
    work_data['compliance_flag'] = (
        (work_data['turb'] <= 1.5) &
        work_data['ph'].between(6.5, 8.5) &
        work_data['cl'].between(0.3, 0.5)
    )
    
    # 6. Сортировка данных для корректного расчёта скользящих средних
    work_data = work_data.sort_values(['filter_id', 'ts']).reset_index(drop=True)
    
    # 7. Расчёт скользящего среднего турбидности (окно 35 отсчётов)
    work_data['turb_ma'] = work_data.groupby('filter_id')['turb'].transform(
        lambda x: x.rolling(window=35, min_periods=1).mean()
    )
    
    # 8. Вычисление разности расхода между соседними измерениями
    work_data['flow_diff'] = work_data.groupby('filter_id')['flow'].transform(
        lambda x: x.diff().fillna(x.iloc[0])
    )
    
    # 9. Определение тренда турбидности
    work_data['turb_diff'] = work_data.groupby('filter_id')['turb_ma'].transform(
        lambda x: x.diff().fillna(0)
    )
    work_data['turb_trend'] = np.sign(work_data['turb_diff']).map({
        -1: 'снижается',
         0: 'стабильно',
         1: 'растёт'
    }).astype('category')
    
    # 10. Удаление промежуточных колонок
    work_data.drop(columns=['dt', 'turb_ma', 'turb_diff'], inplace=True)
    work_data['filter_id'] = work_data['filter_id'].astype('category')
    
    return work_data


# ============================================================================
# Этап 3. Инициализация графического интерфейса
# ============================================================================

def create_main_window() -> tk.Tk:
    """
    Создание и настройка главного окна приложения.
    
    Returns:
        Настроенное главное окно Tkinter
    """
    window = tk.Tk()
    window.title(f"Дашборд: Вариант {VARIANT_NUMBER}")
    window.geometry("1000x700")
    window.configure(bg="#f0f2f5")
    return window


def setup_plot_area(parent: tk.Widget) -> tuple[Figure, FigureCanvasTkAgg, NavigationToolbar2Tk]:
    """
    Создание области для отображения графиков.
    
    Args:
        parent: Родительский виджет
        
    Returns:
        Кортеж (Figure, FigureCanvasTkAgg, NavigationToolbar2Tk)
    """
    # Контейнер для графика
    plot_frame = tk.Frame(parent, bg="white", relief=tk.SUNKEN, bd=1)
    plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Создание фигуры Matplotlib
    figure = Figure(figsize=(9, 5.5), dpi=100)
    
    # Интеграция с Tkinter
    canvas_widget = FigureCanvasTkAgg(figure, master=plot_frame)
    canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Панель инструментов (масштабирование, сохранение)
    toolbar = NavigationToolbar2Tk(canvas_widget, plot_frame)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    return figure, canvas_widget, toolbar


# ============================================================================
# Этап 4. Функции отрисовки графиков
# ============================================================================

def clear_figure(figure: Figure) -> None:
    """Очистка фигуры перед новой отрисовкой."""
    figure.clear()


def plot_line_chart(figure: Figure, canvas: FigureCanvasTkAgg, data: pd.DataFrame) -> None:
    """
    Отрисовка линейного графика динамики турбидности.
    
    Args:
        figure: Объект Figure для отрисовки
        canvas: Холст для обновления отображения
        data: DataFrame с данными
    """
    clear_figure(figure)
    axis = figure.add_subplot(111)
    
    # Используем копию данных для безопасности
    plot_data = data.copy()
    
    sns.lineplot(
        data=plot_data,
        x='ts',
        y='turb',
        hue='filter_id',
        ax=axis
    )
    
    axis.set_title('Динамика турбидности по фильтрам\n(Скользящее окно k=35 учтено при предобработке)')
    axis.set_xlabel('Время (timestamp)')
    axis.set_ylabel('Турбидность')
    
    figure.tight_layout()
    canvas.draw_idle()


def plot_bar_chart(figure: Figure, canvas: FigureCanvasTkAgg, data: pd.DataFrame) -> None:
    """
    Отрисовка столбчатой диаграммы средних значений.
    
    Args:
        figure: Объект Figure для отрисовки
        canvas: Холст для обновления отображения
        data: DataFrame с данными
    """
    clear_figure(figure)
    axis = figure.add_subplot(111)
    
    # Агрегация данных по фильтрам
    aggregated_data = data.groupby('filter_id').agg({
        'turb': 'mean',
        'flow': 'max'
    }).reset_index()
    
    sns.barplot(
        data=aggregated_data,
        x='filter_id',
        y='turb',
        palette='viridis',
        ax=axis
    )
    
    axis.set_title('Средняя турбидность по фильтрам')
    axis.set_xlabel('ID фильтра')
    axis.set_ylabel('Средняя турбидность')
    
    figure.tight_layout()
    canvas.draw_idle()


def plot_scatter_chart(figure: Figure, canvas: FigureCanvasTkAgg, data: pd.DataFrame) -> None:
    """
    Отрисовка точечной диаграммы зависимости параметров.
    
    Args:
        figure: Объект Figure для отрисовки
        canvas: Холст для обновления отображения
        data: DataFrame с данными
    """
    clear_figure(figure)
    axis = figure.add_subplot(111)
    
    sns.scatterplot(
        data=data,
        x='ph',
        y='turb',
        hue='ph_status',
        style='season',
        s=80,
        ax=axis
    )
    
    axis.set_title('Зависимость мутности от кислотности\n(группировка по сезонам и статусу pH)')
    axis.set_xlabel('pH (кислотность)')
    axis.set_ylabel('Турбидность')
    
    figure.tight_layout()
    canvas.draw_idle()


def plot_heatmap_chart(figure: Figure, canvas: FigureCanvasTkAgg, data: pd.DataFrame) -> None:
    """
    Отрисовка тепловой карты корреляции параметров.
    
    Args:
        figure: Объект Figure для отрисовки
        canvas: Холст для обновления отображения
        data: DataFrame с данными
    """
    clear_figure(figure)
    axis = figure.add_subplot(111)
    
    # Создание сводной таблицы для тепловой карты
    pivot_table = data.pivot_table(
        values='flow',
        index='season',
        columns='ph_status',
        aggfunc='mean',
        fill_value=0
    )
    
    sns.heatmap(
        data=pivot_table,
        annot=True,
        cmap='YlGnBu',
        fmt=".1f",
        ax=axis
    )
    
    axis.set_title('Средний расход воды: Сезоны × Статус pH')
    
    figure.tight_layout()
    canvas.draw_idle()


# ============================================================================
# Этап 5. Обработчики событий и панель управления
# ============================================================================

def refresh_chart(
    chart_type: Literal["line", "bar", "scatter", "heatmap"],
    canvas: FigureCanvasTkAgg,
    figure: Figure,
    data: pd.DataFrame
) -> None:
    """
    Обновление отображаемого графика.
    
    Args:
        chart_type: Тип графика для отображения
        canvas: Холст для отрисовки
        figure: Объект Figure
        data: DataFrame с данными
    """
    if chart_type == "line":
        plot_line_chart(figure, canvas, data)
    elif chart_type == "bar":
        plot_bar_chart(figure, canvas, data)
    elif chart_type == "scatter":
        plot_scatter_chart(figure, canvas, data)
    elif chart_type == "heatmap":
        plot_heatmap_chart(figure, canvas, data)


def on_chart_button_click(
    chart_type: Literal["line", "bar", "scatter", "heatmap"]
) -> None:
    """
    Обработчик нажатия кнопки выбора типа графика.
    
    Args:
        chart_type: Выбранный тип графика
    """
    global CURRENT_CHART
    CURRENT_CHART = chart_type
    
    if canvas is not None and fig is not None and df_work is not None:
        refresh_chart(chart_type, canvas, fig, df_work)


def on_refresh_button_click() -> None:
    """Обработчик кнопки обновления данных."""
    global df_work, CURRENT_CHART
    
    if df_raw is not None:
        print("Пересчёт данных...")
        df_work = preprocess_data(df_raw)
        
        if canvas is not None and fig is not None:
            refresh_chart(CURRENT_CHART, canvas, fig, df_work)


def on_export_button_click(figure: Figure) -> None:
    """
    Обработчик кнопки экспорта графика.
    
    Args:
        figure: Объект Figure для сохранения
    """
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG файлы", "*.png"), ("PDF файлы", "*.pdf")]
    )
    
    if filepath:
        try:
            figure.savefig(filepath, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Успех", f"График сохранён в:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


def create_control_panel(parent: tk.Widget, figure: Figure) -> tk.Frame:
    """
    Создание панели управления с кнопками.
    
    Args:
        parent: Родительский виджет
        figure: Объект Figure для экспорта
        
    Returns:
        Созданный фрейм с кнопками
    """
    control_frame = tk.Frame(parent, bg="#f0f2f5")
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Кнопки выбора типа графика
    tk.Button(
        control_frame,
        text="Линейный график",
        command=lambda: on_chart_button_click('line'),
        width=16
    ).pack(side=tk.LEFT, padx=4)
    
    tk.Button(
        control_frame,
        text="Столбчатая диаграмма",
        command=lambda: on_chart_button_click('bar'),
        width=16
    ).pack(side=tk.LEFT, padx=4)
    
    tk.Button(
        control_frame,
        text="Точечная диаграмма",
        command=lambda: on_chart_button_click('scatter'),
        width=16
    ).pack(side=tk.LEFT, padx=4)
    
    tk.Button(
        control_frame,
        text="Тепловая карта",
        command=lambda: on_chart_button_click('heatmap'),
        width=16
    ).pack(side=tk.LEFT, padx=4)
    
    # Кнопки управления (справа)
    tk.Button(
        control_frame,
        text="Обновить данные",
        command=on_refresh_button_click,
        width=14,
        bg="#4CAF50",
        fg="white"
    ).pack(side=tk.RIGHT, padx=4)
    
    tk.Button(
        control_frame,
        text="Экспорт графика",
        command=lambda: on_export_button_click(figure),
        width=14,
        bg="#2196F3",
        fg="white"
    ).pack(side=tk.RIGHT, padx=4)
    
    return control_frame


# ============================================================================
# Основная функция запуска приложения
# ============================================================================

def main() -> None:
    """Точка входа в приложение."""
    global df_raw, df_work, fig, canvas, CURRENT_CHART
    
    # Настройка matplotlib
    setup_matplotlib_style()
    
    # Загрузка и предобработка данных
    try:
        df_raw = load_data('data.csv')
        df_work = preprocess_data(df_raw)
        
        # Сохранение подготовленных данных
        df_work.to_parquet('data_prepared.parquet', index=False)
        print("Данные сохранены в data_prepared.parquet")
        
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return
    
    # Создание главного окна
    root = create_main_window()
    
    # Настройка области графика
    fig, canvas, toolbar = setup_plot_area(root)
    
    # Создание панели управления
    create_control_panel(root, fig)
    
    # Первоначальная отрисовка графика
    if df_work is not None:
        refresh_chart(CURRENT_CHART, canvas, fig, df_work)
    
    # Запуск главного цикла
    print("Дашборд запущен. Закрытие окна завершит работу программы.")
    root.mainloop()


if __name__ == "__main__":
    main()