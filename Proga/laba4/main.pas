program ShowKeyCodes;
uses Keyboard, SysUtils;

const
	MAX_MSG = 2;

procedure ShiftRight(var arr: array of integer; shiftCount, max_size: integer);
var
  i: integer;
begin
  for i := max_size - 1 downto shiftCount do begin
		arr[i] := arr[i - shiftCount];
		// writeln('запись в ', i, ' из ', i - shiftCount);
	end;
end;

var
	// ####################
	_key_event: TKeyEvent;
	// ####################

	arr: array of integer;
	key: Word;
	messages: array[0..MAX_MSG] of string = (
		'Узнать размер Дек''а',
		'Заполнить случайными элементами',
		'Отобразить массив'
	);
	i, j, k: integer;
	selected, number, size: integer;
	x0, x1, x2, x3: integer;
	y0, y1, y2: integer;
begin
	// ##############
	Randomize;
	InitKeyboard;
	// ##############

	selected := 0;
	size := 0;
	repeat
		// ##################
		// очистить экран
		Write(#27'[2J');
		Write(#27'[1;1H');
		// ##################

		for i := 0 to MAX_MSG do begin
			if i = selected then write('[*] ')
			else write('[ ] ');
			writeln(messages[i]);
		end;

		// ###############################
		// прочесть клавишу в KeyCode
		_key_event := GetKeyEvent;
		_key_event := TranslateKeyEvent(_key_event);
		key := GetKeyEventCode(_key_event);
		// ###############################

		case key of
			// в key клавиша ESC?
			283: begin writeln('Выход...'); break; end;
			// в key клавиша UP?
			65313: selected := selected - 1;
			// в key клавиша DOWN?
			65319: selected := selected + 1;
			// в key клавиша ENTER?
			7181: begin
				writeln;
				case selected of
					0: writeln('Размер Дек''а: ', size, ' эл.');

					1: begin
						write('Введите 0 для записи в конец, иначе в начало: ');
						readln(y0);
						repeat
							write('Введите кол-во элементов и диапазон: ');
							readln(x0, x1, x2);
							if x0 < 1 then writeln('Количество элементов должно быть больше 0!');
							if x1 = x2 then writeln('Диапазон не может быть равен 0!');
						until (x0 > 0) and (x1 <> x2);

						if x1 > x2 then begin
							x3 := x1;
							x1 := x2;
							x2 := x3;
						end;

						j := size;
						size := size + x0;
						// расширить массив на x0 элементов
						SetLength(arr, size);

						if y0 <> 0 then begin
							j := x0 - 1;
							// сдвинуть все элементы вправо на x0
							ShiftRight(arr, x0, size);
						end;

						for i := 1 to x0 do begin
							number := Random(x2 - x1 + 1) + x1;
							// writeln('index: ', j, ', new value: ', number);
							arr[j] := number;
							if y0 = 0 then j := j + 1 else j := j - 1;
						end;
					end;

					2: begin
						write('Массив: ');
						for i := 0 to Length(arr)-1 do write(arr[i], ' ');
					end;

				end;
				readln;
			end;
		// else
		// 	writeln('Другая клавиша: ', KeyCode);
		end;

		if selected < 0 then selected := MAX_MSG;
		selected := selected mod (MAX_MSG + 1);
		// Sleep(50);

	until false;
	DoneKeyboard;
end.