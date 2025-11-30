
program Main;
var 
  n, i, i2: Word;
  A: array of Integer;
  B: array of Integer;
begin
  readln(n);
  SetLength(A, n);
  SetLength(B, n);
  for i := 0 to n-1 do read(A[i]);
  i2 := 0;
  if n < 2 then begin
    write('NO');
  end else begin
    for i := 0 to n-2 do begin
      if A[i+1] > A[i] then begin
        B[i2] := A[i];
        i2 := i2 + 1;
      end;
    end;
    if i2 = 0 then begin
      write('NO');
    end else begin
      writeln(i2);
      for i := 0 to i2-1 do write(B[i], ' ');
    end;
  end;
end.