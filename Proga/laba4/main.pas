program Main;
uses Keyboard, SysUtils;

const
  MAX_MSG = 8;

type
	mainType = longint;
  Element = record
    data: mainType;
    prev: ^Element;
    next: ^Element;
  end;


// #####################################################
// ФУНКЦИИ И ПРОЦЕДУРЫ

function InputCount(): mainType;
var
  count: mainType;
begin
  repeat
    write('Введите количество элементов: ');
    readln(count);
    if count >= 0 then break;
    writeln('Количество элементов должно быть положительным!');
  until false;
  InputCount := count;
end;

function InputNumber(): mainType;
var
  number: mainType;
begin
  write('Введите число: ');
  readln(number);
  InputNumber := number;
end;

procedure Clear(var str: Element);
var
  ptr: ^Element;
begin
  while str.data > 0 do begin    // пока количество больше 0
    ptr := str.prev;             // ссылка на элемент
    str.prev := (ptr^).next;     // ссылка на следующий
    dispose(ptr);                // освобождаем память
    str.data := str.data - 1;
  end;
  str.next := nil;
end;

procedure Display(var str: Element);
var
  ptr: ^Element;
begin
  ptr := str.prev;               // указатель на текущий
  while ptr <> nil do begin      // пока указатель действительный
    write((ptr^).data, ' ');     // вывести значение элемента
    ptr := (ptr^).next;          // указатель на следующий
  end;
end;

procedure PushStart(var str: Element; value: mainType);
var
  ptr: ^Element;
begin
  new(ptr);                      // выделение памяти
  (ptr^).data := value;          // запись значения в A
  (ptr^).prev := nil;            // в A ссылка на следующий
  (ptr^).next := nil;            // в A ссылка на предыдущий
  if str.data = 0 then begin      // если дек пуст
    str.prev := ptr;               // в дек ссылку на начало
    str.next := ptr;               // в дек ссылку на конец
  end else begin                  // иначе
    (ptr^).next := str.prev;       // в A ссылка на следующий B
    (str.prev^).prev := ptr;       // в B ссылка на предыдущий A
    str.prev := ptr;               // в начало дек ссылку на А
  end;
  str.data := str.data + 1;       // счётчик +1
end;

procedure PushEnd(var str: Element; value: mainType);
var
  ptr: ^Element;
begin
  new(ptr);                      // выделение памяти
  (ptr^).data := value;         // запись значения в A
  (ptr^).prev := nil;            // в A ссылка на следующий
  (ptr^).next := nil;            // в A ссылка на предыдущий
  if str.data = 0 then begin     // если дек пуст
    str.prev := ptr;               // в дек ссылку на начало
    str.next := ptr;               // в дек ссылку на конец
  end else begin                 // иначе
    (ptr^).prev := str.next;       // в A ссылка на предыдущий Б
    (str.next^).next := ptr;       // в Б ссылка на следующий А
    str.next := ptr;               // в конец дек ссылку на А
  end;
  str.data := str.data + 1;      // счётчик +1
end;

function PopStart(var str: Element): mainType;
var
  value: mainType;
  ptr: ^Element;
begin
  ptr := str.prev;
  value := (ptr^).data;
  str.prev := (ptr^).next;
  str.data := str.data - 1;
  if str.data > 0 then
    (str.prev^).prev := nil
	else
		str.next := nil;
  dispose(ptr);
  PopStart := value;
end;

function PopEnd(var str: Element): mainType;
var
  value: mainType;
  ptr: ^Element;
begin
  ptr := str.next;
  value := (ptr^).data;
  str.next := (ptr^).prev;
  str.data := str.data - 1;
  if str.data > 0 then
    (str.next^).next := nil
	else
		str.prev := nil;
  dispose(ptr);
  PopEnd := value;
end;

procedure Fill(var str: Element);
var
  value, i: mainType;
begin
  for i := InputCount() downto 1 do begin
    read(value); PushEnd(str, value);
  end;
end;

procedure RandomFill(var str: Element);
var
  a, b, c, count, i, value: mainType;
begin
  writeln('Генерация N натуральных элементов');
  count := InputCount();

  while count <> 0 do begin
    write('Введите диапазон: ');
    readln(a, b);
    if a <> b then break;
    writeln('Диапазон не может быть равен 0!');
  end;

  if (a > b) and (count <> 0) then begin
    c := a; a := b; b := c;
  end;

  for i := 1 to count do begin
    // записать в value случайное число от a до b
    value := Random(b - a + 1) + a;
    PushEnd(str, value);
  end;
end;
// #####################################################

var
  _key_event: TKeyEvent;

  str: Element;
  key: Word;
  messages: array[0..MAX_MSG] of string = (
    'Очистить',
    'Заполнить',
    'Заполнить случайными элементами',
    'Узнать размер',
    'Отобразить',
    'Вставить в начало',
    'Вставить в конец',
    'Забрать из начала',
    'Забрать из конца'
  );
  selected, number, i: mainType;
begin
  // ##############
  Randomize;
  InitKeyboard;
  // ##############

  str.data := 0;
  str.prev := nil;
  str.next := nil;

  selected := 0;
  repeat
    // ##################
    // очистить экран
    Write(#27'[2J');
    Write(#27'[1;1H');
    // ##################

    writeln('Управление Дек''ом');
    for i := 0 to MAX_MSG do begin
      if i = selected then
        write('[*] ')
      else
        write('[ ] ');
      writeln(messages[i]);
    end;

    // ###############################
    // прочесть клавишу в key
    _key_event := GetKeyEvent;
    _key_event := TranslateKeyEvent(_key_event);
    key := GetKeyEventCode(_key_event);
    // ###############################

    // в key клавиша ...?
    case key of
      // ESC?
      283: begin writeln('Выход...'); break; end;
      // UP?
      65313: selected := selected - 1;
      // DOWN?
      65319: selected := selected + 1;
      // ENTER?
      7181: begin
        writeln;
        // selected?
        case selected of

          0: begin
            Clear(str);
            writeln('Дек очищен.');
          end;

          1: begin
            Fill(str);
          end;

          2: begin
            RandomFill(str);
          end;

          3: begin
            writeln('Размер: ', str.data, ' эл.');
          end;

          4: begin
            write('Массив: '); Display(str);
          end;

          5: begin
            number := InputNumber();
            PushStart(str, number);
          end;

          6: begin
            number := InputNumber();
            PushEnd(str, number);
          end;

          7: begin
            if str.data > 0 then begin
              number := PopStart(str);
              writeln('Число с начала: ', number);
            end else
              writeln('В массиве нет элементов');
          end;

          8: begin
            if str.data > 0 then begin
              number := PopEnd(str);
              writeln('Число с конца: ', number);
            end else
              writeln('В массиве нет элементов');
          end;
        end;
        readln;
      end;
    end;

    if selected < 0 then selected := MAX_MSG;
    selected := selected mod (MAX_MSG + 1);

  until false;
  DoneKeyboard;
end.