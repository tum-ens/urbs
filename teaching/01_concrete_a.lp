\* Source Pyomo model name=Example1 *\

min 
x11:
+25 x1
+50 x10
+50 x2
+25 x3
+50 x4
+25 x5
+50 x6
+25 x7
+50 x8
+25 x9

s.t.

c_u_x12_:
+1 x2
<= 100

c_u_x13_:
+1 x4
<= 100

c_u_x14_:
+1 x6
<= 100

c_u_x15_:
+1 x8
<= 100

c_u_x16_:
+1 x10
<= 100

c_u_x17_:
+1 x1
<= 30

c_u_x18_:
+1 x3
<= 30

c_u_x19_:
+1 x5
<= 30

c_u_x20_:
+1 x7
<= 30

c_u_x21_:
+1 x9
<= 30

c_l_x22_:
+1 x1
+1 x2
>= 60

c_l_x23_:
+1 x3
+1 x4
>= 100

c_l_x24_:
+1 x5
+1 x6
>= 120

c_l_x25_:
+1 x7
+1 x8
>= 80

c_l_x26_:
+1 x10
+1 x9
>= 30

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= x1 <= +inf
   0 <= x2 <= +inf
   0 <= x3 <= +inf
   0 <= x4 <= +inf
   0 <= x5 <= +inf
   0 <= x6 <= +inf
   0 <= x7 <= +inf
   0 <= x8 <= +inf
   0 <= x9 <= +inf
   0 <= x10 <= +inf
end
