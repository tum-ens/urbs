\* Source Pyomo model name=Example1 *\

min 
OBJ:
+25 s(t1_Biomass)
+50 s(t1_Gas)
+25 s(t2_Biomass)
+50 s(t2_Gas)
+25 s(t3_Biomass)
+50 s(t3_Gas)
+25 s(t4_Biomass)
+50 s(t4_Gas)
+25 s(t5_Biomass)
+50 s(t5_Gas)

s.t.

c_u_ConstraintGasCap1_:
+1 s(t1_Gas)
<= 100

c_u_ConstraintGasCap2_:
+1 s(t2_Gas)
<= 100

c_u_ConstraintGasCap3_:
+1 s(t3_Gas)
<= 100

c_u_ConstraintGasCap4_:
+1 s(t4_Gas)
<= 100

c_u_ConstraintGasCap5_:
+1 s(t5_Gas)
<= 100

c_u_ConstraintBiomassCap1_:
+1 s(t1_Biomass)
<= 30

c_u_ConstraintBiomassCap2_:
+1 s(t2_Biomass)
<= 30

c_u_ConstraintBiomassCap3_:
+1 s(t3_Biomass)
<= 30

c_u_ConstraintBiomassCap4_:
+1 s(t4_Biomass)
<= 30

c_u_ConstraintBiomassCap5_:
+1 s(t5_Biomass)
<= 30

c_l_ConstraintDem1_:
+1 s(t1_Biomass)
+1 s(t1_Gas)
>= 60

c_l_ConstraintDem2_:
+1 s(t2_Biomass)
+1 s(t2_Gas)
>= 100

c_l_ConstraintDem3_:
+1 s(t3_Biomass)
+1 s(t3_Gas)
>= 120

c_l_ConstraintDem4_:
+1 s(t4_Biomass)
+1 s(t4_Gas)
>= 80

c_l_ConstraintDem5_:
+1 s(t5_Biomass)
+1 s(t5_Gas)
>= 30

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= s(t1_Biomass) <= +inf
   0 <= s(t1_Gas) <= +inf
   0 <= s(t2_Biomass) <= +inf
   0 <= s(t2_Gas) <= +inf
   0 <= s(t3_Biomass) <= +inf
   0 <= s(t3_Gas) <= +inf
   0 <= s(t4_Biomass) <= +inf
   0 <= s(t4_Gas) <= +inf
   0 <= s(t5_Biomass) <= +inf
   0 <= s(t5_Gas) <= +inf
end
