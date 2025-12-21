program ShowKeyCodes;

uses
  Keyboard;

var
  Key: TKeyEvent;
  KeyCode: Word;
begin
  InitKeyboard;
  repeat
    Key := GetKeyEvent;
    Key := TranslateKeyEvent(Key);
    KeyCode := GetKeyEventCode(Key);

    // writeln('Код клавиши: ', KeyCode);
    if KeyCode = 283 then // ESC
    begin
      writeln('Выход...'); Break;
    end else if KeyCode = 65313 then begin
			writeln('вверх');
		end else if KeyCode = 65319 then begin
			writeln('вниз')
		end;

		// Код клавиши: 65313 ^
		// Код клавиши: 65319 v

  until false;
  DoneKeyboard;
end.