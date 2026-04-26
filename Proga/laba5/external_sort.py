import os
import struct
import heapq
import shutil
from pathlib import Path
import numpy as np
import gc
from typing import Callable

# Константы (в соответствии с C++ версией)
READER_SIZE = 1024 * 1024 * 10  # 10 MiB - буфер чтения
MAX_RECORDS = 500_000
WRITER_SIZE = 1024 * 1024 * 10  # 10 MiB - буфер записи

# Определяем numpy тип данных (соответствует C++ __attribute__((packed)) Record)
# Строковые поля (S) фиксированной длины, little-endian типы для чисел
record_dtype = np.dtype([
	('nickname', 'S24'),
	('uuid', 'S37'),
	('reg_date', 'S11'),
	('level', '<u4'),
	('hours', '<f4'),
	('vac_ban', 'b1')
], align=False)  # align=False гарантирует плотную упаковку ровно в 81 байт

class MergeNode:
	"""Узел для приоритетной очереди в фазе слияния"""
	__slots__ = ['key', 'file_index', 'raw_bytes', 'ascending']

	def __init__(self, key, file_index: int, raw_bytes: bytes, ascending: bool):
		self.key = key
		self.file_index = file_index
		self.raw_bytes = raw_bytes
		self.ascending = ascending

	def __lt__(self, other):
		# Если ascending == False, инвертируем оператор сравнения, как в C++ лямбде
		if self.ascending:
			return self.key < other.key
		return self.key > other.key

def extract_key(raw_bytes: bytes, keyIndex: int):
	"""
	Извлечение ключа для сортировки из 81-байтной записи
	Учитывает обрезку нулевых байтов (\\x00) для строковых полей.
	"""
	if keyIndex == 0:
		return raw_bytes[0:24].split(b'\x00', 1)[0]
	elif keyIndex == 1:
		return raw_bytes[24:61].split(b'\x00', 1)[0]
	elif keyIndex == 2:
		return raw_bytes[61:72].split(b'\x00', 1)[0]
	elif keyIndex == 3:
		return struct.unpack('<I', raw_bytes[72:76])[0]
	elif keyIndex == 4:
		return struct.unpack('<f', raw_bytes[76:80])[0]
	elif keyIndex == 5:
		return raw_bytes[80] != 0

def _sort_and_dump(records: np.ndarray, total: int, keyIndex: int, ascending: bool, temp_dir: Path, file_idx: int):
	"""Сортировка текущего блока numpy массива на месте и сохранение в бинарный файл"""
	fields = ['nickname', 'uuid', 'reg_date', 'level', 'hours', 'vac_ban']
	sort_field = fields[keyIndex]
	
	# Берем срез (view) реально заполненных данных
	view = records[:total]
	
	# Сортировка O(N log N) на уровне C-библиотек Numpy
	view.sort(order=sort_field)
	
	# Если убывание, просто разворачиваем view за O(1) память, не копируя данные
	if not ascending:
		view = view[::-1]
		
	out_path = temp_dir / f"r{file_idx}.tmp"
	view.tofile(out_path)  # Сброс бинарного дампа

def external_sort(path: str, keyIndex: int, ascending: bool, progressCallback: Callable[[float], None]) -> None:
	temp_dir = Path("temp")
	if temp_dir.exists():
		shutil.rmtree(temp_dir)
	temp_dir.mkdir(parents=True, exist_ok=True)

	total_file_size = os.path.getsize(path)
	if total_file_size == 0:
		return

	# Фаза 1: Блочное Чтение и Сортировка (Разделение)
	# Пиковое потребление памяти здесь: 77.2 МБ (records) + 10 МБ (reader_buf) = ~87.2 МБ
	records = np.empty(MAX_RECORDS, dtype=record_dtype)
	reader_buf = bytearray(READER_SIZE)
	
	total_files = 0
	total_records = 0
	read_it = 0

	progressCallback(0.0)

	with open(path, "rb") as f_in:
		while True:
			# Чтение напрямую в предвыделенный буфер для экономии памяти
			bytes_read = f_in.readinto(reader_buf)
			if bytes_read == 0:
				break
			
			# Поиск последнего перевода строки, чтобы не разрывать запись
			last_newline = reader_buf.rfind(b'\n', 0, bytes_read)
			if last_newline == -1:
				last_newline = bytes_read - 1
				
			# Откат файлового курсора до неполной строки
			f_in.seek(last_newline + 1 - bytes_read, os.SEEK_CUR)
			read_it += (last_newline + 1)
			
			# Парсинг текущего 10 МБ буфера байтовыми операциями (без создания списков)
			idx = 0
			while idx <= last_newline:
				if total_records == MAX_RECORDS:
					_sort_and_dump(records, total_records, keyIndex, ascending, temp_dir, total_files)
					total_files += 1
					total_records = 0
					progressCallback(read_it / total_file_size)
				
				# Достигнут конец безопасного участка
				if idx == last_newline + 1:
					break
				
				# Ручной парсинг индексов по запятой
				comma1 = reader_buf.find(b',', idx, last_newline + 1)
				if comma1 == -1:
					break
				records['nickname'][total_records] = bytes(reader_buf[idx:comma1])
				
				comma2 = reader_buf.find(b',', comma1 + 1, last_newline + 1)
				records['uuid'][total_records] = bytes(reader_buf[comma1+1:comma2])
				
				comma3 = reader_buf.find(b',', comma2 + 1, last_newline + 1)
				records['reg_date'][total_records] = bytes(reader_buf[comma2+1:comma3])
				
				comma4 = reader_buf.find(b',', comma3 + 1, last_newline + 1)
				records['level'][total_records] = int(reader_buf[comma3+1:comma4])
				
				comma5 = reader_buf.find(b',', comma4 + 1, last_newline + 1)
				records['hours'][total_records] = float(reader_buf[comma4+1:comma5])
				
				newline = reader_buf.find(b'\n', comma5 + 1, last_newline + 1)
				if newline == -1:
					newline = last_newline
				# Учтем возможный \r от Windows (если файл формата CRLF)
				records['vac_ban'][total_records] = reader_buf[comma5+1:newline].startswith(b'true')
				
				idx = newline + 1
				total_records += 1

	# Запись последнего недозаполненного блока
	if total_records > 0:
		_sort_and_dump(records, total_records, keyIndex, ascending, temp_dir, total_files)
		total_files += 1
		progressCallback(read_it / total_file_size)

	# ОСВОБОЖДЕНИЕ ПАМЯТИ: перед аллокацией 95 МБ удаляем массив records (77 МБ)
	del records
	del reader_buf
	gc.collect()

	progressCallback(0.0)

	# Фаза 2: K-Way Merge (Слияние)
	# Открываем все временные файлы для чтения
	open_files = []
	pq = []
	
	for i in range(total_files):
		f = open(temp_dir / f"r{i}.tmp", "rb")
		raw_bytes = f.read(81)  # Читаем ровно 1 структуру (81 байт)
		if len(raw_bytes) == 81:
			key = extract_key(raw_bytes, keyIndex)
			heapq.heappush(pq, MergeNode(key, i, raw_bytes, ascending))
		open_files.append(f)

	# Пиковое потребление памяти здесь: 95 МБ (writer_buf)
	writer_buf = bytearray(WRITER_SIZE)
	writer_pos = 0
	read_out_size = 0

	with open(f"{path}.sorted", "wb") as f_out:
		while pq:
			node = heapq.heappop(pq)
			raw_bytes = node.raw_bytes
			f_idx = node.file_index
			
			# Десериализация (парсим бинарные данные 81 байт)
			nick = raw_bytes[0:24].split(b'\x00', 1)[0]
			uuid = raw_bytes[24:61].split(b'\x00', 1)[0]
			date = raw_bytes[61:72].split(b'\x00', 1)[0]
			level = struct.unpack('<I', raw_bytes[72:76])[0]
			hours = struct.unpack('<f', raw_bytes[76:80])[0]
			ban_str = b"true" if raw_bytes[80] != 0 else b"false"
			
			# Векторное форматирование байт (% оператор для bytes очень быстр и не создает Unicode-строк)
			row = b"%b,%b,%b,%d,%.3f,%b\n" % (nick, uuid, date, level, hours, ban_str)
			row_len = len(row)
			
			# Запись в буфер слияния
			writer_buf[writer_pos:writer_pos+row_len] = row
			writer_pos += row_len
			read_out_size += row_len
			
			# Сброс буфера (по аналогии с C++: WRITER_SIZE - 1000)
			if writer_pos > WRITER_SIZE - 1000:
				f_out.write(memoryview(writer_buf)[:writer_pos])
				progressCallback(read_out_size / total_file_size)
				writer_pos = 0
				
			# Чтение следующей записи из того же файла, откуда была взята минимальная
			next_bytes = open_files[f_idx].read(81)
			if len(next_bytes) == 81:
				node.key = extract_key(next_bytes, keyIndex)
				node.raw_bytes = next_bytes
				heapq.heappush(pq, node)
				
		# Сброс остатков буфера
		if writer_pos > 0:
			f_out.write(memoryview(writer_buf)[:writer_pos])
			read_out_size += writer_pos
			p: float = read_out_size / total_file_size
			if p > 1.0:
				p = 1.0
			progressCallback(p)

	# Очистка ресурсов
	for f in open_files:
		f.close()
	shutil.rmtree(temp_dir)

if __name__ == "__main__":
	def progress(p: float):
		print(f"Прогресс: {p * 100:.2f}%")

	# Сортировка файла: path, keyIndex, ascending, callback
	# Индексы:
	# 0 = nickname
	# 1 = uuid
	# 2 = reg_date
	# 3 = level
	# 4 = hours
	# 5 = vac_ban
	
	# Пример вызова, эквивалентный `external_sort("data.csv", 2, false, progress);`
	external_sort("data.csv", 0, True, progress)