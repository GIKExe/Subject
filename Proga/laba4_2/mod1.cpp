#include "mod.h"
#include <time.h>
#include <stdlib.h>

bool initRandom = false;

struct Element {
	int data;
	Element *prev;
	Element *next;
};

Export void* make() {
	if (!initRandom) {
		srand(time(0));
		initRandom = true;
	}
	Element* ptr = new Element;
	ptr->data = 0;
	ptr->prev = nullptr;
	ptr->next = nullptr;
	return ptr;
}

Export void clear(void* handle) {
	Element* str = (Element*) handle;
	Element* ptr = str->prev;
	while (ptr != nullptr) {
		Element* next = ptr->next;
		delete ptr;
		ptr = next;
	}
	str->prev = nullptr;
	str->next = nullptr;
	str->data = 0;
}

Export void destroy(void* handle) {
	Element* str = (Element*) handle;
	clear(str);
	delete str;
}

Export int getSize(void* handle) {
	Element* str = (Element*) handle;
	return str->data;
}

Export bool isEmpty(void* handle) {
	Element* str = (Element*) handle;
	return str->data == 0;
}

Export void pushFront(void* handle, int value) {
	Element* str = (Element*) handle;
	Element* ptr = new Element;
	ptr->data = value;
	ptr->prev = nullptr;
	ptr->next = nullptr;
	if (str->prev == nullptr) {
		str->prev = ptr;
		str->next = ptr;
	} else {
		ptr->next = str->prev;
		str->prev->prev = ptr;
		str->prev = ptr;
	}
	str->data++;
}

Export void pushBack(void* handle, int value) {
	Element* str = (Element*) handle;
	Element* ptr = new Element;
	ptr->data = value;
	ptr->prev = nullptr;
	ptr->next = nullptr;
	if (str->next == nullptr) {
		str->prev = ptr;
		str->next = ptr;
	} else {
		ptr->prev = str->next;
		str->next->next = ptr;
		str->next = ptr;
	}
	str->data++;
}

Export void fillRandom(void* handle, int value) {
	Element* str = (Element*) handle;
	if (value < 0) return;
	for (; value > 0; value--) {
		unsigned int x = (rand() << 17) + (rand() << 2) + (rand() & 3);
		pushBack(handle, (signed int) x);
	}
}

Export int popFront(void* handle) {
	Element* str = (Element*) handle;
	Element* ptr = str->prev;
	int value = ptr->data;
	str->prev = ptr->next;
	str->data--;
	if (str->prev != nullptr) {
		str->prev->prev = nullptr;
	} else {
		str->next = nullptr;
	}
	delete ptr;
	return value;
}

Export int popBack(void* handle) {
	Element* str = (Element*) handle;
	Element* ptr = str->next;
	int value = ptr->data;
	str->next = ptr->prev;
	str->data--;
	if (str->next != nullptr) {
		str->next->next = nullptr;
	} else {
		str->prev = nullptr;
	}
	delete ptr;
	return value;
}

Export int display(void* handle, int* buffer, int buffer_size) {
	Element* str = (Element*) handle;
	if (buffer && str->data <= buffer_size) {
		int count = 0;
		Element* ptr = str->prev;
		while (ptr != nullptr) {
			buffer[count] = ptr->data;
			ptr = ptr->next;
			count++;
		}; return count;
	}; return 0;
}