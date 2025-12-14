program Main;
var
  n, i: Word;
  a: array of Single;
begin
  readln(n);
  SetLength(a, n);
  for i := 0 to n-1 do begin
    read(a[i]);
    if (i > 0) and (a[i] < a[i-1]) then begin
      write(i); exit()
    end;
  end;
  write('0');
end.