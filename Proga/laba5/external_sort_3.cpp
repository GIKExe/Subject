#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <filesystem>
#include <queue>
#include <functional>
#include <string>
#include <iomanip>
#include <iostream>
#include <cmath>

namespace fs = std::filesystem;
using namespace std;
using namespace std::chrono;


#define BUFFER_SIZE (1024*1024*10)   // 20 MiB
#define RECORDS_PER_TEMP (1'000'000) // 75 MiB 


struct __attribute__((packed)) Record {
	char nickname[24];
	char uuid[37];
	char reg_date[11];
	char level;
	float hours;
	char vac_ban;
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

	for (i = 0; (**index) != ','; i++, (*index)++)
		rec.uuid[i] = (**index);
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

	rec.vac_ban = 0;
	if (memcmp(*index, "true", 4) == 0)
		rec.vac_ban = 1;
	while ((**index) != '\n') (*index)++;
	(*index)++;
}


void serialize(char *buffer, Record &rec) {

}


void external_sort(const char *path, int keyIndex, bool ascending) {
	ifstream input;
	ofstream output;

	auto sortStart = high_resolution_clock::now();

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
	char *buffer = new char[BUFFER_SIZE+1]; // delete[] buffer
	Record *records = new Record[RECORDS_PER_TEMP]; // delete[] records
	
	while (1) {
		// чтение куска файла.
		input.read(buffer, BUFFER_SIZE);
		std::streamsize bytesRead = input.gcount();
		if (bytesRead == 0) break;
		// востановление указателя
		size_t currentFilePos = input.tellg();
		char* index = buffer + (bytesRead-1);
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
			if (totalRecords == RECORDS_PER_TEMP) {
				cout << "Прогресс: " << readIt / totalFileSize * 100 << '%' << endl;
				sort(records, records + totalRecords, cmp);
				output.open(tempDir + "/r" + to_string(totalFiles++) + ".tmp", ios::binary);
				output.write(reinterpret_cast<char*>(records), sizeof(Record) * totalRecords);
				output.close();
				totalRecords = 0;
			}
		}
	}
	input.close();

	if (totalRecords > 0) {
		cout << "Прогресс: " << readIt / totalFileSize * 100 << '%' << endl;
		sort(records, records + totalRecords, cmp);
		output.open(tempDir + "/r" + to_string(totalFiles++) + ".tmp", ios::binary);
		output.write(reinterpret_cast<char*>(records), sizeof(Record) * totalRecords);
		output.close();
	}

	delete[] buffer;
	delete[] records;
	auto splitEnd = chrono::high_resolution_clock::now();
	cout << "Разбиение завершено за: " << chrono::duration_cast<chrono::milliseconds>(splitEnd - sortStart).count() / 1000.0 << " сек." << endl;
}

int main() {
	const int _unused_xxx = sizeof(Record);
	external_sort("data.csv", 0, true);
	return 0;
}