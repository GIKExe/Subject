
program Main;
  var n, i, li, mi, x, c, m: Word;
begin
  readln(n);
  li := 0;
  mi := 0;
  c := 0;
  m := 0;
  for i := 0 to n-1 do begin
    read(x);
    if x > 0 then begin
      if c = 0 then li := i;
      c := c + 1;
    end else begin
      if c >= m then begin
        mi := li;
        m := c;
      end;
      li := 0;
      c := 0;
    end;
  end;
  if c >= m then begin
    mi := li;
    m := c;
  end;
  write(mi); write(' '); write(m);
end.