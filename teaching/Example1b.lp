\* Source Pyomo model name=Example1 *\

min 
OBJ:
+50 s(1_1)
+25 s(1_2)
+50 s(2_1)
+25 s(2_2)
+50 s(3_1)
+25 s(3_2)
+50 s(4_1)
+25 s(4_2)
+50 s(5_1)
+25 s(5_2)

s.t.

c_u_ConstraintGasCap1_:
+1 s(1_1)
<= 100

c_u_ConstraintGasCap2_:
+1 s(2_1)
<= 100

c_u_ConstraintGasCap3_:
+1 s(3_1)
<= 100

c_u_ConstraintGasCap4_:
+1 s(4_1)
<= 100

c_u_ConstraintGasCap5_:
+1 s(5_1)
<= 100

c_u_ConstraintBiomassCap1_:
+1 s(1_2)
<= 30

c_u_ConstraintBiomassCap2_:
+1 s(2_2)
<= 30

c_u_ConstraintBiomassCap3_:
+1 s(3_2)
<= 30

c_u_ConstraintBiomassCap4_:
+1 s(4_2)
<= 30

c_u_ConstraintBiomassCap5_:
+1 s(5_2)
<= 30

c_l_ConstraintDem1_:
+1 s(1_1)
+1 s(1_2)
>= 60

c_l_ConstraintDem2_:
+1 s(2_1)
+1 s(2_2)
>= 100

c_l_ConstraintDem3_:
+1 s(3_1)
+1 s(3_2)
>= 120

c_l_ConstraintDem4_:
+1 s(4_1)
+1 s(4_2)
>= 80

c_l_ConstraintDem5_:
+1 s(5_1)
+1 s(5_2)
>= 30

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= s(1_1) <= +inf
   0 <= s(1_2) <= +inf
   0 <= s(2_1) <= +inf
   0 <= s(2_2) <= +inf
   0 <= s(3_1) <= +inf
   0 <= s(3_2) <= +inf
   0 <= s(4_1) <= +inf
   0 <= s(4_2) <= +inf
   0 <= s(5_1) <= +inf
   0 <= s(5_2) <= +inf
end
