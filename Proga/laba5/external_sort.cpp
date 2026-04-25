// #include <cstdio>
// #include <cstdlib>
#include <cstring>
#include <fstream>
#include <vector>
#include <algorithm>
// #include <chrono>
#include <filesystem>
#include <queue>
// #include <functional>
#include <string>
// #include <iomanip>
#include <iostream>
// #include <cmath>

#include "external_sort.h"

namespace fs = std::filesystem;
using namespace std;
// using namespace std::chrono;


const size_t READER_SIZE = 1024*1024*10; // 20 MiB
const size_t MAX_RECORDS = 1'000'000;    // 75 MiB 
const size_t WRITER_SIZE = 1024*1024*95; // 95 MiB

const char TRUE[] = "true";
const char FALSE[] = "false";

struct __attribute__((packed)) Record {
	char nickname[24];
	char uuid[37];
	char reg_date[11];
	unsigned int level;
	float hours;
	bool vac_ban;
};


struct MergeNode {
	Record rec;
	int fileIndex;
};


using Comparator = bool(*)(const Record&, const Record&);

static const Comparator comparators[2][6] = {
	{ // descending (по убыванию) — индекс 0
		[](const Record& a, const Record& b) { return std::strcmp(a.nickname, b.nickname) > 0; },
		[](const Record& a, const Record& b) { return std::strcmp(a.uuid, b.uuid) > 0; },
		[](const Record& a, const Record& b) { return std::strcmp(a.reg_date, b.reg_date) > 0; },
		[](const Record& a, const Record& b) { return a.level > b.level; },
		[](const Record& a, const Record& b) { return a.hours > b.hours; },
		[](const Record& a, const Record& b) { return a.vac_ban > b.vac_ban; }
	},
	{ // ascending (по возрастанию) — индекс 1
		[](const Record& a, const Record& b) { return std::strcmp(a.nickname, b.nickname) < 0; },
		[](const Record& a, const Record& b) { return std::strcmp(a.uuid, b.uuid) < 0; },
		[](const Record& a, const Record& b) { return std::strcmp(a.reg_date, b.reg_date) < 0; },
		[](const Record& a, const Record& b) { return a.level < b.level; },
		[](const Record& a, const Record& b) { return a.hours < b.hours; },
		[](const Record& a, const Record& b) { return a.vac_ban < b.vac_ban; }
	}
};


void parse(char **index, Record &rec) {
	int i;

	for (i = 0; (**index) != ','; i++, (*index)++)
		rec.nickname[i] = (**index);
	rec.nickname[i] = 0;
	(*index)++;

	for (i = 0; (**index) != ','; i++, (*index)++) {
		// if ((**index) == ' ') continue;
		rec.uuid[i] = (**index);
	}
	rec.uuid[i] = 0;
	(*index)++; 

	for (i = 0; (**index) != ','; i++, (*index)++)
		rec.reg_date[i] = (**index);
	rec.reg_date[i] = 0;
	(*index)++;

	rec.level = strtol(*index, index, 10);
	(*index)++;

	rec.hours = strtod(*index, index);
	(*index)++;

	rec.vac_ban = false;
	if (memcmp(*index, "true", 4) == 0)
		rec.vac_ban = true;
	while ((**index) != '\n') (*index)++;
	(*index)++;
}


void serialize(char **index, Record &rec) {
	int i;

	for (i = 0; rec.nickname[i] != 0; i++, (*index)++)
		(**index) = rec.nickname[i];
	(**index) = ',';
	(*index)++;

	for (i = 0; rec.uuid[i] != 0; i++, (*index)++)
		(**index) = rec.uuid[i];
	(**index) = ',';
	(*index)++;

	for (i = 0; rec.reg_date[i] != 0; i++, (*index)++)
		(**index) = rec.reg_date[i];
	(**index) = ',';
	(*index)++;

	(*index) += sprintf(*index, "%d,", rec.level);
	(*index) += sprintf(*index, "%.3f,", rec.hours);

	const char *buf = rec.vac_ban ? TRUE : FALSE;
	for (i = 0; buf[i] != 0; i++, (*index)++)
		(**index) = buf[i];
	(**index) = '\n';
	(*index)++;
}


Export void external_sort(const char *path, int keyIndex, bool ascending, void (*progressCallback)(float)) {
	ifstream input;
	ofstream output;
	Comparator cmp = comparators[ascending][keyIndex];
	string tempDir = "temp";

	fs::create_directories(tempDir);

	input.open(path, std::ios::binary);
	input.seekg(0, std::ios::end);
	size_t totalFileSize = input.tellg();
	double readIt = 0;
	input.seekg(0, std::ios::beg);

	size_t totalFiles = 0;
	size_t totalRecords = 0;
	char *buffer = new char[READER_SIZE+1];
	char *index;
	Record *records = new Record[MAX_RECORDS];
	
	progressCallback(0);
	while (1) {
		// чтение куска файла.
		input.read(buffer, READER_SIZE);
		std::streamsize bytesRead = input.gcount();
		if (bytesRead == 0) break;
		// востановление указателя
		size_t currentFilePos = input.tellg();
		index = buffer + (bytesRead-1);
		for (; *index != '\n'; index--) // не очень безопасно
			currentFilePos--;
		*(index+1) = 0;
		readIt += (index+1) - buffer;
		input.seekg(currentFilePos, std::ios::beg);
		// переход к чтению
		index = buffer;
		while (*index != 0) {
			parse(&index, records[totalRecords]);
			totalRecords++;
			if (totalRecords == MAX_RECORDS) {
				sort(records, records + totalRecords, cmp);
				output.open(tempDir + "/r" + to_string(totalFiles++) + ".tmp", ios::binary);
				output.write(reinterpret_cast<char*>(records), sizeof(Record) * totalRecords);
				output.close();
				progressCallback(readIt / totalFileSize);
				totalRecords = 0;
			}
		}
	}
	input.close();

	if (totalRecords > 0) {
		sort(records, records + totalRecords, cmp);
		output.open(tempDir + "/r" + to_string(totalFiles++) + ".tmp", ios::binary);
		output.write(reinterpret_cast<char*>(records), sizeof(Record) * totalRecords);
		output.close();
		progressCallback(readIt / totalFileSize);
	}

	delete[] buffer;
	delete[] records;

	progressCallback(0);
	auto inverted_cmp = [&](const MergeNode& a, const MergeNode& b) {
		return cmp(b.rec, a.rec);
	};

	priority_queue<MergeNode, vector<MergeNode>, decltype(inverted_cmp)> pq(inverted_cmp);
	vector<ifstream*> openFiles;
	output.open(string(path) + ".sorted", ios::binary);

	for (int i = 0; i < totalFiles; ++i) {
		auto* file = new ifstream(tempDir + "/r" + to_string(i) + ".tmp", ios::binary);
		Record rec;
		file->read((char*)&rec, sizeof(Record));
		if (file->gcount() == sizeof(Record)) {
			pq.push({rec, i});
		}
		openFiles.push_back(file);
	}

	readIt = 0;
	buffer = new char[WRITER_SIZE];
	index = buffer;
	size_t size;

	while (!pq.empty()) {
		MergeNode top = pq.top();
		pq.pop();
		serialize(&index, top.rec);
		size = index - buffer;
		if (size > WRITER_SIZE-1000) {
			output.write(buffer, size);
			readIt += size;
			progressCallback(readIt / totalFileSize);
			index = buffer;
		}

		Record rec;
		openFiles[top.fileIndex]->read((char*)&rec, sizeof(Record));
		if (openFiles[top.fileIndex]->gcount() == sizeof(Record)) {
			pq.push({rec, top.fileIndex});
		}
	}

	if (index > buffer) {
		output.write(buffer, size);
		readIt += size;
		progressCallback(readIt / totalFileSize);
	}

	delete[] buffer;
	for (auto file : openFiles) { file->close(); delete file; }
	fs::remove_all(tempDir);
	output.close();
}


int main() {
	auto progress = [](float p) {
		printf("Прогресс: %.2f%%\n", p * 100);
	};

	const int _unused_xxx = sizeof(Record);
	// ascending (по возрастанию = true)
	// 0 nickname
	// 1 uuid
	// 2 reg_date
	// 3 level
	// 4 hours
	// 5 vac_ban
	external_sort("data.csv", 2, false, progress);
	return 0;
}

// как приложение:
// g++ external_sort.cpp -o external_sort
// как библиотеку:
// g++ -shared -o external_sort.dll external_sort.cpp -static -Os -s