import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import csv
import os
import ctypes

# Импорт локального модуля
try:
	import generate
except ImportError:
	generate = None

class App(tk.Tk):
	def __init__(self):
		super().__init__()

		self.title("CSV Processor & External Sorter")
		self.geometry("1150x650")
		self.configure(bg="#f0f0f0")

		# Переменные состояния
		self.file_path = tk.StringVar(value="")
		self.num_lines_in_file = tk.IntVar(value=0)
		
		# Загрузка DLL
		self.mod1 = None
		if os.path.exists("external_sort.dll"):
			try:
				self.mod1 = ctypes.CDLL("./external_sort.dll")
				self.mod1.external_sort.argtypes = [
					ctypes.c_char_p, 
					ctypes.c_int, 
					ctypes.c_bool, 
					ctypes.CFUNCTYPE(None, ctypes.c_float)
				]
				self.mod1.external_sort.restype = None
			except Exception as e:
				print(f"Ошибка загрузки DLL: {e}")

		import external_sort as mod2
		self.mod2 = mod2

		self.lib = self.mod1
		self.init_ui()

	def init_ui(self):
		# --- Сверху: Прогресс-бар ---
		style = ttk.Style()
		style.theme_use('default')
		style.configure("Green.Horizontal.TProgressbar", foreground='#28a745', background='#28a745')

		separator_style = ttk.Style()
		separator_style.configure("Purple.TSeparator", background="#c72dbf")
		
		self.progress = ttk.Progressbar(self, orient="horizontal", length=100, 
										mode="determinate", style="Green.Horizontal.TProgressbar")
		self.progress.pack(side="top", fill="x")

		# Основной контейнер
		main_container = tk.Frame(self, bg="#f0f0f0")
		main_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

		# --- Левая часть ---
		self.left_panel = tk.Frame(main_container, bg="#f0f0f0")
		self.left_panel.pack(side="left", fill="y", padx=(0, 10))

		# 1. Файл и путь
		file_info_frame = tk.Frame(self.left_panel, bg="#f0f0f0")
		file_info_frame.pack(fill="x", pady=5)
		
		tk.Label(file_info_frame, text="Файл: ", font=("Arial", 9, "bold"), bg="#f0f0f0").pack(side="top", anchor="w")
		self.path_label = tk.Label(file_info_frame, text="Не выбран", fg="red", 
								   wraplength=220, justify="left", bg="#f0f0f0")
		self.path_label.pack(side="top", anchor="w")

		# Лейбл для отображения количества строк
		self.lines_count_label = tk.Label(file_info_frame, text="Кол-во строк: 0", 
										  font=("Arial", 9), fg="#555", bg="#f0f0f0")
		self.lines_count_label.pack(side="top", anchor="w", pady=(2, 0))

		# 2. Кнопка выбора
		tk.Button(self.left_panel, text="Выбрать файл", command=self.select_file).pack(fill="x", pady=5)

		ttk.Separator(self.left_panel, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=10)

		# 3. Поле для ввода числа (1-2048)
		tk.Label(self.left_panel, text="Размер (1-2048):", bg="#f0f0f0").pack(anchor="w")
		vcmd = (self.register(self.validate_int), '%P')
		self.size_entry = tk.Entry(self.left_panel, validate='key', state='disabled', validatecommand=vcmd)
		self.size_entry.insert(0, "1")
		self.size_entry.pack(fill="x", pady=2)

		# 4. Кнопка Сгенерировать
		self.gen_button = tk.Button(self.left_panel, text="Сгенерировать", state="disabled", command=self.run_generate)
		self.gen_button.pack(fill="x", pady=5)

		ttk.Separator(self.left_panel, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=10)

		# Модуль
		tk.Label(self.left_panel, text="Модуль:", bg="#f0f0f0").pack(anchor="w")
		self.mod_options = ["C++", "Python"]
		self.mod_combo = ttk.Combobox(self.left_panel, values=self.mod_options, state="disabled")
		self.mod_combo.current(0)
		self.mod_combo.pack(fill="x", pady=2)
		self.mod_combo.bind("<<ComboboxSelected>>", self.on_mod_combo)

		# 5. Ключ
		tk.Label(self.left_panel, text="Ключ:", bg="#f0f0f0").pack(anchor="w")
		self.key_options = ["Ник", "Айди", "Дата регистрации", "Уровень", "Кол-во часов", "Вак бан"]
		self.key_combo = ttk.Combobox(self.left_panel, values=self.key_options, state="disabled")
		self.key_combo.current(0)
		self.key_combo.pack(fill="x", pady=2)

		# 6. Направление
		tk.Label(self.left_panel, text="Направление:", bg="#f0f0f0").pack(anchor="w")
		self.dir_options = ["По убыванию", "По возрастанию"]
		self.dir_combo = ttk.Combobox(self.left_panel, values=self.dir_options, state="disabled")
		self.dir_combo.current(1)
		self.dir_combo.pack(fill="x", pady=2)

		# 7. Кнопка Сортировать
		def sort_thread():
			Thread(target=self.run_sort, daemon=True).start()
		self.sort_btn = tk.Button(self.left_panel, text="Сортировать", state="disabled", command=sort_thread)
		self.sort_btn.pack(fill="x", pady=5)

		ttk.Separator(self.left_panel, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=10)

		# 8-10. Настройки отображения
		self.file_target = tk.StringVar(value="orig")
		tk.Radiobutton(self.left_panel, text="Исходный файл", variable=self.file_target, 
					   value="orig", bg="#f0f0f0").pack(anchor="w")
		tk.Radiobutton(self.left_panel, text="Сортированный файл", variable=self.file_target, 
					   value="sort", bg="#f0f0f0").pack(anchor="w")

		tk.Label(self.left_panel, text="Начать со строки:", bg="#f0f0f0").pack(anchor="w")
		self.start_line_entry = tk.Entry(self.left_panel)
		self.start_line_entry.insert(0, "0")
		self.start_line_entry.pack(fill="x", pady=2)

		tk.Label(self.left_panel, text="Кол-во строк:", bg="#f0f0f0").pack(anchor="w")
		self.count_line_entry = tk.Entry(self.left_panel)
		self.count_line_entry.insert(0, "10")
		self.count_line_entry.pack(fill="x", pady=2)

		# 11. Кнопка Отобразить
		tk.Button(self.left_panel, text="Отобразить", command=self.display_content).pack(fill="x", pady=5)

		# --- Правая часть: Output ---
		right_panel = tk.Frame(main_container)
		right_panel.pack(side="right", fill="both", expand=True)

		# Ширина ровно 100 символов
		self.output_text = tk.Text(right_panel, width=100, wrap="none", state="disabled", font=("Courier New", 10))
		scroll_y = tk.Scrollbar(right_panel, orient="vertical", command=self.output_text.yview)
		scroll_x = tk.Scrollbar(right_panel, orient="horizontal", command=self.output_text.xview)
		
		self.output_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

		scroll_y.pack(side="right", fill="y")
		scroll_x.pack(side="bottom", fill="x")
		self.output_text.pack(side="left", fill="both", expand=True)

	# --- Логика ---

	def on_mod_combo(self, event):
		match self.mod_combo.current():
			case 0:
				self.lib = self.mod1 
			case 1:
				self.lib = self.mod2

	def validate_int(self, P):
		if P == "":
			return True
		try:
			val = int(P)
			return 1 <= val <= 2048
		except ValueError:
			return False

	def update_progress(self, value):
		self.progress['value'] = value * 100
		self.update_idletasks()

	def select_file(self):
		path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

		if path:
			self.file_path.set(path)
			self.path_label.config(text=path, fg="gray")
			
			# Активируем элементы
			self.mod_combo.config(state="readonly")
			self.key_combo.config(state="readonly")
			self.dir_combo.config(state="readonly")
			self.sort_btn.config(state="normal")

			self.size_entry.config(state='normal')
			self.gen_button.config(state='normal')
			
			# Подсчет строк
			self.count_total_lines(path)
		# else:
		# 	self.path_label.config(text="Не выбран", fg="red")
		# 	self.lines_count_label.config(text="Кол-во строк: 0")
		# 	self.sort_btn.config(state="disabled")

	def count_total_lines(self, path):
		try:
			with open(path, 'r', encoding='utf-8') as f:
				# Более надежный способ для CSV
				count = sum(1 for _ in f)
				self.num_lines_in_file.set(count)
				self.lines_count_label.config(text=f"Кол-во строк: {count}")
		except Exception as e:
			messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")

	def run_generate(self):
		if not self.file_path.get():
			messagebox.showwarning("Внимание", "Сначала выберите файл!")
			return
		
		if generate:
			size_bytes = int(self.size_entry.get()) * (1024**2)
			generate.generate(self.file_path.get(), size_bytes, self.update_progress)
			self.count_total_lines(self.file_path.get())
			messagebox.showinfo("Готово", "Генерация завершена")
		else:
			messagebox.showerror("Ошибка", "Модуль 'generate' не найден")

	def run_sort(self):
		self.sort_btn.config(state='disabled')
		self.gen_button.config(state='disabled')
		path = self.file_path.get()
		# Проверка на \n в конце
		try:
			with open(path, 'rb+') as f:
				f.seek(-1, os.SEEK_END)
				if f.read(1) != b'\n':
					messagebox.showerror("Ошибка", "Файл должен заканчиваться символом переноса строки (LF).")
					self.sort_btn.config(state='normal')
					self.gen_button.config(state='normal')
					return
		except Exception as e:
			messagebox.showerror("Ошибка доступа", str(e))
			self.sort_btn.config(state='normal')
			self.gen_button.config(state='normal')
			return

		if not self.lib:
			messagebox.showerror("Ошибка", "DLL не загружена")
			self.sort_btn.config(state='normal')
			self.gen_button.config(state='normal')
			return

		CMPFUNC = ctypes.CFUNCTYPE(None, ctypes.c_float)
		callback_c = CMPFUNC(self.update_progress)
		
		key_idx = self.key_combo.current()
		ascending = bool(self.dir_combo.current())

		try:
			self.lib.external_sort(path.encode('utf-8'), key_idx, ascending, callback_c)
			messagebox.showinfo("Успех", "Сортировка завершена")
		except Exception as e:
			messagebox.showerror("Ошибка DLL", str(e))
		self.sort_btn.config(state='normal')
		self.gen_button.config(state='normal')

	def display_content(self):
		base_path = self.file_path.get()
		if not base_path:
			return

		target = base_path if self.file_target.get() == "orig" else base_path + ".sorted"
		
		if not os.path.exists(target):
			messagebox.showerror("Ошибка", f"Файл {target} не найден")
			return

		try:
			start_line = int(self.start_line_entry.get())
			count = int(self.count_line_entry.get())
			
			self.output_text.config(state="normal")
			self.output_text.delete("1.0", tk.END)

			with open(target, 'r', encoding='utf-8') as f:
				reader = csv.reader(f)
				for i, row in enumerate(reader):
					if i < start_line:
						continue
					if i >= start_line + count:
						break
					self.output_text.insert(tk.END, ",".join(row) + "\n")
			
			self.output_text.config(state="disabled")

		except ValueError:
			messagebox.showerror("Ошибка", "Введите корректные числа")

if __name__ == "__main__":
	app = App()
	app.mainloop()