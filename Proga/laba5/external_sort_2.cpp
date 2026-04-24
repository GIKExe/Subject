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

// ------------------------------------------------------------
// Структура записи (упакована, без лишних выравниваний)
// ------------------------------------------------------------
struct Record {
	char nickname[24];
	char uuid[40];
	char reg_date[16];
	int level;
	float hours;
	bool vac_ban;
};

// ------------------------------------------------------------
// Двумерный массив компараторов: [направление][ключ]
// Направление: 0 = descending, 1 = ascending
// ------------------------------------------------------------
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

// ------------------------------------------------------------
// Парсинг одной CSV строки в структуру Record
// Формат: nickname,uuid,reg_date,level,hours,vac_ban
// ------------------------------------------------------------
bool parse(const char* line, Record& rec) {
	// std::memset(rec.nickname, 0, sizeof(rec.nickname));
	// std::memset(rec.uuid, 0, sizeof(rec.uuid));
	// std::memset(rec.reg_date, 0, sizeof(rec.reg_date));
	// rec.level = 0;
	// rec.hours = 0.0f;
	// rec.vac_ban = false;

	const char *ptr = line;
	char *fieldStart;

	// 1. nickname
	fieldStart = const_cast<char*>(ptr);
	while (*ptr != ',') ptr++;
	size_t len = ptr - fieldStart;
	// if (len >= sizeof(rec.nickname)) len = sizeof(rec.nickname) - 1;
	std::memcpy(rec.nickname, fieldStart, len);

	// 2. uuid
	fieldStart = const_cast<char*>(ptr);
	while (*ptr != ',') ptr++;
	len = ptr - fieldStart;
	// if (len >= sizeof(rec.uuid)) len = sizeof(rec.uuid) - 1;
	std::memcpy(rec.uuid, fieldStart, len);

	// 3. reg_date
	fieldStart = const_cast<char*>(ptr);
	while (*ptr != ',') ptr++;
	len = ptr - fieldStart;
	// if (len >= sizeof(rec.reg_date)) len = sizeof(rec.reg_date) - 1;
	std::memcpy(rec.reg_date, fieldStart, len);

	// 4. level (int)
	rec.level = std::atoi(ptr);
	while (*ptr != ',') ptr++;

	// 5. hours (float)
	rec.hours = std::strtof(ptr, nullptr);
	while (*ptr != ',') ptr++;

	// 6. vac_ban (true/false)
	if (std::strncmp(ptr, "true", 4) == 0) {
		rec.vac_ban = true;
	} else {
		rec.vac_ban = false;
	}
}

// ------------------------------------------------------------
// Сериализация структуры Record в CSV строку
// ------------------------------------------------------------
std::string serialize(const Record& rec) {
	std::string out;
	out.reserve(128);
	out.append(rec.nickname);
	out.push_back(',');
	out.append(rec.uuid);
	out.push_back(',');
	out.append(rec.reg_date);
	out.push_back(',');
	out.append(std::to_string(rec.level));
	out.push_back(',');
	char buf[32];
	std::snprintf(buf, sizeof(buf), "%.3f", rec.hours);
	out.append(buf);
	out.push_back(',');
	out.append(rec.vac_ban ? "true" : "false");
	out.push_back('\n');
	return out;
}

// ------------------------------------------------------------
// Основная функция внешней сортировки
// ------------------------------------------------------------
void external_sort(
	const std::string& inputFile,
	int keyIndex,
	bool ascending,
	std::function<void(float)> progressCallback
) {
	using namespace std::chrono;
	auto totalStart = high_resolution_clock::now();

	const size_t BUFFER_SIZE = 1024 * 1024;      // 1 МБ
	const size_t RECORDS_PER_TEMP = 1'000'000;
	fs::create_directories("temp");

	// Получаем нужный компаратор один раз
	Comparator cmp = comparators[ascending ? 1 : 0][keyIndex];

	// ---------- Этап 1: разделение и сортировка блоков ----------
	auto stage1Start = high_resolution_clock::now();

	std::ifstream inFile(inputFile, std::ios::binary);
	if (!inFile.is_open())
		throw std::runtime_error("Cannot open input file");

	inFile.seekg(0, std::ios::end);
	size_t totalFileSize = inFile.tellg();
	inFile.seekg(0, std::ios::beg);
	size_t bytesProcessed = 0;

	std::vector<Record> records;
	records.reserve(RECORDS_PER_TEMP);

	std::vector<std::string> tempFiles;
	std::string leftover;
	std::vector<char> rawBuf(BUFFER_SIZE);
	size_t totalRecords = 0;

	while (inFile) {
		inFile.read(rawBuf.data(), BUFFER_SIZE);
		std::streamsize bytesRead = inFile.gcount();
		if (bytesRead == 0 && leftover.empty()) break;

		std::string chunk = leftover + std::string(rawBuf.data(), bytesRead);
		bytesProcessed += bytesRead;

		size_t lastNewline = chunk.rfind('\n');
		if (lastNewline == std::string::npos) {
			leftover = chunk;
			continue;
		}

		leftover = chunk.substr(lastNewline + 1);
		std::string fullData = chunk.substr(0, lastNewline + 1);

		size_t pos = 0;
		while (pos < fullData.size()) {
			size_t eol = fullData.find('\n', pos);
			if (eol == std::string::npos) break;
			std::string line = fullData.substr(pos, eol - pos);
			pos = eol + 1;
			if (line.empty()) continue;

			Record rec;
			if (parse(line.c_str(), rec)) {
				records.push_back(rec);
				totalRecords++;

				if (records.size() >= RECORDS_PER_TEMP) {
					std::sort(records.begin(), records.end(), cmp);
					char tempName[64];
					std::snprintf(tempName, sizeof(tempName), "temp/part_%04zu.bin", tempFiles.size());
					std::ofstream outFile(tempName, std::ios::binary);
					outFile.write(reinterpret_cast<const char*>(records.data()),
								  records.size() * sizeof(Record));
					outFile.close();
					tempFiles.push_back(tempName);
					records.clear();
					records.reserve(RECORDS_PER_TEMP);
				}
			}
		}

		if (progressCallback && totalFileSize > 0) {
			float percent = 100.0f * bytesProcessed / totalFileSize;
			progressCallback(percent);
		}
	}

	if (!records.empty()) {
		std::sort(records.begin(), records.end(), cmp);
		char tempName[64];
		std::snprintf(tempName, sizeof(tempName), "temp/part_%04zu.bin", tempFiles.size());
		std::ofstream outFile(tempName, std::ios::binary);
		outFile.write(reinterpret_cast<const char*>(records.data()),
					  records.size() * sizeof(Record));
		outFile.close();
		tempFiles.push_back(tempName);
		records.clear();
	}

	inFile.close();
	if (progressCallback) progressCallback(100.0f);

	auto stage1End = high_resolution_clock::now();
	double stage1Sec = duration<double>(stage1End - stage1Start).count();
	std::printf("[Stage 1] Sorting & partitioning finished in %.3f s\n", stage1Sec);

	if (tempFiles.empty()) {
		std::printf("No data found.\n");
		return;
	}

	// ---------- Этап 2: многопутевое слияние ----------
	auto stage2Start = high_resolution_clock::now();

	struct Source {
		std::ifstream stream;
		Record current;
		bool valid;
	};
	std::vector<Source> sources;
	sources.reserve(tempFiles.size());

	for (const auto& fname : tempFiles) {
		Source src;
		src.stream.open(fname, std::ios::binary);
		if (!src.stream.is_open())
			throw std::runtime_error("Cannot open temp file: " + fname);
		src.stream.read(reinterpret_cast<char*>(&src.current), sizeof(Record));
		src.valid = (src.stream.gcount() == sizeof(Record));
		if (src.valid) sources.push_back(std::move(src));
	}

	if (sources.empty()) {
		std::printf("No valid data in temp files.\n");
		return;
	}

	// Компаратор для кучи: для ascending (min‑heap) a > b → ниже приоритет
	auto heapComp = [cmp, ascending](const std::pair<Record, int>& a,
									  const std::pair<Record, int>& b) -> bool {
		if (ascending)
			return cmp(b.first, a.first); // a > b  (приоритет ниже)
		else
			return cmp(a.first, b.first); // a < b  (приоритет ниже)
	};
	using QueueElement = std::pair<Record, int>;
	std::priority_queue<QueueElement, std::vector<QueueElement>, decltype(heapComp)> pq(heapComp);

	for (size_t i = 0; i < sources.size(); ++i) {
		if (sources[i].valid)
			pq.emplace(sources[i].current, i);
	}

	std::ofstream sortedFile("sorted.txt", std::ios::out | std::ios::trunc);
	if (!sortedFile.is_open())
		throw std::runtime_error("Cannot create sorted.txt");

	size_t recordsWritten = 0;
	const size_t totalRecordsCount = totalRecords;
	const size_t progressStep = std::max<size_t>(1, totalRecordsCount / 100);

	while (!pq.empty()) {
		auto [rec, idx] = pq.top();
		pq.pop();

		sortedFile << serialize(rec);
		++recordsWritten;

		Source& src = sources[idx];
		if (src.stream.read(reinterpret_cast<char*>(&src.current), sizeof(Record)))
			pq.emplace(src.current, idx);

		if (progressCallback && (recordsWritten % progressStep == 0 || recordsWritten == totalRecordsCount)) {
			float percent = 100.0f * recordsWritten / totalRecordsCount;
			progressCallback(percent);
		}
	}

	sortedFile.close();

	for (auto& src : sources) src.stream.close();
	for (const auto& fname : tempFiles) fs::remove(fname);
	fs::remove_all("temp");

	auto stage2End = high_resolution_clock::now();
	double stage2Sec = duration<double>(stage2End - stage2Start).count();
	std::printf("[Stage 2] Multiway merge finished in %.3f s\n", stage2Sec);

	auto totalEnd = high_resolution_clock::now();
	double totalSec = duration<double>(totalEnd - totalStart).count();
	std::printf("[Total] External sort completed in %.3f s\n", totalSec);
}

// ------------------------------------------------------------
// Пример использования
// ------------------------------------------------------------
/*
int main() {
	auto progress = [](float p) {
		std::printf("Progress: %.2f%%\r", p);
		std::fflush(stdout);
	};
	external_sort("data.csv", 0, true, progress);
	return 0;
}
*/