class PromptBuilder:
	def __init__(self):
		self._system_role = (
			"Ты --- опытный методист и преподаватель высшей категории. "
			"Твоя задача --- создавать качественные учебные программы, "
			"адаптированные под уровень подготовки учащихся."
		)
		self._discipline = None
		self._level = None
	
	def set_discipline(self, discipline: str):
		self._discipline = discipline
		return self
	
	def set_level(self, level: str):
		self._level = level
		return self
	
	def build_program_prompt(self) -> list:
		if not self._discipline:
			raise ValueError("Дисциплина не установлена!")
		if not self._level:
			raise ValueError("Уровень подготовки не установлен!")
		
		level_instructions = {
			"Школа": "Программа должна быть адаптирована для школьников. Общий объём: 34-68 часов.",
			"ВУЗ": "Программа должна соответствовать стандартам высшего образования. Объём: 72-108 часов.",
			"Курсы": "Программа должна быть практико-ориентированной. Объём: 20-40 часов."
		}
		
		level_text = level_instructions.get(self._level, level_instructions["ВУЗ"])
		
		user_prompt = (
			f"Создай подробную учебную программу по дисциплине: «{self._discipline}». "
			f"Уровень подготовки: {self._level}.\n\n{level_text}\n\n"
			f"Структура: 1. ПОЯСНИТЕЛЬНАЯ ЗАПИСКА, 2. ПОЧАСОВОЙ ПЛАН, "
			f"3. ЛИТЕРАТУРА, 4. ТЕМЫ ДЗ, 5. ФОРМЫ КОНТРОЛЯ.\n\n"
			f"Верни результат в формате JSON со следующими полями: "
			f"discipline, level, total_hours, goals, schedule, literature, homework, assessment.\n"
			f"Никаких пояснений, только JSON."
		)
		
		return [
			{"role": "system", "content": self._system_role},
			{"role": "user", "content": user_prompt}
		]
	
	def get_system_role(self) -> str:
		return self._system_role
	

if __name__ == '__main__':
	builder = PromptBuilder()
	print("=== Системная роль ===")
	print(builder.get_system_role())

	print("\n=== build_program_prompt без параметров ===")
	try:
		builder.build_program_prompt()
	except ValueError as e:
		print(f"Ошибка: {e}")

	builder.set_discipline("Программирование на Python").set_level("Курсы")
	print("\n=== build_program_prompt после установки параметров ===")
	messages = builder.build_program_prompt()
	for msg in messages:
		print(f"{msg['role']}: {msg['content'][:200]}...")