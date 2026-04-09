#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <sstream>
#include <queue>
#include <filesystem>
#include <chrono>

namespace fs = std::filesystem;
using namespace std;

// Структура данных CSV
struct Record {
    string nickname;
    string uuid;
    string reg_date;
    int level;
    float hours;
    bool vac_ban;

    // Метод для сравнения по индексу колонки
    static bool compare(const Record& a, const Record& b, int keyIndex) {
        switch (keyIndex) {
            case 0: return a.nickname < b.nickname;
            case 1: return a.uuid < b.uuid;
            case 2: return a.reg_date < b.reg_date;
            case 3: return a.level < b.level;
            case 4: return a.hours < b.hours;
            case 5: return a.vac_ban < b.vac_ban;
            default: return a.uuid < b.uuid;
        }
    }
};

// Вспомогательные функции
Record parseCSV(const string& line) {
    stringstream ss(line);
    string item;
    Record r;
    getline(ss, r.nickname, ',');
    getline(ss, r.uuid, ',');
    getline(ss, r.reg_date, ',');
    getline(ss, item, ','); r.level = stoi(item);
    getline(ss, item, ','); r.hours = stof(item);
    getline(ss, item, ','); r.vac_ban = (item == "1" || item == "true");
    return r;
}

string serialize(const Record& r) {
    return r.nickname + "," + r.uuid + "," + r.reg_date + "," + 
           to_string(r.level) + "," + to_string(r.hours) + "," + (r.vac_ban ? "1" : "0");
}

// Структура для итератора слияния
struct MergeNode {
    Record rec;
    int fileIndex;
    bool operator>(const MergeNode& other) const {
        return false; // Логика сравнения определяется динамически в priority_queue
    }
};

void external_sort(string inputPath, int keyIndex) {
    const size_t MEMORY_LIMIT = 100 * 1024 * 1024; // 100MB
    string tempDir = "temp";
    fs::create_directory(tempDir);

    auto start = chrono::high_resolution_clock::now();

    // --- ЭТАП 1: РАЗБИЕНИЕ (RUN GENERATION) ---
    ifstream dataFile(inputPath);
    string line;
    vector<Record> buffer;
    size_t currentMem = 0;
    int runCount = 0;

    while (getline(dataFile, line)) {
        buffer.push_back(parseCSV(line));
        currentMem += line.size() + sizeof(Record); // Грубая оценка памяти

        if (currentMem >= MEMORY_LIMIT) {
            sort(buffer.begin(), buffer.end(), [keyIndex](const Record& a, const Record& b) {
                return Record::compare(a, b, keyIndex);
            });
            ofstream out(tempDir + "/run_" + to_string(runCount++) + ".txt");
            for (const auto& r : buffer) out << serialize(r) << "\n";
            buffer.clear();
            currentMem = 0;
        }
    }
    // Сброс остатка
    if (!buffer.empty()) {
        sort(buffer.begin(), buffer.end(), [keyIndex](const Record& a, const Record& b) {
            return Record::compare(a, b, keyIndex);
        });
        ofstream out(tempDir + "/run_" + to_string(runCount++) + ".txt");
        for (const auto& r : buffer) out << serialize(r) << "\n";
    }
    dataFile.close();

    auto splitEnd = chrono::high_resolution_clock::now();
    cout << "Phase 1 (Split) finished in: " 
         << chrono::duration_cast<chrono::seconds>(splitEnd - start).count() << "s\n";

    // --- ЭТАП 2: СЛИЯНИЕ (MERGE) ---
    auto compareNodes = [keyIndex](const MergeNode& a, const MergeNode& b) {
        return !Record::compare(a.rec, b.rec, keyIndex); // invert for min-heap
    };
    priority_queue<MergeNode, vector<MergeNode>, decltype(compareNodes)> pq(compareNodes);
    
    vector<ifstream*> runs(runCount);
    ofstream outFile("sorted.txt");

    for (int i = 0; i < runCount; ++i) {
        runs[i] = new ifstream(tempDir + "/run_" + to_string(i) + ".txt");
        if (getline(*runs[i], line)) {
            pq.push({parseCSV(line), i});
        }
    }

    while (!pq.empty()) {
        MergeNode top = pq.top();
        pq.pop();
        outFile << serialize(top.rec) << "\n";

        if (getline(*runs[top.fileIndex], line)) {
            pq.push({parseCSV(line), top.fileIndex});
        }
    }

    // Очистка
    outFile.close();
    for (int i = 0; i < runCount; ++i) {
        runs[i]->close();
        delete runs[i];
    }
    fs::remove_all(tempDir);

    auto mergeEnd = chrono::high_resolution_clock::now();
    cout << "Phase 2 (Merge) finished in: " 
         << chrono::duration_cast<chrono::seconds>(mergeEnd - splitEnd).count() << "s\n";
}

int main() {
    int key;
    cout << "Choose key (0: Nick, 1: UUID, 2: Date, 3: Lvl, 4: Hours, 5: VAC): ";
    cin >> key;
    
    try {
        external_sort("data.csv", key);
        cout << "Sorting complete. Result in sorted.txt" << endl;
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
    }
    return 0;
}

// g++ -std=c++17 external_sort.cpp -o external_sort