#pragma once
#define Export __declspec(dllexport)

extern "C" {
	Export void* make();
	Export void clear(void* handle);
	Export void destroy(void* handle);

	Export int getSize(void* handle);
	Export bool isEmpty(void* handle);

	Export void pushFront(void* handle, int value);
	Export void pushBack(void* handle, int value);

	Export int popFront(void* handle);
	Export int popBack(void* handle);
	
	Export int display(void* handle, int* buffer, int buffer_size);
}

// g++ -shared -o mod1.dll mod1.cpp -static-libgcc -static-libstdc++ -static
// g++ -shared -o mod3.dll mod3.cpp -static-libgcc -static-libstdc++ -static