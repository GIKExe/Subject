import tkinter as tk
from tkinter import ttk, messagebox
from ctypes import *
from functools import wraps


def draw():
	if mod is None: return
	size: int = mod.getSize(struct)
	if size == 0: return []
	ArrayType = c_int * size
	buffer = ArrayType()
	copied = mod.display(struct, buffer, size)
	if copied != size:
		raise RuntimeError("Ошибка копирования данных")
	grid.fill_grid(list(buffer)) 


def redraw(func):
	@wraps(func)
	def wraper(*args, **kwargs):
		func(*args, **kwargs)
		draw()
	return wraper


def on_select(event):
	global mod, struct
	value = combobox.get()
	print("Выбран другой модуль, очистка и инициализация дека")

	if (mod != None):
		for btn in buttons:
			btn.config(state="disabled")
		mod.destroy(struct)
	grid.clear_grid()

	mod = mods[value]
	struct = mod.make()
	for btn in buttons:
		btn.config(state="normal")


class Int32Entry(tk.Entry):
	def __init__(self, master=None, **kwargs):
		super().__init__(master, **kwargs)
		self.config(validate="key")
		self.validate_command = (self.register(self.validate_input), "%P")
		self.config(validatecommand=self.validate_command)
		
	def validate_input(self, new_value):
		# Разрешаем пустую строку для возможности очистки
		if new_value == "":
			return True
		
		# Проверяем, что вводятся только цифры и знак минус
		if not new_value.lstrip('-').isdigit():
			return False
		
		# Преобразуем в целое число
		try:
			value = int(new_value)
		except ValueError:
			return False
		
		# Проверяем диапазон для i32
		if -2147483648 <= value <= 2147483647:
			return True
		else:
			messagebox.showerror("Ошибка", "Число выходит за диапазон i32 (-2147483648 до 2147483647)")
			return False


class NumberGrid:
	def __init__(self, master):
		self.master = master
		self.cell_width = 80  # фиксированная ширина ячейки
		self.cell_height = 30  # фиксированная высота ячейки
		self.labels = []  # список для хранения виджетов
		
	def clear_grid(self):
		for label in self.labels:
			label.destroy()
		self.labels.clear()

	def fill_grid(self, numbers):
		self.clear_grid()
		max_cols = self.master.winfo_width() // self.cell_width
		
		if len(numbers) < max_cols:
			max_cols = len(numbers)
		
		for i, number in enumerate(numbers):
			row = i // max_cols
			col = i % max_cols
			
			label = ttk.Label(
				self.master,
				text=str(number),
				width=10,
				relief="ridge",
				padding=0,
				anchor="center"
			)
			
			x = col * (self.cell_width)
			y = row * (self.cell_height)
			
			label.place(
				x=x, y=y,
				width=self.cell_width,
				height=self.cell_height
			)
			
			self.labels.append(label)


def main():
	global buttons, combobox, grid

	root = tk.Tk()
	root.title("Дек на библиотеках")
	root.geometry("800x600")

	left_frame = tk.Frame(root, width=400, height=600, bg="lightgray")
	right_frame = tk.Frame(root, width=400, height=600, bg="lightblue")

	left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
	right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

	left_top_frame = tk.Frame(left_frame, height=200, bg="lightgray")
	left_bottom_frame = tk.Frame(left_frame, height=400, bg="lightgray")

	left_top_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
	left_bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

	combobox = ttk.Combobox(left_top_frame, values=combobox_options, state="readonly")
	combobox.bind("<<ComboboxSelected>>", on_select)
	combobox.pack(pady=10, padx=20)

	entry = Int32Entry(left_top_frame, width=30)
	entry.pack(pady=5, padx=20)


	@redraw
	def f1():
		mod.clear(struct)
		print("дек очищен")

	def f2():
		value = mod.getSize(struct)
		print(f"размер дека: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))

	@redraw
	def f3():
		value = entry.get()
		if not value: return
		value = int(value)
		if value < 0: return
		mod.fillRandom(struct, value)
		print(f"помещено в конец {value} случайных чисел");

	@redraw
	def f4():
		value = entry.get()
		if not value: return
		value = int(value)
		mod.pushFront(struct, value)
		print(f"помещено в начало: {value}")

	@redraw
	def f5():
		value = entry.get()
		if not value: return
		value = int(value)
		mod.pushBack(struct, value)
		print(f"помещено в конец: {value}")
	
	@redraw
	def f6():
		if mod.isEmpty(struct): return
		value = mod.popFront(struct)
		print(f"получено из начала: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))

	@redraw
	def f7():
		if mod.isEmpty(struct): return
		value = mod.popBack(struct)
		print(f"получено из конца: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))

	buttons = []
	button_nf = (
		["Очистить", f1],
		["Узнать размер", f2],
		["Заполнить случайными", f3],
		["Вставить в начало", f4],
		["Вставить в конец", f5],
		["Забрать из начала", f6],
		["Забрать из конца", f7],
	)

	for i in range(len(button_nf)):
		btn = tk.Button(
			left_bottom_frame,
			text=button_nf[i][0],
			command=button_nf[i][1],
			width=20,
			state="disabled")
		btn.pack(pady=5, padx=20, fill=tk.X)
		buttons.append(btn)

	grid = NumberGrid(right_frame)
	root.mainloop()


def load_mod(path: str) -> CDLL:
	if path == "mod2":
		import mod2
		return mod2
	
	mod = CDLL(path)
	mod.make.restype = c_void_p

	mod.clear.argtypes = [c_void_p]

	mod.destroy.argtypes = [c_void_p]

	mod.getSize.argtypes = [c_void_p]
	mod.getSize.restype = c_int

	mod.isEmpty.argtypes = [c_void_p]
	mod.isEmpty.restype = c_bool

	mod.pushFront.argtypes = [c_void_p, c_int]
	mod.pushBack.argtypes = [c_void_p, c_int]
	mod.fillRandom.argtypes = [c_void_p, c_int]

	mod.popFront.argtypes = [c_void_p]
	mod.popFront.restype = c_int

	mod.popBack.argtypes = [c_void_p]
	mod.popBack.restype = c_int

	mod.display.argtypes = [c_void_p, POINTER(c_int), c_int]
	mod.display.restype = c_int
	return mod


if __name__ == "__main__":
	mod = None
	struct = None
	mods = {
		"C++": load_mod("./mod1.dll"),
		"Python": load_mod("mod2"),
		"STL": load_mod("./mod3.dll"),
	}
	combobox_options = list(mods.keys())
	main()