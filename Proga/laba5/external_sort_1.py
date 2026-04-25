#!/usr/bin/env python3
# external_sort.py
# Реализация внешней сортировки CSV-файла с жёстким ограничением памяти (<100 МБ)
# Используются: numpy для хранения блоков, numba для быстрого парсинга,
# heapq для k-way слияния, ручная сериализация без модуля csv.
# Временные файлы хранят записи в бинарном packed-формате (81 байт).

import os
import struct
import heapq
# import tempfile
import shutil
from pathlib import Path
from typing import Callable
import numpy as np
import numba

# ----------------------------------------------------------------------
# Константы (аналоги C++ версии)
READER_SIZE = 10 * 1024 * 1024          # 10 MiB буфер для чтения исходного CSV
MAX_RECORDS = 1_000_000                 # 1 млн записей в блоке (~81 MiB)
WRITER_SIZE = 95 * 1024 * 1024          # 95 MiB буфер для вывода CSV на этапе слияния
CHUNK_SIZE_WRITE = 10_000               # запись обратного порядка кусками по 10k записей

# ----------------------------------------------------------------------
# Описание структуры записи в памяти (little-endian, packed, 81 байт)
# Поля: nickname[24] + uuid[37] + reg_date[11] + level(ui32) + hours(fp32) + vac_ban(bool)
RECORD_DTYPE = np.dtype([
	('nickname', 'S24'),
	('uuid', 'S37'),
	('reg_date', 'S11'),
	('level', '<u4'),
	('hours', '<f4'),
	('vac_ban', 'b1')
])
assert RECORD_DTYPE.itemsize == 81, "Неверный размер записи"

# ----------------------------------------------------------------------
# Функция быстрого парсинга блока текстового CSV в numpy-массив.
# Используется Numba для JIT-компиляции – работает на скорости близкой к C.
@numba.jit(nopython=True)
def parse_chunk(data: bytes, records: np.ndarray, start_idx: int) -> int:
	"""
	Парсит блок байт (текстовый CSV, строки разделены \n) и заполняет
	numpy structured array начиная с индекса start_idx.
	Возвращает количество добавленных записей.
	"""
	i = start_idx
	pos = 0
	n = len(data)
	while pos < n:
		# nickname – до запятой
		ns = pos
		while pos < n and data[pos] != ord(','):
			pos += 1
		nickname = data[ns:pos]
		pos += 1

		# uuid
		us = pos
		while pos < n and data[pos] != ord(','):
			pos += 1
		uuid = data[us:pos]
		pos += 1

		# reg_date
		rs = pos
		while pos < n and data[pos] != ord(','):
			pos += 1
		reg_date = data[rs:pos]
		pos += 1

		# level – целое
		ls = pos
		while pos < n and data[pos] != ord(','):
			pos += 1
		level_bytes = data[ls:pos]
		level = 0
		for b in level_bytes:
			level = level * 10 + (b - 48)
		pos += 1

		# hours – float
		hs = pos
		while pos < n and data[pos] != ord(','):
			pos += 1
		hours_bytes = data[hs:pos]
		# разбор с десятичной точкой
		dot = -1
		for idx, b in enumerate(hours_bytes):
			if b == ord('.'):
				dot = idx
				break
		if dot == -1:                     # целое число
			hours = 0.0
			for b in hours_bytes:
				hours = hours * 10.0 + (b - 48)
		else:
			int_part = 0
			for b in hours_bytes[:dot]:
				int_part = int_part * 10 + (b - 48)
			frac_part = 0
			frac_div = 1
			for b in hours_bytes[dot+1:]:
				frac_part = frac_part * 10 + (b - 48)
				frac_div *= 10
			hours = int_part + frac_part / frac_div
		pos += 1

		# vac_ban – "true"/"false"
		vs = pos
		while pos < n and data[pos] != ord('\n'):
			pos += 1
		vac_ban_bytes = data[vs:pos]
		vac_ban = (len(vac_ban_bytes) == 4 and
				   vac_ban_bytes[0] == ord('t') and
				   vac_ban_bytes[1] == ord('r') and
				   vac_ban_bytes[2] == ord('u') and
				   vac_ban_bytes[3] == ord('e'))
		pos += 1   # пропустить '\n'

		# запись в numpy массив
		records['nickname'][i] = nickname
		records['uuid'][i] = uuid
		records['reg_date'][i] = reg_date
		records['level'][i] = level
		records['hours'][i] = hours
		records['vac_ban'][i] = vac_ban
		i += 1
	return i - start_idx

# ----------------------------------------------------------------------
# Преобразование бинарной записи (81 байт) в CSV-строку (байты) для вывода.
def serialize_record(record_bytes: bytes) -> bytes:
	"""Распаковывает 81 байт в поля и формирует байтовую CSV-строку, оканчивающуюся \n"""
	nickname, uuid, reg_date, level, hours, vac_ban = struct.unpack('<24s37s11sIf?', record_bytes)
	# обрезаем нулевые байты в строках фиксированной длины
	nickname = nickname.split(b'\x00', 1)[0]
	uuid = uuid.split(b'\x00', 1)[0]
	reg_date = reg_date.split(b'\x00', 1)[0]
	vac_ban_str = b'true' if vac_ban else b'false'
	# Формируем bytearray, чтобы избежать множественных конкатенаций
	out = bytearray()
	out.extend(nickname)
	out.append(ord(','))
	out.extend(uuid)
	out.append(ord(','))
	out.extend(reg_date)
	out.append(ord(','))
	out.extend(str(level).encode())
	out.append(ord(','))
	# ровно 3 знака после запятой, как в C++ версии
	out.extend(f"{hours:.3f}".encode())
	out.append(ord(','))
	out.extend(vac_ban_str)
	out.append(ord('\n'))
	return bytes(out)

# ----------------------------------------------------------------------
# Вспомогательный класс для элементов в куче при слиянии.
class RecordWrapper:
	__slots__ = ('record_bytes', 'file_idx', 'key_value', 'ascending')
	def __init__(self, record_bytes: bytes, file_idx: int, key_idx: int, ascending: bool):
		self.record_bytes = record_bytes
		self.file_idx = file_idx
		self.ascending = ascending
		# распаковываем только нужное поле для сравнения
		fields = struct.unpack('<24s37s11sIf?', record_bytes)
		# извлекаем поле по индексу key_idx
		if key_idx == 0:         # nickname
			val = fields[0].split(b'\x00', 1)[0]
		elif key_idx == 1:       # uuid
			val = fields[1].split(b'\x00', 1)[0]
		elif key_idx == 2:       # reg_date
			val = fields[2].split(b'\x00', 1)[0]
		elif key_idx == 3:       # level
			val = fields[3]
		elif key_idx == 4:       # hours
			val = fields[4]
		else:                    # vac_ban
			val = fields[5]
		self.key_value = val

	def __lt__(self, other):
		# для min-heap: если ascending == True, то меньший key_value имеет приоритет,
		# если ascending == False, то больший key_value имеет приоритет (т.е. пирамида на максимум)
		if self.ascending:
			return self.key_value < other.key_value
		else:
			return self.key_value > other.key_value

# ----------------------------------------------------------------------
# Основная функция внешней сортировки
def external_sort(path: str, key_idx: int, ascending: bool,
				  progress_cb: Callable[[float], None]) -> None:
	"""
	path        – путь к входному CSV-файлу (разделитель ',', строки заканчиваются \n)
	key_idx     – индекс поля для сортировки (0=nickname,1=uuid,2=reg_date,3=level,4=hours,5=vac_ban)
	ascending   – True – по возрастанию, False – по убыванию
	progress_cb – callback, принимающий float от 0.0 до 1.0
	"""
	# ------------------------------------------------------------------
	# ФАЗА 1: разбиение на отсортированные блоки
	# ------------------------------------------------------------------
	temp_dir = Path("temp_external_sort")
	temp_dir.mkdir(exist_ok=True)

	# Открываем исходный файл в бинарном режиме
	with open(path, 'rb') as infile:
		infile.seek(0, os.SEEK_END)
		total_file_size = infile.tell()
		infile.seek(0, os.SEEK_SET)

		# Выделяем память: массив для хранения блока записей (MAX_RECORDS * 81 байт ≈ 81 MiB)
		records = np.empty(MAX_RECORDS, dtype=RECORD_DTYPE)
		buffer = bytearray(READER_SIZE)          # буфер чтения 10 MiB
		pending = b''                            # остаток от предыдущего чтения
		total_records_in_block = 0
		total_files = 0
		bytes_read_total = 0                     # для прогресса (реальные байты из файла)
		progress_cb(0.0)

		while True:
			# Читаем очередной кусок из файла
			chunk = infile.read(READER_SIZE)
			if not chunk and not pending:
				break

			data = pending + chunk
			# Ищем последний символ перевода строки в data
			last_nl = data.rfind(b'\n')
			if last_nl == -1:
				# Нет ни одного \n – файл повреждён, но продолжим (обработаем как одну строку)
				valid_part = data
				pending = b''
			else:
				valid_part = data[:last_nl+1]      # включая последний \n
				pending = data[last_nl+1:]          # неполная строка на следующий раз

			# Парсим valid_part в records, начиная с total_records_in_block
			if valid_part:
				n_parsed = parse_chunk(valid_part, records, total_records_in_block)
				total_records_in_block += n_parsed
				bytes_read_total += len(valid_part)
				progress_cb(min(bytes_read_total / total_file_size, 1.0))

			# Если блок заполнен или файл закончился (pending может быть пуст)
			if total_records_in_block >= MAX_RECORDS or (not chunk and not pending):
				# Сортировка блока (in-place) по нужному полю
				rec_view = records[:total_records_in_block]
				# Используем метод sort(order='field') – без копирования
				field_names = ['nickname', 'uuid', 'reg_date', 'level', 'hours', 'vac_ban']
				rec_view.sort(order=field_names[key_idx])
				# Запись во временный файл (бинарный, packed)
				tmp_path = temp_dir / f"r{total_files}.tmp"
				with open(tmp_path, 'wb') as tmp_file:
					if ascending:
						rec_view.tofile(tmp_file)
					else:
						# Для убывающего порядка записываем блоки в обратном порядке кусками,
						# чтобы не выделять дополнительную память на всю копию.
						chunk_sz = CHUNK_SIZE_WRITE
						for start in range(total_records_in_block - 1, -1, -chunk_sz):
							end = max(start - chunk_sz + 1, 0)
							# Срез records[end:start+1] – view, [::-1] – view с обратным порядком
							# tobytes() создаст копию только этого маленького куска.
							block = records[end:start+1][::-1]
							tmp_file.write(block.tobytes())
				total_files += 1
				total_records_in_block = 0
				# После записи блока сообщаем прогресс (остаёмся на том же значении)
				progress_cb(min(bytes_read_total / total_file_size, 1.0))

			if not chunk:
				break

	# ------------------------------------------------------------------
	# ФАЗА 2: k-way слияние временных файлов
	# ------------------------------------------------------------------
	if total_files == 0:
		# Пустой входной файл – просто создаём пустой выходной
		with open(path + ".sorted", 'wb') as outfile:
			pass
		shutil.rmtree(temp_dir)
		progress_cb(1.0)
		return

	# Открываем все временные файлы для чтения
	file_handles = []
	heap = []
	for i in range(total_files):
		f = open(temp_dir / f"r{i}.tmp", 'rb')
		# Читаем первую запись (81 байт)
		raw = f.read(81)
		if len(raw) == 81:
			wrapper = RecordWrapper(raw, i, key_idx, ascending)
			heapq.heappush(heap, wrapper)
		file_handles.append(f)

	# Подготавливаем выходной файл
	out_path = path + ".sorted"
	outfile = open(out_path, 'wb')
	out_buffer = bytearray(WRITER_SIZE)    # буфер вывода 95 MiB
	out_pos = 0
	bytes_written_total = 0
	progress_cb(0.0)

	# Слияние
	while heap:
		wrapper = heapq.heappop(heap)
		# Сериализуем запись в CSV и добавляем в буфер
		csv_line = serialize_record(wrapper.record_bytes)
		line_len = len(csv_line)
		if out_pos + line_len > WRITER_SIZE - 1000:   # оставляем запас
			# Сброс буфера в файл
			outfile.write(out_buffer[:out_pos])
			bytes_written_total += out_pos
			progress_cb(min(bytes_written_total / total_file_size, 1.0))
			out_pos = 0
		out_buffer[out_pos:out_pos+line_len] = csv_line
		out_pos += line_len

		# Читаем следующую запись из того же файла
		f = file_handles[wrapper.file_idx]
		raw = f.read(81)
		if len(raw) == 81:
			new_wrapper = RecordWrapper(raw, wrapper.file_idx, key_idx, ascending)
			heapq.heappush(heap, new_wrapper)

	# Сброс остатка буфера
	if out_pos > 0:
		outfile.write(out_buffer[:out_pos])
		bytes_written_total += out_pos
		progress_cb(min(bytes_written_total / total_file_size, 1.0))

	# Закрываем всё и удаляем временную директорию
	outfile.close()
	for f in file_handles:
		f.close()
	shutil.rmtree(temp_dir)
	progress_cb(1.0)

# ----------------------------------------------------------------------
# Пример использования (аналог main() из C++)
def main():
	def progress(p: float) -> None:
		print(f"Прогресс: {p*100:.2f}%")

	# Сортировка по полю reg_date (индекс 2) по убыванию (False)
	# Замените "data.csv" на путь к вашему файлу
	external_sort("data.csv", key_idx=2, ascending=False, progress_cb=progress)

if __name__ == "__main__":
	main()