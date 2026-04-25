#pragma once
#define Export __declspec(dllexport)

extern "C" {
	Export void external_sort(
		const char *path, 
		int keyIndex, 
		bool ascending, 
		void (*progressCallback)(float)
	);
}

