
@echo off
g++ -shared -o mod1.dll mod1.cpp -static -Os -s
g++ -shared -o mod3.dll mod3.cpp -static -Os -s
