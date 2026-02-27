#pragma once

#define Export extern "C" __declspec(dllexport)

// typedef struct Element;
struct Element;

Export Element* make();
Export void clear(Element* str);
Export void destroy(Element* str);

Export int getData(Element* str);
Export Element* getPrev(Element* ptr);
Export Element* getNext(Element* ptr);

Export void pushStart(Element* str, int value);
Export void pushEnd(Element* str, int value);

Export int popStart(Element* str);
Export int popEnd(Element* str);

