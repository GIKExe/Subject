import json
import time
from openai import OpenAI
from google.colab import userdata

# ---------- Настройка клиента ----------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=userdata.get("OPENROUTER_API_KEY"),
)

MODEL = "google/gemma-4-31b-it:free"

# ---------- Функция повторных попыток ----------
def safe_api_call(messages, max_retries=3):
    """Отправка запроса с автоматическими повторами при ошибках"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3,
                # max_tokens=2048,
                top_p=0.95
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Попытка {attempt+1} не удалась: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise

# ---------- Генерация учебной программы ----------
def generate_curriculum(discipline: str, level: str, builder: PromptBuilder) -> dict:
    """Основная функция генерации учебной программы"""
    builder.set_discipline(discipline).set_level(level)
    messages = builder.build_program_prompt()
    
    print(f"Генерация программы по дисциплине: {discipline}")
    print(f"Уровень: {level}")
    
    raw = safe_api_call(messages)
    
    # Очистка от лишнего текста (поиск JSON)
    start = raw.find('{')
    end = raw.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("Не найден JSON-объект в ответе")
    
    try:
        curriculum = json.loads(raw[start:end])
        return curriculum
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        print(f"Сырой ответ: {raw[:500]}...")
        raise

# ---------- Сохранение в JSON ----------
def save_json( dict, filename: str):
    """Сохранение данных в JSON-файл"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Сохранено в {filename}")

# ---------- Генерация текстового документа ----------
def generate_text_file(curriculum: dict, filename: str):
    """Создание форматированного текстового файла с программой"""
    text = f"""
==============================================
                    УЧЕБНАЯ ПРОГРАММА
==============================================

ДИСЦИПЛИНА: {curriculum.get('discipline', 'Не указано')}
УРОВЕНЬ ПОДГОТОВКИ: {curriculum.get('level', 'Не указано')}
ОБЩЕЕ КОЛИЧЕСТВО ЧАСОВ: {curriculum.get('total_hours', 'Не указано')}

==============================================
1. ПОЯСНИТЕЛЬНАЯ ЗАПИСКА
==============================================

ЦЕЛИ И ЗАДАЧИ КУРСА:
{curriculum.get('goals', 'Не указано')}

==============================================
2. ПОЧАСОВОЙ ПЛАН ЗАНЯТИЙ
==============================================

"""
    # Добавление расписания
    schedule = curriculum.get('schedule', [])
    if schedule:
        text += f"{'№':<4} {'ТЕМА':<50} {'ЧАСЫ':<8} {'КОНТРОЛЬ':<20}\n"
        text += "-" * 82 + "\n"
        for lesson in schedule:
            topic = lesson.get('topic', '')[:48]
            text += f"{lesson.get('lesson', ''):<4} {topic:<50} {lesson.get('hours', ''):<8} {lesson.get('control', ''):<20}\n"
    
    text += f"""
==============================================
3. СПИСОК НЕОБХОДИМОЙ ЛИТЕРАТУРЫ
==============================================

ОСНОВНАЯ ЛИТЕРАТУРА:
"""
    literature = curriculum.get('literature', {})
    for i, book in enumerate(literature.get('main', []), 1):
        text += f"  {i}. {book}\n"
    
    text += "\nДОПОЛНИТЕЛЬНАЯ ЛИТЕРАТУРА:\n"
    for i, book in enumerate(literature.get('additional', []), 1):
        text += f"  {i}. {book}\n"
    
    text += f"""
==============================================
4. ТЕМЫ ДЛЯ ДОМАШНИХ ЗАДАНИЙ
==============================================

"""
    homework = curriculum.get('homework', [])
    for i, hw in enumerate(homework, 1):
        text += f"{i}. {hw.get('topic', '')}\n"
        text += f"   {hw.get('description', '')}\n\n"
    
    text += f"""
==============================================
5. ФОРМЫ КОНТРОЛЯ
==============================================

{curriculum.get('assessment', 'Не указано')}

==============================================
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Сохранено в {filename}")

# ---------- Основной конвейер ----------
def create_educational_program(discipline: str, level: str):
    """Основная функция создания учебной программы"""
    builder = PromptBuilder()
    
    try:
        # Генерация программы
        curriculum = generate_curriculum(discipline, level, builder)
        
        # Сохранение результатов
        safe_discipline = discipline.replace(" ", "_").replace("/", "_")
        save_json(curriculum, f"curriculum_{safe_discipline}.json")
        generate_text_file(curriculum, f"curriculum_{safe_discipline}.txt")
        
        print("\n✓ Программа успешно создана!")
        return curriculum
        
    except Exception as e:
        print(f"\n✗ Ошибка при генерации: {e}")
        raise

# ---------- Пример вызова ----------
if __name__ == "__main__":
    # Тестовый запуск
    result = create_educational_program(
        discipline="Программирование на Python",
        level="Курсы"
    )
    print(f"\nВсего часов: {result.get('total_hours')}")
    print(f"Количество занятий: {len(result.get('schedule', []))}")