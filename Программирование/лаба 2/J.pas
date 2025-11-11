program Main;
var
  n, i: Word;
  a: array of Single;
begin
  readln(n);
  SetLength(a, n+2);
  for i := 1 to n do read(a[i]);
  a[0] := a[2];
  a[n+1] := a[n-1];
  for i := 1 to n do begin
    if not (((a[i] > a[i-1]) and (a[i] > a[i-1])) or
      ((a[i] < a[i-1]) and (a[i] < a[i-1]))) then
    begin
      write('No');
      exit();
    end;
  end;
  write('Yes');
end.