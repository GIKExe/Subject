#include "mod.h"

#include <time.h>
#include <stdlib.h>

#include <deque>
// #include <cstddef>

bool initRandom = false;
#define IntDeque std::deque<int>
#define Cast(x) static_cast<IntDeque*>(x)

Export void* make() {
	if (!initRandom) {
		srand(time(0));
		initRandom = true;
	}
	try {
		return new IntDeque();
	} catch (...) {
		return nullptr;
	}
}

Export void destroy(void* handle) {
	if (handle == nullptr) return; 
	delete Cast(handle);
}

Export void clear(void* handle) {
	if (handle == nullptr) return; 
	Cast(handle)->clear();
}

Export int getSize(void* handle) {
	if (handle == nullptr) return 0; 
	return Cast(handle)->size();
}

Export bool isEmpty(void* handle) {
	if (handle == nullptr) return false; 
	return Cast(handle)->empty();
}

Export void pushFront(void* handle, int value) {
	if (handle == nullptr) return; 
	Cast(handle)->push_front(value);
}

Export void pushBack(void* handle, int value) {
	if (handle == nullptr) return; 
	Cast(handle)->push_back(value);
}

Export void fillRandom(void* handle, int value) {
	if (handle == nullptr) return; 
	auto *deq = Cast(handle);
	if (value < 0) return;
	for (; value > 0; value--) {
		unsigned int x = (rand() << 17) + (rand() << 2) + (rand() & 3);
		pushBack(handle, (signed int) x);
	}
}

Export int popFront(void* handle) {
	if (handle == nullptr) return 0; 
	auto *deq = Cast(handle);
	if (deq->empty()) return 0;
	auto value = deq->front();
	deq->pop_front();
	return value;
}

Export int popBack(void* handle) {
	if (handle == nullptr) return 0; 
	auto *deq = Cast(handle);
	if (deq->empty()) return 0;
	auto value = deq->back();
	deq->pop_back();
	return value;
}

Export int display(void* handle, int* buffer, int buffer_size) {
	auto* d = Cast(handle);
	int count = d->size();
	if (buffer && count <= buffer_size) {
		std::copy(d->begin(), d->end(), buffer);
		return count;
	}; return 0;
}