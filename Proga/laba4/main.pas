program ShowKeyCodes;
uses Keyboard, SysUtils;
const
	MAX_MSG = 3;
var
	Key: TKeyEvent;
	KeyCode: Word;
	messages: array[0..MAX_MSG] of string = (
		'Первый_пункт',
		'Второй_пункт',
		'Третий_пункт',
		'Четвёртый_пункт'
	);
	selected, i: integer;
begin
	InitKeyboard;
	selected := 0;
	repeat
		Write(#27'[2J');
		Write(#27'[1;1H');

		for i := 0 to MAX_MSG do begin
			if i = selected then write('[*] ')
			else write('[ ] ');
			writeln(messages[i]);
		end;

		Key := GetKeyEvent;
		Key := TranslateKeyEvent(Key);
		KeyCode := GetKeyEventCode(Key);

		// writeln('Код клавиши: ', KeyCode);
		if KeyCode = 283 then // ESC
		begin
			writeln('Выход...'); Break;
		end else if KeyCode = 65313 then begin
			// writeln('вверх');
			selected := selected - 1;
		end else if KeyCode = 65319 then begin
			// writeln('вниз')
			selected := selected + 1;
		end;
		if selected < 0 then selected := MAX_MSG;
		selected := selected mod (MAX_MSG + 1);

		// Код клавиши: 65313 ^
		// Код клавиши: 65319 v
		// Sleep(50);

	until false;
	DoneKeyboard;
end.