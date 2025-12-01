program Main;

uses
  Math, SysUtils;

procedure f1;
var
  a, b: LongInt;
  c: Single;
begin
  a := 77617;
  b := 33096;
  c := 333.75 * Power(b, 6)
    + Power(a, 2) * (11 * Power(a, 2) * Power(b, 2)
    - Power(b, 6) - 121 * Power(b, 4) - 2)
    + 5.5 * Power(b, 8) + (a / (2 * b));
  WriteLn(c:0:6);
  WriteLn;
end;

procedure f2;
var
  a, b: LongInt;
  c: Single;
begin
  a := 77617;
  b := 33096;
  c := 21 * Power(b, 2) - 2 * Power(a, 2)
    + 55 * Power(b, 4)
		- 10 * Power(a, 2) * Power(b, 2)
    + (a / (2 * b));
  WriteLn(c:0:6);
  WriteLn;
end;

function Q(x: Single): Single;
var
  y: Single;
begin
  y := Abs(x - Sqrt(Power(x, 2) + 1))
        - 1 / (x + Sqrt(Power(x, 2) + 1));
  Q := y;
end;

function E(z: Single): Single;
var
  r: Single;
begin
  if z = 0 then
    E := 1
  else
  begin
    r := (Exp(z) - 1) / z;
    E := r;
  end;
end;

procedure f3(x: Single);
var
  y: Single;
begin
  y := E(Power(Q(x), 2));
  WriteLn(y:0:6);
end;

begin
  f1;
  f2;
  f3(15.0);
  f3(16.0);
  f3(17.0);
  f3(9999.0);
end.