from random import randint


class Element:
	def __init__(self):
		self.data: int = 0
		self.prev: Element = None 
		self.next: Element = None

def make() -> Element:
	return Element()

def clear(str: Element) -> None:
	ptr = str.prev;
	while (ptr != None):
		next = ptr.next;
		del ptr # типо удаление
		ptr = next
	str.prev = None
	str.next = None
	str.data = 0

def destroy(str: Element) -> None:
	clear(str)
	del str

def getSize(str: Element) -> int:
	return str.data

def isEmpty(str: Element) -> bool:
	return str.data == 0

def pushFront(str: Element, value: int) -> None:
	ptr = Element()
	ptr.data = value
	ptr.prev = None
	ptr.next = None
	if str.prev == None:
		str.prev = ptr
		str.next = ptr
	else:
		ptr.next = str.prev
		str.prev.prev = ptr 
		str.prev = ptr
	str.data += 1

def pushBack(str: Element, value: int) -> None:
	ptr = Element()
	ptr.data = value
	ptr.prev = None
	ptr.next = None
	if str.next == None:
		str.prev = ptr
		str.next = ptr
	else:
		ptr.prev = str.next
		str.next.next = ptr
		str.next = ptr
	str.data += 1

def fillRandom(str: Element, value: int) -> None:
	if value < 0: return
	while value > 0:
		pushBack(str, randint(-2**31, 2**31-1))
		value -= 1

def popFront(str: Element) -> int:
	ptr = str.prev
	value = ptr.data
	str.prev = ptr.next
	str.data -= 1
	if str.prev != None:
		str.prev.prev = None
	else:
		str.next = None
	del ptr
	return value

def popBack(str: Element) -> int:
	ptr = str.next
	value = ptr.data
	str.next = ptr.prev
	str.data -= 1
	if str.next != None:
		str.next.next = None
	else:
		str.prev = None
	del ptr
	return value

def display(str: Element, buffer: list[int], buffer_size: int) -> int:
	if str.data <= buffer_size:
		count: int = 0
		ptr = str.prev
		while (ptr != None):
			buffer[count] = ptr.data
			ptr = ptr.next
			count += 1
		return count
	return 0