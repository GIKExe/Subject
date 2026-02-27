

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

def getData(str: Element) -> int:
	return str.data

def getPrev(str: Element) -> Element:
	return str.prev

def getNext(str: Element) -> Element:
	return str.next

def pushStart(str: Element, value: int) -> None:
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

def pushEnd(str: Element, value: int) -> None:
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

def popStart(str: Element) -> int:
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

def popEnd(str: Element) -> int:
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