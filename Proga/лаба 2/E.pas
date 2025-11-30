
program Main;
var 
  A: array of LongInt;
  n, k, i, m, s, li, ri: LongInt;
begin
  readln(n, k);
  SetLength(A, n);
  m := n; s := 0;
  li := 0; ri := n-1;
  for i := 0 to n-1 do begin
    read(A[i]); s := s + A[i];
  end;
  while s > k do begin
    if A[li] > A[ri] then
      begin s := s - A[li]; li := li + 1; end
    else
      begin s := s - A[ri]; ri := ri - 1; end;
    m := m - 1;
  end;
  write(m);
end.