#include <iostream>
#include <iomanip>
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

struct Record {
    string nickname;
    string uuid;
    string reg_date;
    int level;
    float hours;
    bool vac_ban;

    // СТРОГОЕ СРАВНЕНИЕ: возвращает true, если 'a' должно идти ПЕРЕД 'b'
    static bool isOrdered(const Record& a, const Record& b, int keyIndex, bool ascending) {
        if (ascending) {
            switch (keyIndex) {
                case 0: return a.nickname < b.nickname;
                case 1: return a.uuid < b.uuid;
                case 2: return a.reg_date < b.reg_date;
                case 3: return a.level < b.level;
                case 4: return a.hours < b.hours;
                default: return a.vac_ban < b.vac_ban;
            }
        } else {
            switch (keyIndex) {
                case 0: return a.nickname > b.nickname;
                case 1: return a.uuid > b.uuid;
                case 2: return a.reg_date > b.reg_date;
                case 3: return a.level > b.level;
                case 4: return a.hours > b.hours;
                default: return a.vac_ban > b.vac_ban;
            }
        }
    }
};

Record parse(const string& line) {
    stringstream ss(line);
    string item;
    Record r;
    getline(ss, r.nickname, ',');
    getline(ss, r.uuid, ',');
    getline(ss, r.reg_date, ',');
    
    auto safe_stoi = [](string s) { try { return s.empty() ? 0 : stoi(s); } catch(...) { return 0; } };
    auto safe_stof = [](string s) { try { return s.empty() ? 0.0f : stof(s); } catch(...) { return 0.0f; } };

    if (getline(ss, item, ',')) r.level = safe_stoi(item);
    if (getline(ss, item, ',')) r.hours = safe_stof(item);
    if (getline(ss, item, ',')) r.vac_ban = (item == "1" || item == "true");
    
    return r;
}

string serialize(const Record& r) {
    stringstream ss;
    ss << fixed << setprecision(3) << r.hours;

    return r.nickname + "," + r.uuid + "," + r.reg_date + "," + 
           to_string(r.level) + "," + ss.str() + "," + (r.vac_ban ? "true" : "false");
}

struct MergeNode {
    Record rec;
    int fileIndex;
};

void external_sort(string inputPath, int keyIdx, bool asc) {
    const size_t ROWS_PER_RUN = 450000; // оценка памяти 
    string tempDir = "temp";
    
    if (fs::exists(tempDir)) fs::remove_all(tempDir);
    fs::create_directory(tempDir);

    ifstream dataFile(inputPath);
    if (!dataFile.is_open()) throw runtime_error("Файл " + inputPath + " не найден!");

    string line;

    vector<Record> buffer;
    int runCount = 0;
    auto start = chrono::high_resolution_clock::now();

    cout << "[1/2] Этап разбиения: чтение и сортировка частей..." << endl;

    while (getline(dataFile, line)) {
        if (line.empty()) continue;
        buffer.push_back(parse(line));

        if (buffer.size() >= ROWS_PER_RUN) {
            sort(buffer.begin(), buffer.end(), [&](const Record& a, const Record& b){ 
                return Record::isOrdered(a, b, keyIdx, asc); 
            });
            
            ofstream out(tempDir + "/r" + to_string(runCount++) + ".tmp", ios::binary);
            for (const auto& r : buffer) out << serialize(r) << "\n";
            buffer.clear();
            cout << "  Сформирована часть " << runCount << endl;
        }
    }

    if (!buffer.empty()) {
        sort(buffer.begin(), buffer.end(), [&](const Record& a, const Record& b){ 
            return Record::isOrdered(a, b, keyIdx, asc); 
        });
        ofstream out(tempDir + "/r" + to_string(runCount++) + ".tmp", ios::binary);
        for (const auto& r : buffer) out << serialize(r) << "\n";
    }
    dataFile.close();

    auto splitEnd = chrono::high_resolution_clock::now();
    cout << "Этап разбиения завершен за " << chrono::duration_cast<chrono::seconds>(splitEnd - start).count() << " сек." << endl;

    // --- ЭТАП СЛИЯНИЯ ---
    cout << "[2/2] Этап слияния: объединение " << runCount << " файлов..." << endl;

    // Компаратор для priority_queue (делаем min-heap на основе нашего порядка)
    auto cmp = [keyIdx, asc](const MergeNode& a, const MergeNode& b) {
        // priority_queue возвращает элемент, для которого компаратор дает false.
        // Чтобы первым выходил элемент, который должен стоять в начале (isOrdered == true),
        // нужно инвертировать логику для очереди:
        return Record::isOrdered(b.rec, a.rec, keyIdx, asc);
    };
    
    priority_queue<MergeNode, vector<MergeNode>, decltype(cmp)> pq(cmp);
    vector<ifstream*> openFiles;
    ofstream outFile("sorted.txt", ios::binary);

    for (int i = 0; i < runCount; ++i) {
        auto* f = new ifstream(tempDir + "/r" + to_string(i) + ".tmp", ios::binary);
        if (getline(*f, line)) {
            pq.push({parse(line), i});
        }
        openFiles.push_back(f);
    }

    while (!pq.empty()) {
        MergeNode top = pq.top();
        pq.pop();
        outFile << serialize(top.rec) << "\n";

        if (getline(*openFiles[top.fileIndex], line)) {
            pq.push({parse(line), top.fileIndex});
        }
    }

    outFile.close();
    for (auto f : openFiles) { f->close(); delete f; }
    fs::remove_all(tempDir);

    auto end = chrono::high_resolution_clock::now();
    cout << "Слияние завершено за " << chrono::duration_cast<chrono::seconds>(end - splitEnd).count() << " сек." << endl;
    cout << "Итоговое время: " << chrono::duration_cast<chrono::seconds>(end - start).count() << " сек." << endl;
}

int main() {
    int k, o;
    cout << "--- Внешняя сортировка CSV ---\n";
    cout << "Ключ (0:Ник, 1:UUID, 2:Дата, 3:Lvl, 4:Часы, 5:VAC): "; 
    if(!(cin >> k)) return 0;
    cout << "Порядок (0:Убывание, 1:Возрастание): "; 
    if(!(cin >> o)) return 0;

    try {
        external_sort("data.csv", k, (o == 1));
        cout << "\nРезультат в файле sorted.txt" << endl;
    } catch (const exception& e) {
        cerr << "\nОШИБКА: " << e.what() << endl;
    }
    return 0;
}

// g++ -std=c++17 external_sort.cpp -o external_sort