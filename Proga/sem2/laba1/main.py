import os, sys
from ctypes import *
import tkinter as tk
from tkinter import scrolledtext, messagebox


class Element(Structure):
	pass


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
						

def main():
	mod1 = CDLL("./mod1.dll")
	mod1.make.restype = POINTER(Element)

	mod1.clear.argtypes = [POINTER(Element)]

	mod1.destroy.argtypes = [POINTER(Element)]

	mod1.getSize.argtypes = [POINTER(Element)]
	mod1.getSize.restype = c_int

	mod1.display.argtypes = [POINTER(Element)]

	mod1.pushStart.argtypes = [POINTER(Element), c_int]
	mod1.pushEnd.argtypes = [POINTER(Element), c_int]

	mod1.popStart.argtypes = [POINTER(Element)]
	mod1.popStart.restype = c_int

	mod1.popEnd.argtypes = [POINTER(Element)]
	mod1.popEnd.restype = c_int


	root = tk.Tk()
	root.title("Дек в динамической памяти")
	root.geometry("800x600")
	root.resizable(False, False)
	
	# Создаем текстовое поле с прокруткой
	text_area = scrolledtext.ScrolledText(root, width=50, height=15, state="disabled")
	text_area.pack(padx=10, pady=10)

	# Перенаправляем stdout
	sys.stdout = Redirector(text_area)

	entry = Int32Entry(root, width=20)
	entry.pack(pady=5)

	# Добавляем кнопку для теста
	def test_print():
		print(entry.get())
		
	tk.Button(root, text="Вывести текст", command=test_print).pack(pady=5)
	
	root.mainloop()


if __name__ == "__main__":
	main()