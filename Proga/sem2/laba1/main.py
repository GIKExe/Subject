import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from random import randint
import os, sys
from ctypes import *

from utils import *

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


class Redirector:
	def __init__(self, text_widget):
		self.text_widget = text_widget
		
	def write(self, string):
		self.text_widget.configure(state="normal")
		self.text_widget.insert(tk.END, string)
		self.text_widget.see(tk.END)  # Прокрутка до конца
		self.text_widget.configure(state="disabled")


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
		self.clear_grid()  # сначала очищаем
		
		# Рассчитываем максимальное количество столбцов
		max_cols = self.master.winfo_width() // self.cell_width
		
		# Если чисел меньше, чем может поместиться в одну строку
		if len(numbers) < max_cols:
			max_cols = len(numbers)
		
		for i, number in enumerate(numbers):
			row = i // max_cols
			col = i % max_cols
			
			# Создаем метку с числом
			label = ttk.Label(
				self.master,
				text=str(number),
				width=10,
				relief="ridge",  # рамка вокруг ячейки
				padding=0,
				anchor="center"
			)
			
			# Размещаем с помощью place для фиксированных координат
			x = col * (self.cell_width)
			y = row * (self.cell_height)
			
			label.place(
				x=x,
				y=y,
				width=self.cell_width,
				height=self.cell_height
			)
			
			self.labels.append(label)


def check(ptr: Element) -> Element:
	if not ptr:
		return None
	return ptr


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

	def draw():
		ptr = check(mod.getPrev(struct))
		nums = []
		while ptr != None:
			nums.append(mod.getData(ptr))
			ptr = check(mod.getNext(ptr))
		grid.fill_grid(nums)

	def f1():
		mod.clear(struct)
		print("дек очищен")
		draw()

	def f3():
		value = randint(-2**31, 2**31-1)
		mod.pushEnd(struct, value)
		print(f"случайное помещено в конец: {value}");
		draw()

	def f4():
		value = mod.getData(struct)
		print(f"размер дека: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))

	def f5():
		value = entry.get()
		if not value: return
		value = int(value)
		mod.pushStart(struct, value)
		print(f"помещено в начало: {value}")
		draw()

	def f6():
		value = entry.get()
		if not value: return
		value = int(value)
		mod.pushEnd(struct, value)
		print(f"помещено в конец: {value}")
		draw()
	
	def f7():
		if mod.getData(struct) < 1: return
		value = mod.popStart(struct)
		print(f"получено из начала: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))
		draw()

	def f8():
		if mod.getData(struct) < 1: return
		value = mod.popEnd(struct)
		print(f"получено из конца: {value}")
		entry.delete(0, tk.END)
		entry.insert(0, str(value))
		draw()

	buttons = []
	button_nf = (
		["Очистить", f1],
		["Заполнить", f6],
		["Заполнить случайным", f3],
		["Узнать размер", f4],
		["Вставить в начало", f5],
		["Вставить в конец", f6],
		["Забрать из начала", f7],
		["Забрать из конца", f8],
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


def load_mod1():
	mod1 = CDLL("./mod1.dll")
	mod1.make.restype = POINTER(Element)

	mod1.clear.argtypes = [POINTER(Element)]

	mod1.destroy.argtypes = [POINTER(Element)]

	mod1.getData.argtypes = [POINTER(Element)]
	mod1.getData.restype = c_int

	mod1.getPrev.argtypes = [POINTER(Element)]
	mod1.getPrev.restype = POINTER(Element)

	mod1.getNext.argtypes = [POINTER(Element)]
	mod1.getNext.restype = POINTER(Element)

	mod1.pushStart.argtypes = [POINTER(Element), c_int]
	mod1.pushEnd.argtypes = [POINTER(Element), c_int]

	mod1.popStart.argtypes = [POINTER(Element)]
	mod1.popStart.restype = c_int

	mod1.popEnd.argtypes = [POINTER(Element)]
	mod1.popEnd.restype = c_int
	return mod1


def load_mod2():
	import mod2 as mod2
	return mod2


if __name__ == "__main__":
	mod = None
	struct = None
	mods = {
		"C++": load_mod1(),
		"Python": load_mod2(),
	}
	combobox_options = list(mods.keys())
	main()