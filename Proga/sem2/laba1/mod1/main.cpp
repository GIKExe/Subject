#include "main.h"
// #include <iostream>

struct Element {
	int data;
	Element *prev;
	Element *next;
};

Export Element* make() {
	Element* ptr = new Element;
	ptr->data = 0;
	ptr->prev = nullptr;
	ptr->next = nullptr;
	return ptr;
}

Export void clear(Element* str) {
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

Export void destroy(Element* str) {
	clear(str);
	delete str;
}

Export int getData(Element* str) {
	return str->data;
}

Export Element* getPrev(Element* ptr) {
	return ptr->prev;
}

Export Element* getNext(Element* ptr) {
	return ptr->next;
}

Export void pushStart(Element* str, int value) {
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

Export void pushEnd(Element* str, int value) {
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

Export int popStart(Element* str) {
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

Export int popEnd(Element* str) {
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

// gcc -c main.cpp
// gcc -shared -o mod1.dll main.o -lstdc++
