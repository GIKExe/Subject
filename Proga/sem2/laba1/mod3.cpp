#include "mod.h"

#include <deque>
#include <cstddef>

#define IntDeque std::deque<int>
#define Cast(x) static_cast<IntDeque*>(x)

Export void* make() {
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

Export int deque_try_front(void* handle, int* out_value) {
	auto* d = Cast(handle);
	if (d->empty() || !out_value) return 0;
	*out_value = d->front();
	return 1;
}

Export int deque_try_back(void* handle, int* out_value) {
	auto* d = Cast(handle);
	if (d->empty() || !out_value)
		return 0;
	*out_value = d->back();
	return 1;
}

Export int display(void* handle, int* buffer, int buffer_size) {
	auto* d = Cast(handle);
	int count = d->size();

	if (buffer && count <= buffer_size) {
		std::copy(d->begin(), d->end(), buffer);
		return count;
	}
	return 0;
}