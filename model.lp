\* Source Pyomo model name=urbs *\

min 
objective_function:
+1 costs(Environmental)
+1 costs(Fixed)
+1 costs(Fuel)
+1 costs(Invest)
+1 costs(Purchase)
+1 costs(Revenue)
+1 costs(Variable)

s.t.

c_e_def_transmission_output(3501_2019_Mid_South_hvac_Elec)_:
-0.90000000000000002 e_tra_in(3501_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3501_2019_Mid_South_hvac_Elec)
= 0

c_e_def_transmission_output(3501_2019_North_Mid_hvac_Elec)_:
-1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
+1 e_tra_out(3501_2019_North_Mid_hvac_Elec)
= 0

c_e_def_transmission_output(3501_2019_North_South_hvac_Elec)_:
-0.84999999999999998 e_tra_in(3501_2019_North_South_hvac_Elec)
+1 e_tra_out(3501_2019_North_South_hvac_Elec)
= 0

c_e_def_transmission_output(3501_2019_South_Mid_hvac_Elec)_:
-0.90000000000000002 e_tra_in(3501_2019_South_Mid_hvac_Elec)
+1 e_tra_out(3501_2019_South_Mid_hvac_Elec)
= 0

c_e_def_transmission_output(3501_2019_South_North_hvac_Elec)_:
-0.84999999999999998 e_tra_in(3501_2019_South_North_hvac_Elec)
+1 e_tra_out(3501_2019_South_North_hvac_Elec)
= 0

c_e_def_transmission_output(3502_2019_Mid_South_hvac_Elec)_:
-0.90000000000000002 e_tra_in(3502_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3502_2019_Mid_South_hvac_Elec)
= 0

c_e_def_transmission_output(3502_2019_North_Mid_hvac_Elec)_:
-1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
+1 e_tra_out(3502_2019_North_Mid_hvac_Elec)
= 0

c_e_def_transmission_output(3502_2019_North_South_hvac_Elec)_:
-0.84999999999999998 e_tra_in(3502_2019_North_South_hvac_Elec)
+1 e_tra_out(3502_2019_North_South_hvac_Elec)
= 0

c_e_def_transmission_output(3502_2019_South_Mid_hvac_Elec)_:
-0.90000000000000002 e_tra_in(3502_2019_South_Mid_hvac_Elec)
+1 e_tra_out(3502_2019_South_Mid_hvac_Elec)
= 0

c_e_def_transmission_output(3502_2019_South_North_hvac_Elec)_:
-0.84999999999999998 e_tra_in(3502_2019_South_North_hvac_Elec)
+1 e_tra_out(3502_2019_South_North_hvac_Elec)
= 0

c_e_def_dc_power_flow(3501_2019_North_Mid_hvac_Elec)_:
+1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
+0.10000000000000001 phase_angle(3501_2019_Mid)
-0.10000000000000001 phase_angle(3501_2019_North)
= 0

c_e_def_dc_power_flow(3502_2019_North_Mid_hvac_Elec)_:
+1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
+0.10000000000000001 phase_angle(3502_2019_Mid)
-0.10000000000000001 phase_angle(3502_2019_North)
= 0

c_u_abs1_e_tra_dc_in(3501_2019_North_Mid_hvac_Elec)_:
-1 abs_e_tra_dc(3501_2019_North_Mid_hvac_Elec)
+1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
<= 0

c_u_abs1_e_tra_dc_in(3502_2019_North_Mid_hvac_Elec)_:
-1 abs_e_tra_dc(3502_2019_North_Mid_hvac_Elec)
+1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
<= 0

c_u_abs2_e_tra_dc_in(3501_2019_North_Mid_hvac_Elec)_:
-1 abs_e_tra_dc(3501_2019_North_Mid_hvac_Elec)
-1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
<= 0

c_u_abs2_e_tra_dc_in(3502_2019_North_Mid_hvac_Elec)_:
-1 abs_e_tra_dc(3502_2019_North_Mid_hvac_Elec)
-1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
<= 0

c_u_res_transmission_input_by_capacity(3501_2019_Mid_South_hvac_Elec)_:
-1 cap_tra_new(2019_Mid_South_hvac_Elec)
+1 e_tra_in(3501_2019_Mid_South_hvac_Elec)
<= 80

c_u_res_transmission_input_by_capacity(3501_2019_North_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_North_Mid_hvac_Elec)
+1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
<= 70

c_u_res_transmission_input_by_capacity(3501_2019_North_South_hvac_Elec)_:
-1 cap_tra_new(2019_North_South_hvac_Elec)
+1 e_tra_in(3501_2019_North_South_hvac_Elec)
<= 100

c_u_res_transmission_input_by_capacity(3501_2019_South_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_South_Mid_hvac_Elec)
+1 e_tra_in(3501_2019_South_Mid_hvac_Elec)
<= 80

c_u_res_transmission_input_by_capacity(3501_2019_South_North_hvac_Elec)_:
-1 cap_tra_new(2019_South_North_hvac_Elec)
+1 e_tra_in(3501_2019_South_North_hvac_Elec)
<= 100

c_u_res_transmission_input_by_capacity(3502_2019_Mid_South_hvac_Elec)_:
-1 cap_tra_new(2019_Mid_South_hvac_Elec)
+1 e_tra_in(3502_2019_Mid_South_hvac_Elec)
<= 80

c_u_res_transmission_input_by_capacity(3502_2019_North_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_North_Mid_hvac_Elec)
+1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
<= 70

c_u_res_transmission_input_by_capacity(3502_2019_North_South_hvac_Elec)_:
-1 cap_tra_new(2019_North_South_hvac_Elec)
+1 e_tra_in(3502_2019_North_South_hvac_Elec)
<= 100

c_u_res_transmission_input_by_capacity(3502_2019_South_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_South_Mid_hvac_Elec)
+1 e_tra_in(3502_2019_South_Mid_hvac_Elec)
<= 80

c_u_res_transmission_input_by_capacity(3502_2019_South_North_hvac_Elec)_:
-1 cap_tra_new(2019_South_North_hvac_Elec)
+1 e_tra_in(3502_2019_South_North_hvac_Elec)
<= 100

c_u_res_transmission_dc_input_by_capacity(3501_2019_North_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_North_Mid_hvac_Elec)
-1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
<= 70

c_u_res_transmission_dc_input_by_capacity(3502_2019_North_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_North_Mid_hvac_Elec)
-1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
<= 70

c_l_res_transmission_capacity(2019_Mid_South_hvac_Elec)_:
+1 cap_tra_new(2019_Mid_South_hvac_Elec)
>= -80

c_l_res_transmission_capacity(2019_North_Mid_hvac_Elec)_:
+1 cap_tra_new(2019_North_Mid_hvac_Elec)
>= -70

c_l_res_transmission_capacity(2019_North_South_hvac_Elec)_:
+1 cap_tra_new(2019_North_South_hvac_Elec)
>= -100

c_l_res_transmission_capacity(2019_South_Mid_hvac_Elec)_:
+1 cap_tra_new(2019_South_Mid_hvac_Elec)
>= -80

c_l_res_transmission_capacity(2019_South_North_hvac_Elec)_:
+1 cap_tra_new(2019_South_North_hvac_Elec)
>= -100

c_e_res_transmission_symmetry(2019_Mid_South_hvac_Elec)_:
+1 cap_tra_new(2019_Mid_South_hvac_Elec)
-1 cap_tra_new(2019_South_Mid_hvac_Elec)
= 0

c_e_res_transmission_symmetry(2019_North_South_hvac_Elec)_:
+1 cap_tra_new(2019_North_South_hvac_Elec)
-1 cap_tra_new(2019_South_North_hvac_Elec)
= 0

c_e_res_transmission_symmetry(2019_South_Mid_hvac_Elec)_:
-1 cap_tra_new(2019_Mid_South_hvac_Elec)
+1 cap_tra_new(2019_South_Mid_hvac_Elec)
= 0

c_e_res_transmission_symmetry(2019_South_North_hvac_Elec)_:
-1 cap_tra_new(2019_North_South_hvac_Elec)
+1 cap_tra_new(2019_South_North_hvac_Elec)
= 0

c_e_def_storage_state(3501_2019_Mid_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3500_2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3501_2019_Mid_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3501_2019_Mid_Hydrogen_Elec)
+1.5625 e_sto_out(3501_2019_Mid_Hydrogen_Elec)
= 0

c_e_def_storage_state(3501_2019_Mid_Pump_storage_Elec)_:
-1 e_sto_con(3500_2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3501_2019_Mid_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3501_2019_Mid_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3501_2019_Mid_Pump_storage_Elec)
= 0

c_e_def_storage_state(3501_2019_North_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3500_2019_North_Hydrogen_Elec)
+1 e_sto_con(3501_2019_North_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3501_2019_North_Hydrogen_Elec)
+1.5625 e_sto_out(3501_2019_North_Hydrogen_Elec)
= 0

c_e_def_storage_state(3501_2019_North_Pump_storage_Elec)_:
-1 e_sto_con(3500_2019_North_Pump_storage_Elec)
+1 e_sto_con(3501_2019_North_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3501_2019_North_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3501_2019_North_Pump_storage_Elec)
= 0

c_e_def_storage_state(3501_2019_South_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3500_2019_South_Hydrogen_Elec)
+1 e_sto_con(3501_2019_South_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3501_2019_South_Hydrogen_Elec)
+1.5625 e_sto_out(3501_2019_South_Hydrogen_Elec)
= 0

c_e_def_storage_state(3501_2019_South_Pump_storage_Elec)_:
-1 e_sto_con(3500_2019_South_Pump_storage_Elec)
+1 e_sto_con(3501_2019_South_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3501_2019_South_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3501_2019_South_Pump_storage_Elec)
= 0

c_e_def_storage_state(3502_2019_Mid_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3501_2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3502_2019_Mid_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3502_2019_Mid_Hydrogen_Elec)
+1.5625 e_sto_out(3502_2019_Mid_Hydrogen_Elec)
= 0

c_e_def_storage_state(3502_2019_Mid_Pump_storage_Elec)_:
-1 e_sto_con(3501_2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3502_2019_Mid_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3502_2019_Mid_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3502_2019_Mid_Pump_storage_Elec)
= 0

c_e_def_storage_state(3502_2019_North_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3501_2019_North_Hydrogen_Elec)
+1 e_sto_con(3502_2019_North_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3502_2019_North_Hydrogen_Elec)
+1.5625 e_sto_out(3502_2019_North_Hydrogen_Elec)
= 0

c_e_def_storage_state(3502_2019_North_Pump_storage_Elec)_:
-1 e_sto_con(3501_2019_North_Pump_storage_Elec)
+1 e_sto_con(3502_2019_North_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3502_2019_North_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3502_2019_North_Pump_storage_Elec)
= 0

c_e_def_storage_state(3502_2019_South_Hydrogen_Elec)_:
-0.99999649999999995 e_sto_con(3501_2019_South_Hydrogen_Elec)
+1 e_sto_con(3502_2019_South_Hydrogen_Elec)
-0.64000000000000001 e_sto_in(3502_2019_South_Hydrogen_Elec)
+1.5625 e_sto_out(3502_2019_South_Hydrogen_Elec)
= 0

c_e_def_storage_state(3502_2019_South_Pump_storage_Elec)_:
-1 e_sto_con(3501_2019_South_Pump_storage_Elec)
+1 e_sto_con(3502_2019_South_Pump_storage_Elec)
-0.93999999999999995 e_sto_in(3502_2019_South_Pump_storage_Elec)
+1.0638297872340425 e_sto_out(3502_2019_South_Pump_storage_Elec)
= 0

c_u_res_storage_input_by_power(3501_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_in(3501_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3501_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_in(3501_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_input_by_power(3501_2019_North_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_North_Hydrogen_Elec)
+1 e_sto_in(3501_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3501_2019_North_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_North_Pump_storage_Elec)
+1 e_sto_in(3501_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_input_by_power(3501_2019_South_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_South_Hydrogen_Elec)
+1 e_sto_in(3501_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3501_2019_South_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_South_Pump_storage_Elec)
+1 e_sto_in(3501_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_in(3502_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_in(3502_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_North_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_North_Hydrogen_Elec)
+1 e_sto_in(3502_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_North_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_North_Pump_storage_Elec)
+1 e_sto_in(3502_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_South_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_South_Hydrogen_Elec)
+1 e_sto_in(3502_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_input_by_power(3502_2019_South_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_South_Pump_storage_Elec)
+1 e_sto_in(3502_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_out(3501_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_out(3501_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_North_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_North_Hydrogen_Elec)
+1 e_sto_out(3501_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_North_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_North_Pump_storage_Elec)
+1 e_sto_out(3501_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_South_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_South_Hydrogen_Elec)
+1 e_sto_out(3501_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3501_2019_South_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_South_Pump_storage_Elec)
+1 e_sto_out(3501_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_out(3502_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_out(3502_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_North_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_North_Hydrogen_Elec)
+1 e_sto_out(3502_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_North_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_North_Pump_storage_Elec)
+1 e_sto_out(3502_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_South_Hydrogen_Elec)_:
-1 cap_sto_p_new(2019_South_Hydrogen_Elec)
+1 e_sto_out(3502_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_output_by_power(3502_2019_South_Pump_storage_Elec)_:
-1 cap_sto_p_new(2019_South_Pump_storage_Elec)
+1 e_sto_out(3502_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3500_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3500_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_North_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_North_Hydrogen_Elec)
+1 e_sto_con(3500_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_North_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_North_Pump_storage_Elec)
+1 e_sto_con(3500_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_South_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_South_Hydrogen_Elec)
+1 e_sto_con(3500_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3500_2019_South_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_South_Pump_storage_Elec)
+1 e_sto_con(3500_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3501_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3501_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_North_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_North_Hydrogen_Elec)
+1 e_sto_con(3501_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_North_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_North_Pump_storage_Elec)
+1 e_sto_con(3501_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_South_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_South_Hydrogen_Elec)
+1 e_sto_con(3501_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3501_2019_South_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_South_Pump_storage_Elec)
+1 e_sto_con(3501_2019_South_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_Mid_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3502_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_Mid_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3502_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_North_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_North_Hydrogen_Elec)
+1 e_sto_con(3502_2019_North_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_North_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_North_Pump_storage_Elec)
+1 e_sto_con(3502_2019_North_Pump_storage_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_South_Hydrogen_Elec)_:
-1 cap_sto_c_new(2019_South_Hydrogen_Elec)
+1 e_sto_con(3502_2019_South_Hydrogen_Elec)
<= 0

c_u_res_storage_state_by_capacity(3502_2019_South_Pump_storage_Elec)_:
-1 cap_sto_c_new(2019_South_Pump_storage_Elec)
+1 e_sto_con(3502_2019_South_Pump_storage_Elec)
<= 0

c_l_res_storage_power(2019_Mid_Hydrogen_Elec)_:
+1 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
>= 0

c_l_res_storage_power(2019_Mid_Pump_storage_Elec)_:
+1 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
>= 8000

c_l_res_storage_power(2019_North_Hydrogen_Elec)_:
+1 cap_sto_p_new(2019_North_Hydrogen_Elec)
>= 0

c_l_res_storage_power(2019_North_Pump_storage_Elec)_:
+1 cap_sto_p_new(2019_North_Pump_storage_Elec)
>= 1500

c_l_res_storage_power(2019_South_Hydrogen_Elec)_:
+1 cap_sto_p_new(2019_South_Hydrogen_Elec)
>= 0

c_l_res_storage_power(2019_South_Pump_storage_Elec)_:
+1 cap_sto_p_new(2019_South_Pump_storage_Elec)
>= 500

c_l_res_storage_capacity(2019_Mid_Hydrogen_Elec)_:
+1 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
>= 0

c_l_res_storage_capacity(2019_Mid_Pump_storage_Elec)_:
+1 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
>= 60000

c_l_res_storage_capacity(2019_North_Hydrogen_Elec)_:
+1 cap_sto_c_new(2019_North_Hydrogen_Elec)
>= 0

c_l_res_storage_capacity(2019_North_Pump_storage_Elec)_:
+1 cap_sto_c_new(2019_North_Pump_storage_Elec)
>= 700000

c_l_res_storage_capacity(2019_South_Hydrogen_Elec)_:
+1 cap_sto_c_new(2019_South_Hydrogen_Elec)
>= 0

c_l_res_storage_capacity(2019_South_Pump_storage_Elec)_:
+1 cap_sto_c_new(2019_South_Pump_storage_Elec)
>= 163000

c_e_res_initial_and_final_storage_state(3500_2019_Mid_Hydrogen_Elec)_:
-0.5 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
+1 e_sto_con(3500_2019_Mid_Hydrogen_Elec)
= 0

c_e_res_initial_and_final_storage_state(3500_2019_Mid_Pump_storage_Elec)_:
-0.5 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
+1 e_sto_con(3500_2019_Mid_Pump_storage_Elec)
= 0

c_e_res_initial_and_final_storage_state(3500_2019_North_Hydrogen_Elec)_:
-0.5 cap_sto_c_new(2019_North_Hydrogen_Elec)
+1 e_sto_con(3500_2019_North_Hydrogen_Elec)
= 0

c_e_res_initial_and_final_storage_state(3500_2019_North_Pump_storage_Elec)_:
-0.5 cap_sto_c_new(2019_North_Pump_storage_Elec)
+1 e_sto_con(3500_2019_North_Pump_storage_Elec)
= 0

c_e_res_initial_and_final_storage_state(3500_2019_South_Hydrogen_Elec)_:
-0.5 cap_sto_c_new(2019_South_Hydrogen_Elec)
+1 e_sto_con(3500_2019_South_Hydrogen_Elec)
= 0

c_e_res_initial_and_final_storage_state(3500_2019_South_Pump_storage_Elec)_:
-0.5 cap_sto_c_new(2019_South_Pump_storage_Elec)
+1 e_sto_con(3500_2019_South_Pump_storage_Elec)
= 0

c_u_res_initial_and_final_storage_state(3502_2019_Mid_Hydrogen_Elec)_:
+0.5 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
-1 e_sto_con(3502_2019_Mid_Hydrogen_Elec)
<= 0

c_u_res_initial_and_final_storage_state(3502_2019_Mid_Pump_storage_Elec)_:
+0.5 cap_sto_c_new(2019_Mid_Pump_storage_Elec)
-1 e_sto_con(3502_2019_Mid_Pump_storage_Elec)
<= 0

c_u_res_initial_and_final_storage_state(3502_2019_North_Hydrogen_Elec)_:
+0.5 cap_sto_c_new(2019_North_Hydrogen_Elec)
-1 e_sto_con(3502_2019_North_Hydrogen_Elec)
<= 0

c_u_res_initial_and_final_storage_state(3502_2019_North_Pump_storage_Elec)_:
+0.5 cap_sto_c_new(2019_North_Pump_storage_Elec)
-1 e_sto_con(3502_2019_North_Pump_storage_Elec)
<= 0

c_u_res_initial_and_final_storage_state(3502_2019_South_Hydrogen_Elec)_:
+0.5 cap_sto_c_new(2019_South_Hydrogen_Elec)
-1 e_sto_con(3502_2019_South_Hydrogen_Elec)
<= 0

c_u_res_initial_and_final_storage_state(3502_2019_South_Pump_storage_Elec)_:
+0.5 cap_sto_c_new(2019_South_Pump_storage_Elec)
-1 e_sto_con(3502_2019_South_Pump_storage_Elec)
<= 0

c_e_def_dsm_variables(3501_2019_Mid_Elec)_:
+1 dsm_down(3501_3501_2019_Mid_Elec)
+1 dsm_down(3501_3502_2019_Mid_Elec)
-1 dsm_up(3501_2019_Mid_Elec)
= 0

c_e_def_dsm_variables(3501_2019_North_Elec)_:
+1 dsm_down(3501_3501_2019_North_Elec)
+1 dsm_down(3501_3502_2019_North_Elec)
-1 dsm_up(3501_2019_North_Elec)
= 0

c_e_def_dsm_variables(3501_2019_South_Elec)_:
+1 dsm_down(3501_3501_2019_South_Elec)
+1 dsm_down(3501_3502_2019_South_Elec)
-0.90000000000000002 dsm_up(3501_2019_South_Elec)
= 0

c_e_def_dsm_variables(3502_2019_Mid_Elec)_:
+1 dsm_down(3502_3501_2019_Mid_Elec)
+1 dsm_down(3502_3502_2019_Mid_Elec)
-1 dsm_up(3502_2019_Mid_Elec)
= 0

c_e_def_dsm_variables(3502_2019_North_Elec)_:
+1 dsm_down(3502_3501_2019_North_Elec)
+1 dsm_down(3502_3502_2019_North_Elec)
-1 dsm_up(3502_2019_North_Elec)
= 0

c_e_def_dsm_variables(3502_2019_South_Elec)_:
+1 dsm_down(3502_3501_2019_South_Elec)
+1 dsm_down(3502_3502_2019_South_Elec)
-0.90000000000000002 dsm_up(3502_2019_South_Elec)
= 0

c_u_res_dsm_upward(3501_2019_Mid_Elec)_:
+1 dsm_up(3501_2019_Mid_Elec)
<= 0

c_u_res_dsm_upward(3501_2019_North_Elec)_:
+1 dsm_up(3501_2019_North_Elec)
<= 500

c_u_res_dsm_upward(3501_2019_South_Elec)_:
+1 dsm_up(3501_2019_South_Elec)
<= 2000

c_u_res_dsm_upward(3502_2019_Mid_Elec)_:
+1 dsm_up(3502_2019_Mid_Elec)
<= 0

c_u_res_dsm_upward(3502_2019_North_Elec)_:
+1 dsm_up(3502_2019_North_Elec)
<= 500

c_u_res_dsm_upward(3502_2019_South_Elec)_:
+1 dsm_up(3502_2019_South_Elec)
<= 2000

c_u_res_dsm_downward(3501_2019_Mid_Elec)_:
+1 dsm_down(3501_3501_2019_Mid_Elec)
+1 dsm_down(3502_3501_2019_Mid_Elec)
<= 0

c_u_res_dsm_downward(3501_2019_North_Elec)_:
+1 dsm_down(3501_3501_2019_North_Elec)
+1 dsm_down(3502_3501_2019_North_Elec)
<= 500

c_u_res_dsm_downward(3501_2019_South_Elec)_:
+1 dsm_down(3501_3501_2019_South_Elec)
+1 dsm_down(3502_3501_2019_South_Elec)
<= 2000

c_u_res_dsm_downward(3502_2019_Mid_Elec)_:
+1 dsm_down(3501_3502_2019_Mid_Elec)
+1 dsm_down(3502_3502_2019_Mid_Elec)
<= 0

c_u_res_dsm_downward(3502_2019_North_Elec)_:
+1 dsm_down(3501_3502_2019_North_Elec)
+1 dsm_down(3502_3502_2019_North_Elec)
<= 500

c_u_res_dsm_downward(3502_2019_South_Elec)_:
+1 dsm_down(3501_3502_2019_South_Elec)
+1 dsm_down(3502_3502_2019_South_Elec)
<= 2000

c_u_res_dsm_maximum(3501_2019_Mid_Elec)_:
+1 dsm_down(3501_3501_2019_Mid_Elec)
+1 dsm_down(3502_3501_2019_Mid_Elec)
+1 dsm_up(3501_2019_Mid_Elec)
<= 0

c_u_res_dsm_maximum(3501_2019_North_Elec)_:
+1 dsm_down(3501_3501_2019_North_Elec)
+1 dsm_down(3502_3501_2019_North_Elec)
+1 dsm_up(3501_2019_North_Elec)
<= 500

c_u_res_dsm_maximum(3501_2019_South_Elec)_:
+1 dsm_down(3501_3501_2019_South_Elec)
+1 dsm_down(3502_3501_2019_South_Elec)
+1 dsm_up(3501_2019_South_Elec)
<= 2000

c_u_res_dsm_maximum(3502_2019_Mid_Elec)_:
+1 dsm_down(3501_3502_2019_Mid_Elec)
+1 dsm_down(3502_3502_2019_Mid_Elec)
+1 dsm_up(3502_2019_Mid_Elec)
<= 0

c_u_res_dsm_maximum(3502_2019_North_Elec)_:
+1 dsm_down(3501_3502_2019_North_Elec)
+1 dsm_down(3502_3502_2019_North_Elec)
+1 dsm_up(3502_2019_North_Elec)
<= 500

c_u_res_dsm_maximum(3502_2019_South_Elec)_:
+1 dsm_down(3501_3502_2019_South_Elec)
+1 dsm_down(3502_3502_2019_South_Elec)
+1 dsm_up(3502_2019_South_Elec)
<= 2000

c_u_res_dsm_recovery(3501_2019_Mid_Elec)_:
+1 dsm_up(3501_2019_Mid_Elec)
<= 0

c_u_res_dsm_recovery(3501_2019_North_Elec)_:
+1 dsm_up(3501_2019_North_Elec)
<= 4000

c_u_res_dsm_recovery(3501_2019_South_Elec)_:
+1 dsm_up(3501_2019_South_Elec)
<= 32000

c_u_res_dsm_recovery(3502_2019_Mid_Elec)_:
+1 dsm_up(3502_2019_Mid_Elec)
<= 0

c_u_res_dsm_recovery(3502_2019_North_Elec)_:
+1 dsm_up(3502_2019_North_Elec)
<= 4000

c_u_res_dsm_recovery(3502_2019_South_Elec)_:
+1 dsm_up(3502_2019_South_Elec)
<= 32000

c_e_res_sell_buy_symmetry(2019_North_Purchase_Elec_buy)_:
-1 cap_pro_new(2019_North_Feed_in)
+1 cap_pro_new(2019_North_Purchase)
= 0

c_e_res_sell_buy_symmetry(2019_South_Purchase_Elec_buy)_:
-1 cap_pro_new(2019_South_Feed_in)
+1 cap_pro_new(2019_South_Purchase)
= 0

c_e_def_process_timevar_output(3501_2019_Mid_Gas_plant_Elec)_:
+1 e_pro_out(3501_2019_Mid_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3501_2019_Mid_Gas_plant)
= 0

c_e_def_process_timevar_output(3501_2019_Mid_Lignite_plant_Elec)_:
+1 e_pro_out(3501_2019_Mid_Lignite_plant_Elec)
-0.40000000000000002 tau_pro(3501_2019_Mid_Lignite_plant)
= 0

c_e_def_process_timevar_output(3502_2019_Mid_Gas_plant_Elec)_:
+1 e_pro_out(3502_2019_Mid_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3502_2019_Mid_Gas_plant)
= 0

c_e_def_process_timevar_output(3502_2019_Mid_Lignite_plant_Elec)_:
+1 e_pro_out(3502_2019_Mid_Lignite_plant_Elec)
-0.40000000000000002 tau_pro(3502_2019_Mid_Lignite_plant)
= 0

c_e_res_vertex(3501_2019_Mid_Biomass_Stock)_:
+1 e_co_stock(3501_2019_Mid_Biomass_Stock)
-1 e_pro_in(3501_2019_Mid_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3501_2019_Mid_Coal_Stock)_:
+1 e_co_stock(3501_2019_Mid_Coal_Stock)
= 0

c_e_res_vertex(3501_2019_Mid_Elec_Demand)_:
+1 dsm_down(3501_3501_2019_Mid_Elec)
+1 dsm_down(3502_3501_2019_Mid_Elec)
-1 dsm_up(3501_2019_Mid_Elec)
+1 e_pro_out(3501_2019_Mid_Biomass_plant_Elec)
+1 e_pro_out(3501_2019_Mid_Gas_plant_Elec)
+1 e_pro_out(3501_2019_Mid_Hydro_plant_Elec)
+1 e_pro_out(3501_2019_Mid_Lignite_plant_Elec)
+1 e_pro_out(3501_2019_Mid_Photovoltaics_Elec)
+1 e_pro_out(3501_2019_Mid_Slack_powerplant_Elec)
+1 e_pro_out(3501_2019_Mid_Wind_park_Elec)
-1 e_sto_in(3501_2019_Mid_Hydrogen_Elec)
-1 e_sto_in(3501_2019_Mid_Pump_storage_Elec)
+1 e_sto_out(3501_2019_Mid_Hydrogen_Elec)
+1 e_sto_out(3501_2019_Mid_Pump_storage_Elec)
-1 e_tra_in(3501_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3501_2019_North_Mid_hvac_Elec)
+1 e_tra_out(3501_2019_South_Mid_hvac_Elec)
= 44444.75886803514

c_e_res_vertex(3501_2019_Mid_Gas_Stock)_:
+1 e_co_stock(3501_2019_Mid_Gas_Stock)
-1 e_pro_in(3501_2019_Mid_Gas_plant_Gas)
= 0

c_e_res_vertex(3501_2019_Mid_Lignite_Stock)_:
+1 e_co_stock(3501_2019_Mid_Lignite_Stock)
-1 e_pro_in(3501_2019_Mid_Lignite_plant_Lignite)
= 0

c_e_res_vertex(3501_2019_Mid_Slack_Stock)_:
+1 e_co_stock(3501_2019_Mid_Slack_Stock)
-1 e_pro_in(3501_2019_Mid_Slack_powerplant_Slack)
= 0

c_e_res_vertex(3501_2019_North_Biomass_Stock)_:
+1 e_co_stock(3501_2019_North_Biomass_Stock)
-1 e_pro_in(3501_2019_North_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3501_2019_North_Coal_Stock)_:
+1 e_co_stock(3501_2019_North_Coal_Stock)
-1 e_pro_in(3501_2019_North_Coal_plant_Coal)
= 0

c_e_res_vertex(3501_2019_North_Elec_Demand)_:
+1 dsm_down(3501_3501_2019_North_Elec)
+1 dsm_down(3502_3501_2019_North_Elec)
-1 dsm_up(3501_2019_North_Elec)
-1 e_pro_in(3501_2019_North_Feed_in_Elec)
+1 e_pro_out(3501_2019_North_Biomass_plant_Elec)
+1 e_pro_out(3501_2019_North_Coal_plant_Elec)
+1 e_pro_out(3501_2019_North_Gas_plant_Elec)
+1 e_pro_out(3501_2019_North_Hydro_plant_Elec)
+1 e_pro_out(3501_2019_North_Photovoltaics_Elec)
+1 e_pro_out(3501_2019_North_Purchase_Elec)
+1 e_pro_out(3501_2019_North_Slack_powerplant_Elec)
+1 e_pro_out(3501_2019_North_Wind_park_Elec)
-1 e_sto_in(3501_2019_North_Hydrogen_Elec)
-1 e_sto_in(3501_2019_North_Pump_storage_Elec)
+1 e_sto_out(3501_2019_North_Hydrogen_Elec)
+1 e_sto_out(3501_2019_North_Pump_storage_Elec)
-1 e_tra_in(3501_2019_North_Mid_hvac_Elec)
-1 e_tra_in(3501_2019_North_South_hvac_Elec)
+1 e_tra_out(3501_2019_South_North_hvac_Elec)
= 9069.3812865567998

c_e_res_vertex(3501_2019_North_Elec_buy_Buy)_:
+1 e_co_buy(3501_2019_North_Elec_buy_Buy)
-1 e_pro_in(3501_2019_North_Purchase_Elec_buy)
= 0

c_e_res_vertex(3501_2019_North_Elec_sell_Sell)_:
-1 e_co_sell(3501_2019_North_Elec_sell_Sell)
+1 e_pro_out(3501_2019_North_Feed_in_Elec_sell)
= 0

c_e_res_vertex(3501_2019_North_Gas_Stock)_:
+1 e_co_stock(3501_2019_North_Gas_Stock)
-1 e_pro_in(3501_2019_North_Gas_plant_Gas)
= 0

c_e_res_vertex(3501_2019_North_Lignite_Stock)_:
+1 e_co_stock(3501_2019_North_Lignite_Stock)
= 0

c_e_res_vertex(3501_2019_North_Slack_Stock)_:
+1 e_co_stock(3501_2019_North_Slack_Stock)
-1 e_pro_in(3501_2019_North_Slack_powerplant_Slack)
= 0

c_e_res_vertex(3501_2019_South_Biomass_Stock)_:
+1 e_co_stock(3501_2019_South_Biomass_Stock)
-1 e_pro_in(3501_2019_South_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3501_2019_South_Coal_Stock)_:
+1 e_co_stock(3501_2019_South_Coal_Stock)
-1 e_pro_in(3501_2019_South_Coal_plant_Coal)
= 0

c_e_res_vertex(3501_2019_South_Elec_Demand)_:
+1 dsm_down(3501_3501_2019_South_Elec)
+1 dsm_down(3502_3501_2019_South_Elec)
-1 dsm_up(3501_2019_South_Elec)
-1 e_pro_in(3501_2019_South_Feed_in_Elec)
+1 e_pro_out(3501_2019_South_Biomass_plant_Elec)
+1 e_pro_out(3501_2019_South_Coal_plant_Elec)
+1 e_pro_out(3501_2019_South_Gas_plant_Elec)
+1 e_pro_out(3501_2019_South_Hydro_plant_Elec)
+1 e_pro_out(3501_2019_South_Photovoltaics_Elec)
+1 e_pro_out(3501_2019_South_Purchase_Elec)
+1 e_pro_out(3501_2019_South_Slack_powerplant_Elec)
+1 e_pro_out(3501_2019_South_Wind_park_Elec)
-1 e_sto_in(3501_2019_South_Hydrogen_Elec)
-1 e_sto_in(3501_2019_South_Pump_storage_Elec)
+1 e_sto_out(3501_2019_South_Hydrogen_Elec)
+1 e_sto_out(3501_2019_South_Pump_storage_Elec)
-1 e_tra_in(3501_2019_South_Mid_hvac_Elec)
-1 e_tra_in(3501_2019_South_North_hvac_Elec)
+1 e_tra_out(3501_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3501_2019_North_South_hvac_Elec)
= 4993.5283769650259

c_e_res_vertex(3501_2019_South_Elec_buy_Buy)_:
+1 e_co_buy(3501_2019_South_Elec_buy_Buy)
-1 e_pro_in(3501_2019_South_Purchase_Elec_buy)
= 0

c_e_res_vertex(3501_2019_South_Elec_sell_Sell)_:
-1 e_co_sell(3501_2019_South_Elec_sell_Sell)
+1 e_pro_out(3501_2019_South_Feed_in_Elec_sell)
= 0

c_e_res_vertex(3501_2019_South_Gas_Stock)_:
+1 e_co_stock(3501_2019_South_Gas_Stock)
-1 e_pro_in(3501_2019_South_Gas_plant_Gas)
= 0

c_e_res_vertex(3501_2019_South_Lignite_Stock)_:
+1 e_co_stock(3501_2019_South_Lignite_Stock)
= 0

c_e_res_vertex(3501_2019_South_Slack_Stock)_:
+1 e_co_stock(3501_2019_South_Slack_Stock)
-1 e_pro_in(3501_2019_South_Slack_powerplant_Slack)
= 0

c_e_res_vertex(3502_2019_Mid_Biomass_Stock)_:
+1 e_co_stock(3502_2019_Mid_Biomass_Stock)
-1 e_pro_in(3502_2019_Mid_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3502_2019_Mid_Coal_Stock)_:
+1 e_co_stock(3502_2019_Mid_Coal_Stock)
= 0

c_e_res_vertex(3502_2019_Mid_Elec_Demand)_:
+1 dsm_down(3501_3502_2019_Mid_Elec)
+1 dsm_down(3502_3502_2019_Mid_Elec)
-1 dsm_up(3502_2019_Mid_Elec)
+1 e_pro_out(3502_2019_Mid_Biomass_plant_Elec)
+1 e_pro_out(3502_2019_Mid_Gas_plant_Elec)
+1 e_pro_out(3502_2019_Mid_Hydro_plant_Elec)
+1 e_pro_out(3502_2019_Mid_Lignite_plant_Elec)
+1 e_pro_out(3502_2019_Mid_Photovoltaics_Elec)
+1 e_pro_out(3502_2019_Mid_Slack_powerplant_Elec)
+1 e_pro_out(3502_2019_Mid_Wind_park_Elec)
-1 e_sto_in(3502_2019_Mid_Hydrogen_Elec)
-1 e_sto_in(3502_2019_Mid_Pump_storage_Elec)
+1 e_sto_out(3502_2019_Mid_Hydrogen_Elec)
+1 e_sto_out(3502_2019_Mid_Pump_storage_Elec)
-1 e_tra_in(3502_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3502_2019_North_Mid_hvac_Elec)
+1 e_tra_out(3502_2019_South_Mid_hvac_Elec)
= 41205.826768155195

c_e_res_vertex(3502_2019_Mid_Gas_Stock)_:
+1 e_co_stock(3502_2019_Mid_Gas_Stock)
-1 e_pro_in(3502_2019_Mid_Gas_plant_Gas)
= 0

c_e_res_vertex(3502_2019_Mid_Lignite_Stock)_:
+1 e_co_stock(3502_2019_Mid_Lignite_Stock)
-1 e_pro_in(3502_2019_Mid_Lignite_plant_Lignite)
= 0

c_e_res_vertex(3502_2019_Mid_Slack_Stock)_:
+1 e_co_stock(3502_2019_Mid_Slack_Stock)
-1 e_pro_in(3502_2019_Mid_Slack_powerplant_Slack)
= 0

c_e_res_vertex(3502_2019_North_Biomass_Stock)_:
+1 e_co_stock(3502_2019_North_Biomass_Stock)
-1 e_pro_in(3502_2019_North_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3502_2019_North_Coal_Stock)_:
+1 e_co_stock(3502_2019_North_Coal_Stock)
-1 e_pro_in(3502_2019_North_Coal_plant_Coal)
= 0

c_e_res_vertex(3502_2019_North_Elec_Demand)_:
+1 dsm_down(3501_3502_2019_North_Elec)
+1 dsm_down(3502_3502_2019_North_Elec)
-1 dsm_up(3502_2019_North_Elec)
-1 e_pro_in(3502_2019_North_Feed_in_Elec)
+1 e_pro_out(3502_2019_North_Biomass_plant_Elec)
+1 e_pro_out(3502_2019_North_Coal_plant_Elec)
+1 e_pro_out(3502_2019_North_Gas_plant_Elec)
+1 e_pro_out(3502_2019_North_Hydro_plant_Elec)
+1 e_pro_out(3502_2019_North_Photovoltaics_Elec)
+1 e_pro_out(3502_2019_North_Purchase_Elec)
+1 e_pro_out(3502_2019_North_Slack_powerplant_Elec)
+1 e_pro_out(3502_2019_North_Wind_park_Elec)
-1 e_sto_in(3502_2019_North_Hydrogen_Elec)
-1 e_sto_in(3502_2019_North_Pump_storage_Elec)
+1 e_sto_out(3502_2019_North_Hydrogen_Elec)
+1 e_sto_out(3502_2019_North_Pump_storage_Elec)
-1 e_tra_in(3502_2019_North_Mid_hvac_Elec)
-1 e_tra_in(3502_2019_North_South_hvac_Elec)
+1 e_tra_out(3502_2019_South_North_hvac_Elec)
= 8806.8051057068624

c_e_res_vertex(3502_2019_North_Elec_buy_Buy)_:
+1 e_co_buy(3502_2019_North_Elec_buy_Buy)
-1 e_pro_in(3502_2019_North_Purchase_Elec_buy)
= 0

c_e_res_vertex(3502_2019_North_Elec_sell_Sell)_:
-1 e_co_sell(3502_2019_North_Elec_sell_Sell)
+1 e_pro_out(3502_2019_North_Feed_in_Elec_sell)
= 0

c_e_res_vertex(3502_2019_North_Gas_Stock)_:
+1 e_co_stock(3502_2019_North_Gas_Stock)
-1 e_pro_in(3502_2019_North_Gas_plant_Gas)
= 0

c_e_res_vertex(3502_2019_North_Lignite_Stock)_:
+1 e_co_stock(3502_2019_North_Lignite_Stock)
= 0

c_e_res_vertex(3502_2019_North_Slack_Stock)_:
+1 e_co_stock(3502_2019_North_Slack_Stock)
-1 e_pro_in(3502_2019_North_Slack_powerplant_Slack)
= 0

c_e_res_vertex(3502_2019_South_Biomass_Stock)_:
+1 e_co_stock(3502_2019_South_Biomass_Stock)
-1 e_pro_in(3502_2019_South_Biomass_plant_Biomass)
= 0

c_e_res_vertex(3502_2019_South_Coal_Stock)_:
+1 e_co_stock(3502_2019_South_Coal_Stock)
-1 e_pro_in(3502_2019_South_Coal_plant_Coal)
= 0

c_e_res_vertex(3502_2019_South_Elec_Demand)_:
+1 dsm_down(3501_3502_2019_South_Elec)
+1 dsm_down(3502_3502_2019_South_Elec)
-1 dsm_up(3502_2019_South_Elec)
-1 e_pro_in(3502_2019_South_Feed_in_Elec)
+1 e_pro_out(3502_2019_South_Biomass_plant_Elec)
+1 e_pro_out(3502_2019_South_Coal_plant_Elec)
+1 e_pro_out(3502_2019_South_Gas_plant_Elec)
+1 e_pro_out(3502_2019_South_Hydro_plant_Elec)
+1 e_pro_out(3502_2019_South_Photovoltaics_Elec)
+1 e_pro_out(3502_2019_South_Purchase_Elec)
+1 e_pro_out(3502_2019_South_Slack_powerplant_Elec)
+1 e_pro_out(3502_2019_South_Wind_park_Elec)
-1 e_sto_in(3502_2019_South_Hydrogen_Elec)
-1 e_sto_in(3502_2019_South_Pump_storage_Elec)
+1 e_sto_out(3502_2019_South_Hydrogen_Elec)
+1 e_sto_out(3502_2019_South_Pump_storage_Elec)
-1 e_tra_in(3502_2019_South_Mid_hvac_Elec)
-1 e_tra_in(3502_2019_South_North_hvac_Elec)
+1 e_tra_out(3502_2019_Mid_South_hvac_Elec)
+1 e_tra_out(3502_2019_North_South_hvac_Elec)
= 5163.1129508597396

c_e_res_vertex(3502_2019_South_Elec_buy_Buy)_:
+1 e_co_buy(3502_2019_South_Elec_buy_Buy)
-1 e_pro_in(3502_2019_South_Purchase_Elec_buy)
= 0

c_e_res_vertex(3502_2019_South_Elec_sell_Sell)_:
-1 e_co_sell(3502_2019_South_Elec_sell_Sell)
+1 e_pro_out(3502_2019_South_Feed_in_Elec_sell)
= 0

c_e_res_vertex(3502_2019_South_Gas_Stock)_:
+1 e_co_stock(3502_2019_South_Gas_Stock)
-1 e_pro_in(3502_2019_South_Gas_plant_Gas)
= 0

c_e_res_vertex(3502_2019_South_Lignite_Stock)_:
+1 e_co_stock(3502_2019_South_Lignite_Stock)
= 0

c_e_res_vertex(3502_2019_South_Slack_Stock)_:
+1 e_co_stock(3502_2019_South_Slack_Stock)
-1 e_pro_in(3502_2019_South_Slack_powerplant_Slack)
= 0

c_e_def_process_input(3501_2019_Mid_Biomass_plant_Biomass)_:
+1 e_pro_in(3501_2019_Mid_Biomass_plant_Biomass)
-1 tau_pro(3501_2019_Mid_Biomass_plant)
= 0

c_e_def_process_input(3501_2019_Mid_Hydro_plant_Hydro)_:
+1 e_pro_in(3501_2019_Mid_Hydro_plant_Hydro)
-1 tau_pro(3501_2019_Mid_Hydro_plant)
= 0

c_e_def_process_input(3501_2019_Mid_Photovoltaics_Solar)_:
+1 e_pro_in(3501_2019_Mid_Photovoltaics_Solar)
-1 tau_pro(3501_2019_Mid_Photovoltaics)
= 0

c_e_def_process_input(3501_2019_Mid_Slack_powerplant_Slack)_:
+1 e_pro_in(3501_2019_Mid_Slack_powerplant_Slack)
-1 tau_pro(3501_2019_Mid_Slack_powerplant)
= 0

c_e_def_process_input(3501_2019_Mid_Wind_park_Wind)_:
+1 e_pro_in(3501_2019_Mid_Wind_park_Wind)
-1 tau_pro(3501_2019_Mid_Wind_park)
= 0

c_e_def_process_input(3501_2019_North_Biomass_plant_Biomass)_:
+1 e_pro_in(3501_2019_North_Biomass_plant_Biomass)
-1 tau_pro(3501_2019_North_Biomass_plant)
= 0

c_e_def_process_input(3501_2019_North_Feed_in_Elec)_:
+1 e_pro_in(3501_2019_North_Feed_in_Elec)
-1 tau_pro(3501_2019_North_Feed_in)
= 0

c_e_def_process_input(3501_2019_North_Hydro_plant_Hydro)_:
+1 e_pro_in(3501_2019_North_Hydro_plant_Hydro)
-1 tau_pro(3501_2019_North_Hydro_plant)
= 0

c_e_def_process_input(3501_2019_North_Photovoltaics_Solar)_:
+1 e_pro_in(3501_2019_North_Photovoltaics_Solar)
-1 tau_pro(3501_2019_North_Photovoltaics)
= 0

c_e_def_process_input(3501_2019_North_Purchase_Elec_buy)_:
+1 e_pro_in(3501_2019_North_Purchase_Elec_buy)
-1 tau_pro(3501_2019_North_Purchase)
= 0

c_e_def_process_input(3501_2019_North_Slack_powerplant_Slack)_:
+1 e_pro_in(3501_2019_North_Slack_powerplant_Slack)
-1 tau_pro(3501_2019_North_Slack_powerplant)
= 0

c_e_def_process_input(3501_2019_North_Wind_park_Wind)_:
+1 e_pro_in(3501_2019_North_Wind_park_Wind)
-1 tau_pro(3501_2019_North_Wind_park)
= 0

c_e_def_process_input(3501_2019_South_Biomass_plant_Biomass)_:
+1 e_pro_in(3501_2019_South_Biomass_plant_Biomass)
-1 tau_pro(3501_2019_South_Biomass_plant)
= 0

c_e_def_process_input(3501_2019_South_Feed_in_Elec)_:
+1 e_pro_in(3501_2019_South_Feed_in_Elec)
-1 tau_pro(3501_2019_South_Feed_in)
= 0

c_e_def_process_input(3501_2019_South_Hydro_plant_Hydro)_:
+1 e_pro_in(3501_2019_South_Hydro_plant_Hydro)
-1 tau_pro(3501_2019_South_Hydro_plant)
= 0

c_e_def_process_input(3501_2019_South_Photovoltaics_Solar)_:
+1 e_pro_in(3501_2019_South_Photovoltaics_Solar)
-1 tau_pro(3501_2019_South_Photovoltaics)
= 0

c_e_def_process_input(3501_2019_South_Purchase_Elec_buy)_:
+1 e_pro_in(3501_2019_South_Purchase_Elec_buy)
-1 tau_pro(3501_2019_South_Purchase)
= 0

c_e_def_process_input(3501_2019_South_Slack_powerplant_Slack)_:
+1 e_pro_in(3501_2019_South_Slack_powerplant_Slack)
-1 tau_pro(3501_2019_South_Slack_powerplant)
= 0

c_e_def_process_input(3501_2019_South_Wind_park_Wind)_:
+1 e_pro_in(3501_2019_South_Wind_park_Wind)
-1 tau_pro(3501_2019_South_Wind_park)
= 0

c_e_def_process_input(3502_2019_Mid_Biomass_plant_Biomass)_:
+1 e_pro_in(3502_2019_Mid_Biomass_plant_Biomass)
-1 tau_pro(3502_2019_Mid_Biomass_plant)
= 0

c_e_def_process_input(3502_2019_Mid_Hydro_plant_Hydro)_:
+1 e_pro_in(3502_2019_Mid_Hydro_plant_Hydro)
-1 tau_pro(3502_2019_Mid_Hydro_plant)
= 0

c_e_def_process_input(3502_2019_Mid_Photovoltaics_Solar)_:
+1 e_pro_in(3502_2019_Mid_Photovoltaics_Solar)
-1 tau_pro(3502_2019_Mid_Photovoltaics)
= 0

c_e_def_process_input(3502_2019_Mid_Slack_powerplant_Slack)_:
+1 e_pro_in(3502_2019_Mid_Slack_powerplant_Slack)
-1 tau_pro(3502_2019_Mid_Slack_powerplant)
= 0

c_e_def_process_input(3502_2019_Mid_Wind_park_Wind)_:
+1 e_pro_in(3502_2019_Mid_Wind_park_Wind)
-1 tau_pro(3502_2019_Mid_Wind_park)
= 0

c_e_def_process_input(3502_2019_North_Biomass_plant_Biomass)_:
+1 e_pro_in(3502_2019_North_Biomass_plant_Biomass)
-1 tau_pro(3502_2019_North_Biomass_plant)
= 0

c_e_def_process_input(3502_2019_North_Feed_in_Elec)_:
+1 e_pro_in(3502_2019_North_Feed_in_Elec)
-1 tau_pro(3502_2019_North_Feed_in)
= 0

c_e_def_process_input(3502_2019_North_Hydro_plant_Hydro)_:
+1 e_pro_in(3502_2019_North_Hydro_plant_Hydro)
-1 tau_pro(3502_2019_North_Hydro_plant)
= 0

c_e_def_process_input(3502_2019_North_Photovoltaics_Solar)_:
+1 e_pro_in(3502_2019_North_Photovoltaics_Solar)
-1 tau_pro(3502_2019_North_Photovoltaics)
= 0

c_e_def_process_input(3502_2019_North_Purchase_Elec_buy)_:
+1 e_pro_in(3502_2019_North_Purchase_Elec_buy)
-1 tau_pro(3502_2019_North_Purchase)
= 0

c_e_def_process_input(3502_2019_North_Slack_powerplant_Slack)_:
+1 e_pro_in(3502_2019_North_Slack_powerplant_Slack)
-1 tau_pro(3502_2019_North_Slack_powerplant)
= 0

c_e_def_process_input(3502_2019_North_Wind_park_Wind)_:
+1 e_pro_in(3502_2019_North_Wind_park_Wind)
-1 tau_pro(3502_2019_North_Wind_park)
= 0

c_e_def_process_input(3502_2019_South_Biomass_plant_Biomass)_:
+1 e_pro_in(3502_2019_South_Biomass_plant_Biomass)
-1 tau_pro(3502_2019_South_Biomass_plant)
= 0

c_e_def_process_input(3502_2019_South_Feed_in_Elec)_:
+1 e_pro_in(3502_2019_South_Feed_in_Elec)
-1 tau_pro(3502_2019_South_Feed_in)
= 0

c_e_def_process_input(3502_2019_South_Hydro_plant_Hydro)_:
+1 e_pro_in(3502_2019_South_Hydro_plant_Hydro)
-1 tau_pro(3502_2019_South_Hydro_plant)
= 0

c_e_def_process_input(3502_2019_South_Photovoltaics_Solar)_:
+1 e_pro_in(3502_2019_South_Photovoltaics_Solar)
-1 tau_pro(3502_2019_South_Photovoltaics)
= 0

c_e_def_process_input(3502_2019_South_Purchase_Elec_buy)_:
+1 e_pro_in(3502_2019_South_Purchase_Elec_buy)
-1 tau_pro(3502_2019_South_Purchase)
= 0

c_e_def_process_input(3502_2019_South_Slack_powerplant_Slack)_:
+1 e_pro_in(3502_2019_South_Slack_powerplant_Slack)
-1 tau_pro(3502_2019_South_Slack_powerplant)
= 0

c_e_def_process_input(3502_2019_South_Wind_park_Wind)_:
+1 e_pro_in(3502_2019_South_Wind_park_Wind)
-1 tau_pro(3502_2019_South_Wind_park)
= 0

c_e_def_process_output(3501_2019_Mid_Biomass_plant_CO2)_:
+1 e_pro_out(3501_2019_Mid_Biomass_plant_CO2)
= 0

c_e_def_process_output(3501_2019_Mid_Biomass_plant_Elec)_:
+1 e_pro_out(3501_2019_Mid_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3501_2019_Mid_Biomass_plant)
= 0

c_e_def_process_output(3501_2019_Mid_Hydro_plant_Elec)_:
+1 e_pro_out(3501_2019_Mid_Hydro_plant_Elec)
-1 tau_pro(3501_2019_Mid_Hydro_plant)
= 0

c_e_def_process_output(3501_2019_Mid_Photovoltaics_Elec)_:
+1 e_pro_out(3501_2019_Mid_Photovoltaics_Elec)
-1 tau_pro(3501_2019_Mid_Photovoltaics)
= 0

c_e_def_process_output(3501_2019_Mid_Slack_powerplant_CO2)_:
+1 e_pro_out(3501_2019_Mid_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3501_2019_Mid_Slack_powerplant_Elec)_:
+1 e_pro_out(3501_2019_Mid_Slack_powerplant_Elec)
-1 tau_pro(3501_2019_Mid_Slack_powerplant)
= 0

c_e_def_process_output(3501_2019_Mid_Wind_park_Elec)_:
+1 e_pro_out(3501_2019_Mid_Wind_park_Elec)
-1 tau_pro(3501_2019_Mid_Wind_park)
= 0

c_e_def_process_output(3501_2019_North_Biomass_plant_CO2)_:
+1 e_pro_out(3501_2019_North_Biomass_plant_CO2)
= 0

c_e_def_process_output(3501_2019_North_Biomass_plant_Elec)_:
+1 e_pro_out(3501_2019_North_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3501_2019_North_Biomass_plant)
= 0

c_e_def_process_output(3501_2019_North_Coal_plant_Elec)_:
+1 e_pro_out(3501_2019_North_Coal_plant_Elec)
-0.40000000000000002 tau_pro(3501_2019_North_Coal_plant)
= 0

c_e_def_process_output(3501_2019_North_Feed_in_Elec_sell)_:
+1 e_pro_out(3501_2019_North_Feed_in_Elec_sell)
-1 tau_pro(3501_2019_North_Feed_in)
= 0

c_e_def_process_output(3501_2019_North_Gas_plant_Elec)_:
+1 e_pro_out(3501_2019_North_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3501_2019_North_Gas_plant)
= 0

c_e_def_process_output(3501_2019_North_Hydro_plant_Elec)_:
+1 e_pro_out(3501_2019_North_Hydro_plant_Elec)
-1 tau_pro(3501_2019_North_Hydro_plant)
= 0

c_e_def_process_output(3501_2019_North_Photovoltaics_Elec)_:
+1 e_pro_out(3501_2019_North_Photovoltaics_Elec)
-1 tau_pro(3501_2019_North_Photovoltaics)
= 0

c_e_def_process_output(3501_2019_North_Purchase_CO2)_:
+1 e_pro_out(3501_2019_North_Purchase_CO2)
-0.00050000000000000001 tau_pro(3501_2019_North_Purchase)
= 0

c_e_def_process_output(3501_2019_North_Purchase_Elec)_:
+1 e_pro_out(3501_2019_North_Purchase_Elec)
-1 tau_pro(3501_2019_North_Purchase)
= 0

c_e_def_process_output(3501_2019_North_Slack_powerplant_CO2)_:
+1 e_pro_out(3501_2019_North_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3501_2019_North_Slack_powerplant_Elec)_:
+1 e_pro_out(3501_2019_North_Slack_powerplant_Elec)
-1 tau_pro(3501_2019_North_Slack_powerplant)
= 0

c_e_def_process_output(3501_2019_North_Wind_park_Elec)_:
+1 e_pro_out(3501_2019_North_Wind_park_Elec)
-1 tau_pro(3501_2019_North_Wind_park)
= 0

c_e_def_process_output(3501_2019_South_Biomass_plant_CO2)_:
+1 e_pro_out(3501_2019_South_Biomass_plant_CO2)
= 0

c_e_def_process_output(3501_2019_South_Biomass_plant_Elec)_:
+1 e_pro_out(3501_2019_South_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3501_2019_South_Biomass_plant)
= 0

c_e_def_process_output(3501_2019_South_Coal_plant_Elec)_:
+1 e_pro_out(3501_2019_South_Coal_plant_Elec)
-0.40000000000000002 tau_pro(3501_2019_South_Coal_plant)
= 0

c_e_def_process_output(3501_2019_South_Feed_in_Elec_sell)_:
+1 e_pro_out(3501_2019_South_Feed_in_Elec_sell)
-1 tau_pro(3501_2019_South_Feed_in)
= 0

c_e_def_process_output(3501_2019_South_Gas_plant_Elec)_:
+1 e_pro_out(3501_2019_South_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3501_2019_South_Gas_plant)
= 0

c_e_def_process_output(3501_2019_South_Hydro_plant_Elec)_:
+1 e_pro_out(3501_2019_South_Hydro_plant_Elec)
-1 tau_pro(3501_2019_South_Hydro_plant)
= 0

c_e_def_process_output(3501_2019_South_Photovoltaics_Elec)_:
+1 e_pro_out(3501_2019_South_Photovoltaics_Elec)
-1 tau_pro(3501_2019_South_Photovoltaics)
= 0

c_e_def_process_output(3501_2019_South_Purchase_CO2)_:
+1 e_pro_out(3501_2019_South_Purchase_CO2)
-0.00050000000000000001 tau_pro(3501_2019_South_Purchase)
= 0

c_e_def_process_output(3501_2019_South_Purchase_Elec)_:
+1 e_pro_out(3501_2019_South_Purchase_Elec)
-1 tau_pro(3501_2019_South_Purchase)
= 0

c_e_def_process_output(3501_2019_South_Slack_powerplant_CO2)_:
+1 e_pro_out(3501_2019_South_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3501_2019_South_Slack_powerplant_Elec)_:
+1 e_pro_out(3501_2019_South_Slack_powerplant_Elec)
-1 tau_pro(3501_2019_South_Slack_powerplant)
= 0

c_e_def_process_output(3501_2019_South_Wind_park_Elec)_:
+1 e_pro_out(3501_2019_South_Wind_park_Elec)
-1 tau_pro(3501_2019_South_Wind_park)
= 0

c_e_def_process_output(3502_2019_Mid_Biomass_plant_CO2)_:
+1 e_pro_out(3502_2019_Mid_Biomass_plant_CO2)
= 0

c_e_def_process_output(3502_2019_Mid_Biomass_plant_Elec)_:
+1 e_pro_out(3502_2019_Mid_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3502_2019_Mid_Biomass_plant)
= 0

c_e_def_process_output(3502_2019_Mid_Hydro_plant_Elec)_:
+1 e_pro_out(3502_2019_Mid_Hydro_plant_Elec)
-1 tau_pro(3502_2019_Mid_Hydro_plant)
= 0

c_e_def_process_output(3502_2019_Mid_Photovoltaics_Elec)_:
+1 e_pro_out(3502_2019_Mid_Photovoltaics_Elec)
-1 tau_pro(3502_2019_Mid_Photovoltaics)
= 0

c_e_def_process_output(3502_2019_Mid_Slack_powerplant_CO2)_:
+1 e_pro_out(3502_2019_Mid_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3502_2019_Mid_Slack_powerplant_Elec)_:
+1 e_pro_out(3502_2019_Mid_Slack_powerplant_Elec)
-1 tau_pro(3502_2019_Mid_Slack_powerplant)
= 0

c_e_def_process_output(3502_2019_Mid_Wind_park_Elec)_:
+1 e_pro_out(3502_2019_Mid_Wind_park_Elec)
-1 tau_pro(3502_2019_Mid_Wind_park)
= 0

c_e_def_process_output(3502_2019_North_Biomass_plant_CO2)_:
+1 e_pro_out(3502_2019_North_Biomass_plant_CO2)
= 0

c_e_def_process_output(3502_2019_North_Biomass_plant_Elec)_:
+1 e_pro_out(3502_2019_North_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3502_2019_North_Biomass_plant)
= 0

c_e_def_process_output(3502_2019_North_Coal_plant_Elec)_:
+1 e_pro_out(3502_2019_North_Coal_plant_Elec)
-0.40000000000000002 tau_pro(3502_2019_North_Coal_plant)
= 0

c_e_def_process_output(3502_2019_North_Feed_in_Elec_sell)_:
+1 e_pro_out(3502_2019_North_Feed_in_Elec_sell)
-1 tau_pro(3502_2019_North_Feed_in)
= 0

c_e_def_process_output(3502_2019_North_Gas_plant_Elec)_:
+1 e_pro_out(3502_2019_North_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3502_2019_North_Gas_plant)
= 0

c_e_def_process_output(3502_2019_North_Hydro_plant_Elec)_:
+1 e_pro_out(3502_2019_North_Hydro_plant_Elec)
-1 tau_pro(3502_2019_North_Hydro_plant)
= 0

c_e_def_process_output(3502_2019_North_Photovoltaics_Elec)_:
+1 e_pro_out(3502_2019_North_Photovoltaics_Elec)
-1 tau_pro(3502_2019_North_Photovoltaics)
= 0

c_e_def_process_output(3502_2019_North_Purchase_CO2)_:
+1 e_pro_out(3502_2019_North_Purchase_CO2)
-0.00050000000000000001 tau_pro(3502_2019_North_Purchase)
= 0

c_e_def_process_output(3502_2019_North_Purchase_Elec)_:
+1 e_pro_out(3502_2019_North_Purchase_Elec)
-1 tau_pro(3502_2019_North_Purchase)
= 0

c_e_def_process_output(3502_2019_North_Slack_powerplant_CO2)_:
+1 e_pro_out(3502_2019_North_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3502_2019_North_Slack_powerplant_Elec)_:
+1 e_pro_out(3502_2019_North_Slack_powerplant_Elec)
-1 tau_pro(3502_2019_North_Slack_powerplant)
= 0

c_e_def_process_output(3502_2019_North_Wind_park_Elec)_:
+1 e_pro_out(3502_2019_North_Wind_park_Elec)
-1 tau_pro(3502_2019_North_Wind_park)
= 0

c_e_def_process_output(3502_2019_South_Biomass_plant_CO2)_:
+1 e_pro_out(3502_2019_South_Biomass_plant_CO2)
= 0

c_e_def_process_output(3502_2019_South_Biomass_plant_Elec)_:
+1 e_pro_out(3502_2019_South_Biomass_plant_Elec)
-0.34999999999999998 tau_pro(3502_2019_South_Biomass_plant)
= 0

c_e_def_process_output(3502_2019_South_Coal_plant_Elec)_:
+1 e_pro_out(3502_2019_South_Coal_plant_Elec)
-0.40000000000000002 tau_pro(3502_2019_South_Coal_plant)
= 0

c_e_def_process_output(3502_2019_South_Feed_in_Elec_sell)_:
+1 e_pro_out(3502_2019_South_Feed_in_Elec_sell)
-1 tau_pro(3502_2019_South_Feed_in)
= 0

c_e_def_process_output(3502_2019_South_Gas_plant_Elec)_:
+1 e_pro_out(3502_2019_South_Gas_plant_Elec)
-0.59999999999999998 tau_pro(3502_2019_South_Gas_plant)
= 0

c_e_def_process_output(3502_2019_South_Hydro_plant_Elec)_:
+1 e_pro_out(3502_2019_South_Hydro_plant_Elec)
-1 tau_pro(3502_2019_South_Hydro_plant)
= 0

c_e_def_process_output(3502_2019_South_Photovoltaics_Elec)_:
+1 e_pro_out(3502_2019_South_Photovoltaics_Elec)
-1 tau_pro(3502_2019_South_Photovoltaics)
= 0

c_e_def_process_output(3502_2019_South_Purchase_CO2)_:
+1 e_pro_out(3502_2019_South_Purchase_CO2)
-0.00050000000000000001 tau_pro(3502_2019_South_Purchase)
= 0

c_e_def_process_output(3502_2019_South_Purchase_Elec)_:
+1 e_pro_out(3502_2019_South_Purchase_Elec)
-1 tau_pro(3502_2019_South_Purchase)
= 0

c_e_def_process_output(3502_2019_South_Slack_powerplant_CO2)_:
+1 e_pro_out(3502_2019_South_Slack_powerplant_CO2)
= 0

c_e_def_process_output(3502_2019_South_Slack_powerplant_Elec)_:
+1 e_pro_out(3502_2019_South_Slack_powerplant_Elec)
-1 tau_pro(3502_2019_South_Slack_powerplant)
= 0

c_e_def_process_output(3502_2019_South_Wind_park_Elec)_:
+1 e_pro_out(3502_2019_South_Wind_park_Elec)
-1 tau_pro(3502_2019_South_Wind_park)
= 0

c_e_def_intermittent_supply(3501_2019_Mid_Hydro_plant_Hydro)_:
-0.48167657996125474 cap_pro_new(2019_Mid_Hydro_plant)
+1 e_pro_in(3501_2019_Mid_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3501_2019_Mid_Photovoltaics_Solar)_:
+1 e_pro_in(3501_2019_Mid_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3501_2019_Mid_Wind_park_Wind)_:
-0.090060233212249874 cap_pro_new(2019_Mid_Wind_park)
+1 e_pro_in(3501_2019_Mid_Wind_park_Wind)
= 0

c_e_def_intermittent_supply(3501_2019_North_Hydro_plant_Hydro)_:
-0.29738731760205944 cap_pro_new(2019_North_Hydro_plant)
+1 e_pro_in(3501_2019_North_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3501_2019_North_Photovoltaics_Solar)_:
-0.0056646116440771752 cap_pro_new(2019_North_Photovoltaics)
+1 e_pro_in(3501_2019_North_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3501_2019_North_Wind_park_Wind)_:
-0.25987159681913813 cap_pro_new(2019_North_Wind_park)
+1 e_pro_in(3501_2019_North_Wind_park_Wind)
= 0

c_e_def_intermittent_supply(3501_2019_South_Hydro_plant_Hydro)_:
-0.19649698417268047 cap_pro_new(2019_South_Hydro_plant)
+1 e_pro_in(3501_2019_South_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3501_2019_South_Photovoltaics_Solar)_:
+1 e_pro_in(3501_2019_South_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3501_2019_South_Wind_park_Wind)_:
-0.24106728113249681 cap_pro_new(2019_South_Wind_park)
+1 e_pro_in(3501_2019_South_Wind_park_Wind)
= 0

c_e_def_intermittent_supply(3502_2019_Mid_Hydro_plant_Hydro)_:
-0.48176615967126901 cap_pro_new(2019_Mid_Hydro_plant)
+1 e_pro_in(3502_2019_Mid_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3502_2019_Mid_Photovoltaics_Solar)_:
+1 e_pro_in(3502_2019_Mid_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3502_2019_Mid_Wind_park_Wind)_:
-0.10649877151115915 cap_pro_new(2019_Mid_Wind_park)
+1 e_pro_in(3502_2019_Mid_Wind_park_Wind)
= 0

c_e_def_intermittent_supply(3502_2019_North_Hydro_plant_Hydro)_:
-0.29739413789240066 cap_pro_new(2019_North_Hydro_plant)
+1 e_pro_in(3502_2019_North_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3502_2019_North_Photovoltaics_Solar)_:
-0.00049257492557192831 cap_pro_new(2019_North_Photovoltaics)
+1 e_pro_in(3502_2019_North_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3502_2019_North_Wind_park_Wind)_:
-0.25555559605069561 cap_pro_new(2019_North_Wind_park)
+1 e_pro_in(3502_2019_North_Wind_park_Wind)
= 0

c_e_def_intermittent_supply(3502_2019_South_Hydro_plant_Hydro)_:
-0.19646996772984046 cap_pro_new(2019_South_Hydro_plant)
+1 e_pro_in(3502_2019_South_Hydro_plant_Hydro)
= 0

c_e_def_intermittent_supply(3502_2019_South_Photovoltaics_Solar)_:
+1 e_pro_in(3502_2019_South_Photovoltaics_Solar)
= 0

c_e_def_intermittent_supply(3502_2019_South_Wind_park_Wind)_:
-0.22412917822503531 cap_pro_new(2019_South_Wind_park)
+1 e_pro_in(3502_2019_South_Wind_park_Wind)
= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Biomass_plant)_:
-1 cap_pro_new(2019_Mid_Biomass_plant)
+1 tau_pro(3501_2019_Mid_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Gas_plant)_:
-1 cap_pro_new(2019_Mid_Gas_plant)
+1 tau_pro(3501_2019_Mid_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Hydro_plant)_:
-1 cap_pro_new(2019_Mid_Hydro_plant)
+1 tau_pro(3501_2019_Mid_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Lignite_plant)_:
-1 cap_pro_new(2019_Mid_Lignite_plant)
+1 tau_pro(3501_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Photovoltaics)_:
-1 cap_pro_new(2019_Mid_Photovoltaics)
+1 tau_pro(3501_2019_Mid_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Slack_powerplant)_:
-1 cap_pro_new(2019_Mid_Slack_powerplant)
+1 tau_pro(3501_2019_Mid_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3501_2019_Mid_Wind_park)_:
-1 cap_pro_new(2019_Mid_Wind_park)
+1 tau_pro(3501_2019_Mid_Wind_park)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Biomass_plant)_:
-1 cap_pro_new(2019_North_Biomass_plant)
+1 tau_pro(3501_2019_North_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Coal_plant)_:
-1 cap_pro_new(2019_North_Coal_plant)
+1 tau_pro(3501_2019_North_Coal_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Feed_in)_:
-1 cap_pro_new(2019_North_Feed_in)
+1 tau_pro(3501_2019_North_Feed_in)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Gas_plant)_:
-1 cap_pro_new(2019_North_Gas_plant)
+1 tau_pro(3501_2019_North_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Hydro_plant)_:
-1 cap_pro_new(2019_North_Hydro_plant)
+1 tau_pro(3501_2019_North_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Photovoltaics)_:
-1 cap_pro_new(2019_North_Photovoltaics)
+1 tau_pro(3501_2019_North_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Purchase)_:
-1 cap_pro_new(2019_North_Purchase)
+1 tau_pro(3501_2019_North_Purchase)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_North_Slack_powerplant)_:
-1 cap_pro_new(2019_North_Slack_powerplant)
+1 tau_pro(3501_2019_North_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3501_2019_North_Wind_park)_:
-1 cap_pro_new(2019_North_Wind_park)
+1 tau_pro(3501_2019_North_Wind_park)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Biomass_plant)_:
-1 cap_pro_new(2019_South_Biomass_plant)
+1 tau_pro(3501_2019_South_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Coal_plant)_:
-1 cap_pro_new(2019_South_Coal_plant)
+1 tau_pro(3501_2019_South_Coal_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Feed_in)_:
-1 cap_pro_new(2019_South_Feed_in)
+1 tau_pro(3501_2019_South_Feed_in)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Gas_plant)_:
-1 cap_pro_new(2019_South_Gas_plant)
+1 tau_pro(3501_2019_South_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Hydro_plant)_:
-1 cap_pro_new(2019_South_Hydro_plant)
+1 tau_pro(3501_2019_South_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Photovoltaics)_:
-1 cap_pro_new(2019_South_Photovoltaics)
+1 tau_pro(3501_2019_South_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Purchase)_:
-1 cap_pro_new(2019_South_Purchase)
+1 tau_pro(3501_2019_South_Purchase)
<= 0

c_u_res_process_throughput_by_capacity(3501_2019_South_Slack_powerplant)_:
-1 cap_pro_new(2019_South_Slack_powerplant)
+1 tau_pro(3501_2019_South_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3501_2019_South_Wind_park)_:
-1 cap_pro_new(2019_South_Wind_park)
+1 tau_pro(3501_2019_South_Wind_park)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Biomass_plant)_:
-1 cap_pro_new(2019_Mid_Biomass_plant)
+1 tau_pro(3502_2019_Mid_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Gas_plant)_:
-1 cap_pro_new(2019_Mid_Gas_plant)
+1 tau_pro(3502_2019_Mid_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Hydro_plant)_:
-1 cap_pro_new(2019_Mid_Hydro_plant)
+1 tau_pro(3502_2019_Mid_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Lignite_plant)_:
-1 cap_pro_new(2019_Mid_Lignite_plant)
+1 tau_pro(3502_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Photovoltaics)_:
-1 cap_pro_new(2019_Mid_Photovoltaics)
+1 tau_pro(3502_2019_Mid_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Slack_powerplant)_:
-1 cap_pro_new(2019_Mid_Slack_powerplant)
+1 tau_pro(3502_2019_Mid_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3502_2019_Mid_Wind_park)_:
-1 cap_pro_new(2019_Mid_Wind_park)
+1 tau_pro(3502_2019_Mid_Wind_park)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Biomass_plant)_:
-1 cap_pro_new(2019_North_Biomass_plant)
+1 tau_pro(3502_2019_North_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Coal_plant)_:
-1 cap_pro_new(2019_North_Coal_plant)
+1 tau_pro(3502_2019_North_Coal_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Feed_in)_:
-1 cap_pro_new(2019_North_Feed_in)
+1 tau_pro(3502_2019_North_Feed_in)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Gas_plant)_:
-1 cap_pro_new(2019_North_Gas_plant)
+1 tau_pro(3502_2019_North_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Hydro_plant)_:
-1 cap_pro_new(2019_North_Hydro_plant)
+1 tau_pro(3502_2019_North_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Photovoltaics)_:
-1 cap_pro_new(2019_North_Photovoltaics)
+1 tau_pro(3502_2019_North_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Purchase)_:
-1 cap_pro_new(2019_North_Purchase)
+1 tau_pro(3502_2019_North_Purchase)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_North_Slack_powerplant)_:
-1 cap_pro_new(2019_North_Slack_powerplant)
+1 tau_pro(3502_2019_North_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3502_2019_North_Wind_park)_:
-1 cap_pro_new(2019_North_Wind_park)
+1 tau_pro(3502_2019_North_Wind_park)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Biomass_plant)_:
-1 cap_pro_new(2019_South_Biomass_plant)
+1 tau_pro(3502_2019_South_Biomass_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Coal_plant)_:
-1 cap_pro_new(2019_South_Coal_plant)
+1 tau_pro(3502_2019_South_Coal_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Feed_in)_:
-1 cap_pro_new(2019_South_Feed_in)
+1 tau_pro(3502_2019_South_Feed_in)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Gas_plant)_:
-1 cap_pro_new(2019_South_Gas_plant)
+1 tau_pro(3502_2019_South_Gas_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Hydro_plant)_:
-1 cap_pro_new(2019_South_Hydro_plant)
+1 tau_pro(3502_2019_South_Hydro_plant)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Photovoltaics)_:
-1 cap_pro_new(2019_South_Photovoltaics)
+1 tau_pro(3502_2019_South_Photovoltaics)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Purchase)_:
-1 cap_pro_new(2019_South_Purchase)
+1 tau_pro(3502_2019_South_Purchase)
<= 0

c_u_res_process_throughput_by_capacity(3502_2019_South_Slack_powerplant)_:
-1 cap_pro_new(2019_South_Slack_powerplant)
+1 tau_pro(3502_2019_South_Slack_powerplant)
<= 999999

c_u_res_process_throughput_by_capacity(3502_2019_South_Wind_park)_:
-1 cap_pro_new(2019_South_Wind_park)
+1 tau_pro(3502_2019_South_Wind_park)
<= 0

c_u_res_process_maxgrad_lower(3501_2019_Mid_Lignite_plant)_:
-0.89999999999999991 cap_pro_new(2019_Mid_Lignite_plant)
+1 tau_pro(3500_2019_Mid_Lignite_plant)
-1 tau_pro(3501_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_maxgrad_lower(3501_2019_North_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_North_Coal_plant)
+1 tau_pro(3500_2019_North_Coal_plant)
-1 tau_pro(3501_2019_North_Coal_plant)
<= 0

c_u_res_process_maxgrad_lower(3501_2019_South_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_South_Coal_plant)
+1 tau_pro(3500_2019_South_Coal_plant)
-1 tau_pro(3501_2019_South_Coal_plant)
<= 0

c_u_res_process_maxgrad_lower(3502_2019_Mid_Lignite_plant)_:
-0.89999999999999991 cap_pro_new(2019_Mid_Lignite_plant)
+1 tau_pro(3501_2019_Mid_Lignite_plant)
-1 tau_pro(3502_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_maxgrad_lower(3502_2019_North_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_North_Coal_plant)
+1 tau_pro(3501_2019_North_Coal_plant)
-1 tau_pro(3502_2019_North_Coal_plant)
<= 0

c_u_res_process_maxgrad_lower(3502_2019_South_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_South_Coal_plant)
+1 tau_pro(3501_2019_South_Coal_plant)
-1 tau_pro(3502_2019_South_Coal_plant)
<= 0

c_u_res_process_maxgrad_upper(3501_2019_Mid_Lignite_plant)_:
-0.89999999999999991 cap_pro_new(2019_Mid_Lignite_plant)
-1 tau_pro(3500_2019_Mid_Lignite_plant)
+1 tau_pro(3501_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_maxgrad_upper(3501_2019_North_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_North_Coal_plant)
-1 tau_pro(3500_2019_North_Coal_plant)
+1 tau_pro(3501_2019_North_Coal_plant)
<= 0

c_u_res_process_maxgrad_upper(3501_2019_South_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_South_Coal_plant)
-1 tau_pro(3500_2019_South_Coal_plant)
+1 tau_pro(3501_2019_South_Coal_plant)
<= 0

c_u_res_process_maxgrad_upper(3502_2019_Mid_Lignite_plant)_:
-0.89999999999999991 cap_pro_new(2019_Mid_Lignite_plant)
-1 tau_pro(3501_2019_Mid_Lignite_plant)
+1 tau_pro(3502_2019_Mid_Lignite_plant)
<= 0

c_u_res_process_maxgrad_upper(3502_2019_North_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_North_Coal_plant)
-1 tau_pro(3501_2019_North_Coal_plant)
+1 tau_pro(3502_2019_North_Coal_plant)
<= 0

c_u_res_process_maxgrad_upper(3502_2019_South_Coal_plant)_:
-0.59999999999999998 cap_pro_new(2019_South_Coal_plant)
-1 tau_pro(3501_2019_South_Coal_plant)
+1 tau_pro(3502_2019_South_Coal_plant)
<= 0

r_l_res_process_capacity(2019_Mid_Biomass_plant)_:
+1 cap_pro_new(2019_Mid_Biomass_plant)
>= 0

r_u_res_process_capacity(2019_Mid_Biomass_plant)_:
+1 cap_pro_new(2019_Mid_Biomass_plant)
<= 5000

r_l_res_process_capacity(2019_Mid_Gas_plant)_:
+1 cap_pro_new(2019_Mid_Gas_plant)
>= 0

r_u_res_process_capacity(2019_Mid_Gas_plant)_:
+1 cap_pro_new(2019_Mid_Gas_plant)
<= 80000

r_l_res_process_capacity(2019_Mid_Hydro_plant)_:
+1 cap_pro_new(2019_Mid_Hydro_plant)
>= 0

r_u_res_process_capacity(2019_Mid_Hydro_plant)_:
+1 cap_pro_new(2019_Mid_Hydro_plant)
<= 1400

r_l_res_process_capacity(2019_Mid_Lignite_plant)_:
+1 cap_pro_new(2019_Mid_Lignite_plant)
>= 0

r_u_res_process_capacity(2019_Mid_Lignite_plant)_:
+1 cap_pro_new(2019_Mid_Lignite_plant)
<= 60000

r_l_res_process_capacity(2019_Mid_Photovoltaics)_:
+1 cap_pro_new(2019_Mid_Photovoltaics)
>= 15000

r_u_res_process_capacity(2019_Mid_Photovoltaics)_:
+1 cap_pro_new(2019_Mid_Photovoltaics)
<= 160000

r_l_res_process_capacity(2019_Mid_Slack_powerplant)_:
+1 cap_pro_new(2019_Mid_Slack_powerplant)
>= 0

r_u_res_process_capacity(2019_Mid_Slack_powerplant)_:
+1 cap_pro_new(2019_Mid_Slack_powerplant)
<= 0

r_l_res_process_capacity(2019_Mid_Wind_park)_:
+1 cap_pro_new(2019_Mid_Wind_park)
>= 0

r_u_res_process_capacity(2019_Mid_Wind_park)_:
+1 cap_pro_new(2019_Mid_Wind_park)
<= 13000

r_l_res_process_capacity(2019_North_Biomass_plant)_:
+1 cap_pro_new(2019_North_Biomass_plant)
>= 0

r_u_res_process_capacity(2019_North_Biomass_plant)_:
+1 cap_pro_new(2019_North_Biomass_plant)
<= 6000

r_l_res_process_capacity(2019_North_Coal_plant)_:
+1 cap_pro_new(2019_North_Coal_plant)
>= 0

r_u_res_process_capacity(2019_North_Coal_plant)_:
+1 cap_pro_new(2019_North_Coal_plant)
<= 100000

r_l_res_process_capacity(2019_North_Feed_in)_:
+1 cap_pro_new(2019_North_Feed_in)
>= 0

r_u_res_process_capacity(2019_North_Feed_in)_:
+1 cap_pro_new(2019_North_Feed_in)
<= 2500

r_l_res_process_capacity(2019_North_Gas_plant)_:
+1 cap_pro_new(2019_North_Gas_plant)
>= 0

r_u_res_process_capacity(2019_North_Gas_plant)_:
+1 cap_pro_new(2019_North_Gas_plant)
<= 100000

r_l_res_process_capacity(2019_North_Hydro_plant)_:
+1 cap_pro_new(2019_North_Hydro_plant)
>= 0

r_u_res_process_capacity(2019_North_Hydro_plant)_:
+1 cap_pro_new(2019_North_Hydro_plant)
<= 20000

r_l_res_process_capacity(2019_North_Photovoltaics)_:
+1 cap_pro_new(2019_North_Photovoltaics)
>= 0

r_u_res_process_capacity(2019_North_Photovoltaics)_:
+1 cap_pro_new(2019_North_Photovoltaics)
<= 3000

r_l_res_process_capacity(2019_North_Purchase)_:
+1 cap_pro_new(2019_North_Purchase)
>= 0

r_u_res_process_capacity(2019_North_Purchase)_:
+1 cap_pro_new(2019_North_Purchase)
<= 2500

r_l_res_process_capacity(2019_North_Slack_powerplant)_:
+1 cap_pro_new(2019_North_Slack_powerplant)
>= 0

r_u_res_process_capacity(2019_North_Slack_powerplant)_:
+1 cap_pro_new(2019_North_Slack_powerplant)
<= 0

r_l_res_process_capacity(2019_North_Wind_park)_:
+1 cap_pro_new(2019_North_Wind_park)
>= 0

r_u_res_process_capacity(2019_North_Wind_park)_:
+1 cap_pro_new(2019_North_Wind_park)
<= 60000

r_l_res_process_capacity(2019_South_Biomass_plant)_:
+1 cap_pro_new(2019_South_Biomass_plant)
>= 0

r_u_res_process_capacity(2019_South_Biomass_plant)_:
+1 cap_pro_new(2019_South_Biomass_plant)
<= 2000

r_l_res_process_capacity(2019_South_Coal_plant)_:
+1 cap_pro_new(2019_South_Coal_plant)
>= 0

r_u_res_process_capacity(2019_South_Coal_plant)_:
+1 cap_pro_new(2019_South_Coal_plant)
<= 100000

r_l_res_process_capacity(2019_South_Feed_in)_:
+1 cap_pro_new(2019_South_Feed_in)
>= 0

r_u_res_process_capacity(2019_South_Feed_in)_:
+1 cap_pro_new(2019_South_Feed_in)
<= 1500

r_l_res_process_capacity(2019_South_Gas_plant)_:
+1 cap_pro_new(2019_South_Gas_plant)
>= 0

r_u_res_process_capacity(2019_South_Gas_plant)_:
+1 cap_pro_new(2019_South_Gas_plant)
<= 100000

r_l_res_process_capacity(2019_South_Hydro_plant)_:
+1 cap_pro_new(2019_South_Hydro_plant)
>= 0

r_u_res_process_capacity(2019_South_Hydro_plant)_:
+1 cap_pro_new(2019_South_Hydro_plant)
<= 0

r_l_res_process_capacity(2019_South_Photovoltaics)_:
+1 cap_pro_new(2019_South_Photovoltaics)
>= 20000

r_u_res_process_capacity(2019_South_Photovoltaics)_:
+1 cap_pro_new(2019_South_Photovoltaics)
<= 600000

r_l_res_process_capacity(2019_South_Purchase)_:
+1 cap_pro_new(2019_South_Purchase)
>= 0

r_u_res_process_capacity(2019_South_Purchase)_:
+1 cap_pro_new(2019_South_Purchase)
<= 1500

r_l_res_process_capacity(2019_South_Slack_powerplant)_:
+1 cap_pro_new(2019_South_Slack_powerplant)
>= 0

r_u_res_process_capacity(2019_South_Slack_powerplant)_:
+1 cap_pro_new(2019_South_Slack_powerplant)
<= 0

r_l_res_process_capacity(2019_South_Wind_park)_:
+1 cap_pro_new(2019_South_Wind_park)
>= 0

r_u_res_process_capacity(2019_South_Wind_park)_:
+1 cap_pro_new(2019_South_Wind_park)
<= 200000

c_u_res_area(2019_Mid)_:
+14000 cap_pro_new(2019_Mid_Photovoltaics)
<= 280000000

c_u_res_area(2019_South)_:
+14000 cap_pro_new(2019_South_Photovoltaics)
<= 5000000000

c_u_res_throughput_by_capacity_min(3501_2019_Mid_Gas_plant)_:
+0.25 cap_pro_new(2019_Mid_Gas_plant)
-1 tau_pro(3501_2019_Mid_Gas_plant)
<= 0

c_u_res_throughput_by_capacity_min(3501_2019_Mid_Lignite_plant)_:
+0.65000000000000002 cap_pro_new(2019_Mid_Lignite_plant)
-1 tau_pro(3501_2019_Mid_Lignite_plant)
<= 0

c_u_res_throughput_by_capacity_min(3501_2019_North_Coal_plant)_:
+0.5 cap_pro_new(2019_North_Coal_plant)
-1 tau_pro(3501_2019_North_Coal_plant)
<= 0

c_u_res_throughput_by_capacity_min(3501_2019_North_Gas_plant)_:
+0.25 cap_pro_new(2019_North_Gas_plant)
-1 tau_pro(3501_2019_North_Gas_plant)
<= 0

c_u_res_throughput_by_capacity_min(3501_2019_South_Coal_plant)_:
+0.5 cap_pro_new(2019_South_Coal_plant)
-1 tau_pro(3501_2019_South_Coal_plant)
<= 0

c_u_res_throughput_by_capacity_min(3501_2019_South_Gas_plant)_:
+0.25 cap_pro_new(2019_South_Gas_plant)
-1 tau_pro(3501_2019_South_Gas_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_Mid_Gas_plant)_:
+0.25 cap_pro_new(2019_Mid_Gas_plant)
-1 tau_pro(3502_2019_Mid_Gas_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_Mid_Lignite_plant)_:
+0.65000000000000002 cap_pro_new(2019_Mid_Lignite_plant)
-1 tau_pro(3502_2019_Mid_Lignite_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_North_Coal_plant)_:
+0.5 cap_pro_new(2019_North_Coal_plant)
-1 tau_pro(3502_2019_North_Coal_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_North_Gas_plant)_:
+0.25 cap_pro_new(2019_North_Gas_plant)
-1 tau_pro(3502_2019_North_Gas_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_South_Coal_plant)_:
+0.5 cap_pro_new(2019_South_Coal_plant)
-1 tau_pro(3502_2019_South_Coal_plant)
<= 0

c_u_res_throughput_by_capacity_min(3502_2019_South_Gas_plant)_:
+0.25 cap_pro_new(2019_South_Gas_plant)
-1 tau_pro(3502_2019_South_Gas_plant)
<= 0

c_e_def_partial_process_input(3501_2019_Mid_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_Mid_Gas_plant)
+1 e_pro_in(3501_2019_Mid_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3501_2019_Mid_Gas_plant)
= 0

c_e_def_partial_process_input(3501_2019_Mid_Lignite_plant_Lignite)_:
-1.8571428571428574 cap_pro_new(2019_Mid_Lignite_plant)
+1 e_pro_in(3501_2019_Mid_Lignite_plant_Lignite)
+0.85714285714285732 tau_pro(3501_2019_Mid_Lignite_plant)
= 0

c_e_def_partial_process_input(3501_2019_North_Coal_plant_Coal)_:
-0.39999999999999991 cap_pro_new(2019_North_Coal_plant)
+1 e_pro_in(3501_2019_North_Coal_plant_Coal)
-0.60000000000000009 tau_pro(3501_2019_North_Coal_plant)
= 0

c_e_def_partial_process_input(3501_2019_North_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_North_Gas_plant)
+1 e_pro_in(3501_2019_North_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3501_2019_North_Gas_plant)
= 0

c_e_def_partial_process_input(3501_2019_South_Coal_plant_Coal)_:
-0.39999999999999991 cap_pro_new(2019_South_Coal_plant)
+1 e_pro_in(3501_2019_South_Coal_plant_Coal)
-0.60000000000000009 tau_pro(3501_2019_South_Coal_plant)
= 0

c_e_def_partial_process_input(3501_2019_South_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_South_Gas_plant)
+1 e_pro_in(3501_2019_South_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3501_2019_South_Gas_plant)
= 0

c_e_def_partial_process_input(3502_2019_Mid_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_Mid_Gas_plant)
+1 e_pro_in(3502_2019_Mid_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3502_2019_Mid_Gas_plant)
= 0

c_e_def_partial_process_input(3502_2019_Mid_Lignite_plant_Lignite)_:
-1.8571428571428574 cap_pro_new(2019_Mid_Lignite_plant)
+1 e_pro_in(3502_2019_Mid_Lignite_plant_Lignite)
+0.85714285714285732 tau_pro(3502_2019_Mid_Lignite_plant)
= 0

c_e_def_partial_process_input(3502_2019_North_Coal_plant_Coal)_:
-0.39999999999999991 cap_pro_new(2019_North_Coal_plant)
+1 e_pro_in(3502_2019_North_Coal_plant_Coal)
-0.60000000000000009 tau_pro(3502_2019_North_Coal_plant)
= 0

c_e_def_partial_process_input(3502_2019_North_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_North_Gas_plant)
+1 e_pro_in(3502_2019_North_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3502_2019_North_Gas_plant)
= 0

c_e_def_partial_process_input(3502_2019_South_Coal_plant_Coal)_:
-0.39999999999999991 cap_pro_new(2019_South_Coal_plant)
+1 e_pro_in(3502_2019_South_Coal_plant_Coal)
-0.60000000000000009 tau_pro(3502_2019_South_Coal_plant)
= 0

c_e_def_partial_process_input(3502_2019_South_Gas_plant_Gas)_:
-0.066666666666666652 cap_pro_new(2019_South_Gas_plant)
+1 e_pro_in(3502_2019_South_Gas_plant_Gas)
-0.93333333333333324 tau_pro(3502_2019_South_Gas_plant)
= 0

c_e_def_partial_process_output(3501_2019_Mid_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_Mid_Gas_plant)
+1 e_pro_out(3501_2019_Mid_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3501_2019_Mid_Gas_plant)
= 0

c_e_def_partial_process_output(3501_2019_Mid_Lignite_plant_CO2)_:
-0.74285714285714288 cap_pro_new(2019_Mid_Lignite_plant)
+1 e_pro_out(3501_2019_Mid_Lignite_plant_CO2)
+0.34285714285714286 tau_pro(3501_2019_Mid_Lignite_plant)
= 0

c_e_def_partial_process_output(3501_2019_North_Coal_plant_CO2)_:
-0.12 cap_pro_new(2019_North_Coal_plant)
+1 e_pro_out(3501_2019_North_Coal_plant_CO2)
-0.17999999999999999 tau_pro(3501_2019_North_Coal_plant)
= 0

c_e_def_partial_process_output(3501_2019_North_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_North_Gas_plant)
+1 e_pro_out(3501_2019_North_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3501_2019_North_Gas_plant)
= 0

c_e_def_partial_process_output(3501_2019_South_Coal_plant_CO2)_:
-0.12 cap_pro_new(2019_South_Coal_plant)
+1 e_pro_out(3501_2019_South_Coal_plant_CO2)
-0.17999999999999999 tau_pro(3501_2019_South_Coal_plant)
= 0

c_e_def_partial_process_output(3501_2019_South_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_South_Gas_plant)
+1 e_pro_out(3501_2019_South_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3501_2019_South_Gas_plant)
= 0

c_e_def_partial_process_output(3502_2019_Mid_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_Mid_Gas_plant)
+1 e_pro_out(3502_2019_Mid_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3502_2019_Mid_Gas_plant)
= 0

c_e_def_partial_process_output(3502_2019_Mid_Lignite_plant_CO2)_:
-0.74285714285714288 cap_pro_new(2019_Mid_Lignite_plant)
+1 e_pro_out(3502_2019_Mid_Lignite_plant_CO2)
+0.34285714285714286 tau_pro(3502_2019_Mid_Lignite_plant)
= 0

c_e_def_partial_process_output(3502_2019_North_Coal_plant_CO2)_:
-0.12 cap_pro_new(2019_North_Coal_plant)
+1 e_pro_out(3502_2019_North_Coal_plant_CO2)
-0.17999999999999999 tau_pro(3502_2019_North_Coal_plant)
= 0

c_e_def_partial_process_output(3502_2019_North_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_North_Gas_plant)
+1 e_pro_out(3502_2019_North_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3502_2019_North_Gas_plant)
= 0

c_e_def_partial_process_output(3502_2019_South_Coal_plant_CO2)_:
-0.12 cap_pro_new(2019_South_Coal_plant)
+1 e_pro_out(3502_2019_South_Coal_plant_CO2)
-0.17999999999999999 tau_pro(3502_2019_South_Coal_plant)
= 0

c_e_def_partial_process_output(3502_2019_South_Gas_plant_CO2)_:
-0.013333333333333327 cap_pro_new(2019_South_Gas_plant)
+1 e_pro_out(3502_2019_South_Gas_plant_CO2)
-0.18666666666666668 tau_pro(3502_2019_South_Gas_plant)
= 0

c_e_def_costs(Environmental)_:
+1 costs(Environmental)
= 0

c_e_def_costs(Fixed)_:
-28000 cap_pro_new(2019_Mid_Biomass_plant)
-6000 cap_pro_new(2019_Mid_Gas_plant)
-20000 cap_pro_new(2019_Mid_Hydro_plant)
-18000 cap_pro_new(2019_Mid_Lignite_plant)
-12000 cap_pro_new(2019_Mid_Photovoltaics)
-30000 cap_pro_new(2019_Mid_Wind_park)
-28000 cap_pro_new(2019_North_Biomass_plant)
-18000 cap_pro_new(2019_North_Coal_plant)
-6000 cap_pro_new(2019_North_Gas_plant)
-20000 cap_pro_new(2019_North_Hydro_plant)
-12000 cap_pro_new(2019_North_Photovoltaics)
-80 cap_pro_new(2019_North_Purchase)
-30000 cap_pro_new(2019_North_Wind_park)
-28000 cap_pro_new(2019_South_Biomass_plant)
-18000 cap_pro_new(2019_South_Coal_plant)
-6000 cap_pro_new(2019_South_Gas_plant)
-20000 cap_pro_new(2019_South_Hydro_plant)
-12000 cap_pro_new(2019_South_Photovoltaics)
-80 cap_pro_new(2019_South_Purchase)
-30000 cap_pro_new(2019_South_Wind_park)
-0.32700000000000001 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
-0.32700000000000001 cap_sto_c_new(2019_North_Hydrogen_Elec)
-0.32700000000000001 cap_sto_c_new(2019_South_Hydrogen_Elec)
-20000 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
-20000 cap_sto_p_new(2019_North_Pump_storage_Elec)
-20000 cap_sto_p_new(2019_South_Pump_storage_Elec)
-16500 cap_tra_new(2019_Mid_South_hvac_Elec)
-33000 cap_tra_new(2019_North_Mid_hvac_Elec)
-30000 cap_tra_new(2019_North_South_hvac_Elec)
-16500 cap_tra_new(2019_South_Mid_hvac_Elec)
-30000 cap_tra_new(2019_South_North_hvac_Elec)
+1 costs(Fixed)
= 10950000

c_e_def_costs(Fuel)_:
+1 costs(Fuel)
-17520 e_co_stock(3501_2019_Mid_Biomass_Stock)
-20440 e_co_stock(3501_2019_Mid_Coal_Stock)
-78840 e_co_stock(3501_2019_Mid_Gas_Stock)
-11680 e_co_stock(3501_2019_Mid_Lignite_Stock)
-2917080 e_co_stock(3501_2019_Mid_Slack_Stock)
-17520 e_co_stock(3501_2019_North_Biomass_Stock)
-20440 e_co_stock(3501_2019_North_Coal_Stock)
-78840 e_co_stock(3501_2019_North_Gas_Stock)
-11680 e_co_stock(3501_2019_North_Lignite_Stock)
-2917080 e_co_stock(3501_2019_North_Slack_Stock)
-17520 e_co_stock(3501_2019_South_Biomass_Stock)
-20440 e_co_stock(3501_2019_South_Coal_Stock)
-78840 e_co_stock(3501_2019_South_Gas_Stock)
-11680 e_co_stock(3501_2019_South_Lignite_Stock)
-2917080 e_co_stock(3501_2019_South_Slack_Stock)
-17520 e_co_stock(3502_2019_Mid_Biomass_Stock)
-20440 e_co_stock(3502_2019_Mid_Coal_Stock)
-78840 e_co_stock(3502_2019_Mid_Gas_Stock)
-11680 e_co_stock(3502_2019_Mid_Lignite_Stock)
-2917080 e_co_stock(3502_2019_Mid_Slack_Stock)
-17520 e_co_stock(3502_2019_North_Biomass_Stock)
-20440 e_co_stock(3502_2019_North_Coal_Stock)
-78840 e_co_stock(3502_2019_North_Gas_Stock)
-11680 e_co_stock(3502_2019_North_Lignite_Stock)
-2917080 e_co_stock(3502_2019_North_Slack_Stock)
-17520 e_co_stock(3502_2019_South_Biomass_Stock)
-20440 e_co_stock(3502_2019_South_Coal_Stock)
-78840 e_co_stock(3502_2019_South_Gas_Stock)
-11680 e_co_stock(3502_2019_South_Lignite_Stock)
-2917080 e_co_stock(3502_2019_South_Slack_Stock)
= 0

c_e_def_costs(Invest)_:
-75084.202568082401 cap_pro_new(2019_Mid_Biomass_plant)
-36263.88158000003 cap_pro_new(2019_Mid_Gas_plant)
-115935.75926337227 cap_pro_new(2019_Mid_Hydro_plant)
-45005.483324166191 cap_pro_new(2019_Mid_Lignite_plant)
-51486.310332399356 cap_pro_new(2019_Mid_Photovoltaics)
-128715.77583099841 cap_pro_new(2019_Mid_Wind_park)
-75084.202568082401 cap_pro_new(2019_North_Biomass_plant)
-45005.483324166191 cap_pro_new(2019_North_Coal_plant)
-36263.88158000003 cap_pro_new(2019_North_Gas_plant)
-115935.75926337227 cap_pro_new(2019_North_Hydro_plant)
-51486.310332399356 cap_pro_new(2019_North_Photovoltaics)
-128715.77583099841 cap_pro_new(2019_North_Wind_park)
-75084.202568082401 cap_pro_new(2019_South_Biomass_plant)
-45005.483324166191 cap_pro_new(2019_South_Coal_plant)
-36263.88158000003 cap_pro_new(2019_South_Gas_plant)
-115935.75926337227 cap_pro_new(2019_South_Hydro_plant)
-51486.310332399356 cap_pro_new(2019_South_Photovoltaics)
-128715.77583099841 cap_pro_new(2019_South_Wind_park)
-0.47388741598903417 cap_sto_c_new(2019_Mid_Hydrogen_Elec)
-0.47388741598903417 cap_sto_c_new(2019_North_Hydrogen_Elec)
-0.47388741598903417 cap_sto_c_new(2019_South_Hydrogen_Elec)
-3043.3136806635221 cap_sto_p_new(2019_Mid_Hydrogen_Elec)
-7245.9849539607667 cap_sto_p_new(2019_Mid_Pump_storage_Elec)
-3043.3136806635221 cap_sto_p_new(2019_North_Hydrogen_Elec)
-7245.9849539607667 cap_sto_p_new(2019_North_Pump_storage_Elec)
-3043.3136806635221 cap_sto_p_new(2019_South_Hydrogen_Elec)
-7245.9849539607667 cap_sto_p_new(2019_South_Pump_storage_Elec)
-1237.6507914145702 cap_tra_new(2019_Mid_South_hvac_Elec)
-2475.3015828291404 cap_tra_new(2019_North_Mid_hvac_Elec)
-2250.2741662083095 cap_tra_new(2019_North_South_hvac_Elec)
-1237.6507914145702 cap_tra_new(2019_South_Mid_hvac_Elec)
-2250.2741662083095 cap_tra_new(2019_South_North_hvac_Elec)
+1 costs(Invest)
= 0

c_e_def_costs(Purchase)_:
+1 costs(Purchase)
-438 e_co_buy(3501_2019_North_Elec_buy_Buy)
-350.39999999999998 e_co_buy(3501_2019_South_Elec_buy_Buy)
-620.5 e_co_buy(3502_2019_North_Elec_buy_Buy)
-496.39999999999998 e_co_buy(3502_2019_South_Elec_buy_Buy)
= 0

c_e_def_costs(Revenue)_:
+1 costs(Revenue)
+23.071649999999995 e_co_sell(3501_2019_North_Elec_sell_Sell)
+276.85979999999995 e_co_sell(3501_2019_South_Elec_sell_Sell)
+27.253163000000001 e_co_sell(3502_2019_North_Elec_sell_Sell)
+327.03795600000001 e_co_sell(3502_2019_South_Elec_sell_Sell)
= 0

c_e_def_costs(Variable)_:
-2920 abs_e_tra_dc(3501_2019_North_Mid_hvac_Elec)
-2920 abs_e_tra_dc(3502_2019_North_Mid_hvac_Elec)
+1 costs(Variable)
-58.399999999999999 e_sto_in(3501_2019_Mid_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3501_2019_Mid_Pump_storage_Elec)
-58.399999999999999 e_sto_in(3501_2019_North_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3501_2019_North_Pump_storage_Elec)
-58.399999999999999 e_sto_in(3501_2019_South_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3501_2019_South_Pump_storage_Elec)
-58.399999999999999 e_sto_in(3502_2019_Mid_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3502_2019_Mid_Pump_storage_Elec)
-58.399999999999999 e_sto_in(3502_2019_North_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3502_2019_North_Pump_storage_Elec)
-58.399999999999999 e_sto_in(3502_2019_South_Hydrogen_Elec)
-58.399999999999999 e_sto_in(3502_2019_South_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3501_2019_Mid_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3501_2019_Mid_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3501_2019_North_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3501_2019_North_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3501_2019_South_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3501_2019_South_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3502_2019_Mid_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3502_2019_Mid_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3502_2019_North_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3502_2019_North_Pump_storage_Elec)
-58.399999999999999 e_sto_out(3502_2019_South_Hydrogen_Elec)
-58.399999999999999 e_sto_out(3502_2019_South_Pump_storage_Elec)
-2920 e_tra_in(3501_2019_Mid_South_hvac_Elec)
-2920 e_tra_in(3501_2019_North_South_hvac_Elec)
-2920 e_tra_in(3501_2019_South_Mid_hvac_Elec)
-2920 e_tra_in(3501_2019_South_North_hvac_Elec)
-2920 e_tra_in(3502_2019_Mid_South_hvac_Elec)
-2920 e_tra_in(3502_2019_North_South_hvac_Elec)
-2920 e_tra_in(3502_2019_South_Mid_hvac_Elec)
-2920 e_tra_in(3502_2019_South_North_hvac_Elec)
-4087.9999999999995 tau_pro(3501_2019_Mid_Biomass_plant)
-4730.4000000000005 tau_pro(3501_2019_Mid_Gas_plant)
-1752.0000000000002 tau_pro(3501_2019_Mid_Lignite_plant)
-292000 tau_pro(3501_2019_Mid_Slack_powerplant)
-4087.9999999999995 tau_pro(3501_2019_North_Biomass_plant)
-1752.0000000000002 tau_pro(3501_2019_North_Coal_plant)
-4730.4000000000005 tau_pro(3501_2019_North_Gas_plant)
-292000 tau_pro(3501_2019_North_Slack_powerplant)
-4087.9999999999995 tau_pro(3501_2019_South_Biomass_plant)
-1752.0000000000002 tau_pro(3501_2019_South_Coal_plant)
-4730.4000000000005 tau_pro(3501_2019_South_Gas_plant)
-2917080 tau_pro(3501_2019_South_Slack_powerplant)
-4087.9999999999995 tau_pro(3502_2019_Mid_Biomass_plant)
-4730.4000000000005 tau_pro(3502_2019_Mid_Gas_plant)
-1752.0000000000002 tau_pro(3502_2019_Mid_Lignite_plant)
-292000 tau_pro(3502_2019_Mid_Slack_powerplant)
-4087.9999999999995 tau_pro(3502_2019_North_Biomass_plant)
-1752.0000000000002 tau_pro(3502_2019_North_Coal_plant)
-4730.4000000000005 tau_pro(3502_2019_North_Gas_plant)
-292000 tau_pro(3502_2019_North_Slack_powerplant)
-4087.9999999999995 tau_pro(3502_2019_South_Biomass_plant)
-1752.0000000000002 tau_pro(3502_2019_South_Coal_plant)
-4730.4000000000005 tau_pro(3502_2019_South_Gas_plant)
-2917080 tau_pro(3502_2019_South_Slack_powerplant)
= 0

c_u_res_global_co2_limit(2019)_:
+2920 e_pro_out(3501_2019_Mid_Biomass_plant_CO2)
+2920 e_pro_out(3501_2019_Mid_Gas_plant_CO2)
+2920 e_pro_out(3501_2019_Mid_Lignite_plant_CO2)
+2920 e_pro_out(3501_2019_Mid_Slack_powerplant_CO2)
+2920 e_pro_out(3501_2019_North_Biomass_plant_CO2)
+2920 e_pro_out(3501_2019_North_Coal_plant_CO2)
+2920 e_pro_out(3501_2019_North_Gas_plant_CO2)
+2920 e_pro_out(3501_2019_North_Purchase_CO2)
+2920 e_pro_out(3501_2019_North_Slack_powerplant_CO2)
+2920 e_pro_out(3501_2019_South_Biomass_plant_CO2)
+2920 e_pro_out(3501_2019_South_Coal_plant_CO2)
+2920 e_pro_out(3501_2019_South_Gas_plant_CO2)
+2920 e_pro_out(3501_2019_South_Purchase_CO2)
+2920 e_pro_out(3501_2019_South_Slack_powerplant_CO2)
+2920 e_pro_out(3502_2019_Mid_Biomass_plant_CO2)
+2920 e_pro_out(3502_2019_Mid_Gas_plant_CO2)
+2920 e_pro_out(3502_2019_Mid_Lignite_plant_CO2)
+2920 e_pro_out(3502_2019_Mid_Slack_powerplant_CO2)
+2920 e_pro_out(3502_2019_North_Biomass_plant_CO2)
+2920 e_pro_out(3502_2019_North_Coal_plant_CO2)
+2920 e_pro_out(3502_2019_North_Gas_plant_CO2)
+2920 e_pro_out(3502_2019_North_Purchase_CO2)
+2920 e_pro_out(3502_2019_North_Slack_powerplant_CO2)
+2920 e_pro_out(3502_2019_South_Biomass_plant_CO2)
+2920 e_pro_out(3502_2019_South_Coal_plant_CO2)
+2920 e_pro_out(3502_2019_South_Gas_plant_CO2)
+2920 e_pro_out(3502_2019_South_Purchase_CO2)
+2920 e_pro_out(3502_2019_South_Slack_powerplant_CO2)
<= 150000000

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
    -inf <= costs(Environmental) <= +inf
    -inf <= costs(Fixed) <= +inf
    -inf <= costs(Fuel) <= +inf
    -inf <= costs(Invest) <= +inf
    -inf <= costs(Purchase) <= +inf
    -inf <= costs(Revenue) <= +inf
    -inf <= costs(Variable) <= +inf
   0 <= e_co_stock(3501_2019_Mid_Biomass_Stock) <= +inf
   0 <= e_co_stock(3501_2019_Mid_Coal_Stock) <= +inf
   0 <= e_co_stock(3501_2019_Mid_Gas_Stock) <= +inf
   0 <= e_co_stock(3501_2019_Mid_Lignite_Stock) <= +inf
   0 <= e_co_stock(3501_2019_Mid_Slack_Stock) <= +inf
   0 <= e_co_stock(3501_2019_North_Biomass_Stock) <= +inf
   0 <= e_co_stock(3501_2019_North_Coal_Stock) <= +inf
   0 <= e_co_stock(3501_2019_North_Gas_Stock) <= +inf
   0 <= e_co_stock(3501_2019_North_Lignite_Stock) <= +inf
   0 <= e_co_stock(3501_2019_North_Slack_Stock) <= +inf
   0 <= e_co_stock(3501_2019_South_Biomass_Stock) <= +inf
   0 <= e_co_stock(3501_2019_South_Coal_Stock) <= +inf
   0 <= e_co_stock(3501_2019_South_Gas_Stock) <= +inf
   0 <= e_co_stock(3501_2019_South_Lignite_Stock) <= +inf
   0 <= e_co_stock(3501_2019_South_Slack_Stock) <= +inf
   0 <= e_co_stock(3502_2019_Mid_Biomass_Stock) <= +inf
   0 <= e_co_stock(3502_2019_Mid_Coal_Stock) <= +inf
   0 <= e_co_stock(3502_2019_Mid_Gas_Stock) <= +inf
   0 <= e_co_stock(3502_2019_Mid_Lignite_Stock) <= +inf
   0 <= e_co_stock(3502_2019_Mid_Slack_Stock) <= +inf
   0 <= e_co_stock(3502_2019_North_Biomass_Stock) <= +inf
   0 <= e_co_stock(3502_2019_North_Coal_Stock) <= +inf
   0 <= e_co_stock(3502_2019_North_Gas_Stock) <= +inf
   0 <= e_co_stock(3502_2019_North_Lignite_Stock) <= +inf
   0 <= e_co_stock(3502_2019_North_Slack_Stock) <= +inf
   0 <= e_co_stock(3502_2019_South_Biomass_Stock) <= +inf
   0 <= e_co_stock(3502_2019_South_Coal_Stock) <= +inf
   0 <= e_co_stock(3502_2019_South_Gas_Stock) <= +inf
   0 <= e_co_stock(3502_2019_South_Lignite_Stock) <= +inf
   0 <= e_co_stock(3502_2019_South_Slack_Stock) <= +inf
   0 <= cap_pro_new(2019_Mid_Biomass_plant) <= +inf
   0 <= cap_pro_new(2019_Mid_Gas_plant) <= +inf
   0 <= cap_pro_new(2019_Mid_Hydro_plant) <= +inf
   0 <= cap_pro_new(2019_Mid_Lignite_plant) <= +inf
   0 <= cap_pro_new(2019_Mid_Photovoltaics) <= +inf
   0 <= cap_pro_new(2019_Mid_Slack_powerplant) <= +inf
   0 <= cap_pro_new(2019_Mid_Wind_park) <= +inf
   0 <= cap_pro_new(2019_North_Biomass_plant) <= +inf
   0 <= cap_pro_new(2019_North_Coal_plant) <= +inf
   0 <= cap_pro_new(2019_North_Feed_in) <= +inf
   0 <= cap_pro_new(2019_North_Gas_plant) <= +inf
   0 <= cap_pro_new(2019_North_Hydro_plant) <= +inf
   0 <= cap_pro_new(2019_North_Photovoltaics) <= +inf
   0 <= cap_pro_new(2019_North_Purchase) <= +inf
   0 <= cap_pro_new(2019_North_Slack_powerplant) <= +inf
   0 <= cap_pro_new(2019_North_Wind_park) <= +inf
   0 <= cap_pro_new(2019_South_Biomass_plant) <= +inf
   0 <= cap_pro_new(2019_South_Coal_plant) <= +inf
   0 <= cap_pro_new(2019_South_Feed_in) <= +inf
   0 <= cap_pro_new(2019_South_Gas_plant) <= +inf
   0 <= cap_pro_new(2019_South_Hydro_plant) <= +inf
   0 <= cap_pro_new(2019_South_Photovoltaics) <= +inf
   0 <= cap_pro_new(2019_South_Purchase) <= +inf
   0 <= cap_pro_new(2019_South_Slack_powerplant) <= +inf
   0 <= cap_pro_new(2019_South_Wind_park) <= +inf
   0 <= tau_pro(3500_2019_Mid_Lignite_plant) <= +inf
   0 <= tau_pro(3500_2019_North_Coal_plant) <= +inf
   0 <= tau_pro(3500_2019_South_Coal_plant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Biomass_plant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Gas_plant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Hydro_plant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Lignite_plant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Photovoltaics) <= +inf
   0 <= tau_pro(3501_2019_Mid_Slack_powerplant) <= +inf
   0 <= tau_pro(3501_2019_Mid_Wind_park) <= +inf
   0 <= tau_pro(3501_2019_North_Biomass_plant) <= +inf
   0 <= tau_pro(3501_2019_North_Coal_plant) <= +inf
   0 <= tau_pro(3501_2019_North_Feed_in) <= +inf
   0 <= tau_pro(3501_2019_North_Gas_plant) <= +inf
   0 <= tau_pro(3501_2019_North_Hydro_plant) <= +inf
   0 <= tau_pro(3501_2019_North_Photovoltaics) <= +inf
   0 <= tau_pro(3501_2019_North_Purchase) <= +inf
   0 <= tau_pro(3501_2019_North_Slack_powerplant) <= +inf
   0 <= tau_pro(3501_2019_North_Wind_park) <= +inf
   0 <= tau_pro(3501_2019_South_Biomass_plant) <= +inf
   0 <= tau_pro(3501_2019_South_Coal_plant) <= +inf
   0 <= tau_pro(3501_2019_South_Feed_in) <= +inf
   0 <= tau_pro(3501_2019_South_Gas_plant) <= +inf
   0 <= tau_pro(3501_2019_South_Hydro_plant) <= +inf
   0 <= tau_pro(3501_2019_South_Photovoltaics) <= +inf
   0 <= tau_pro(3501_2019_South_Purchase) <= +inf
   0 <= tau_pro(3501_2019_South_Slack_powerplant) <= +inf
   0 <= tau_pro(3501_2019_South_Wind_park) <= +inf
   0 <= tau_pro(3502_2019_Mid_Biomass_plant) <= +inf
   0 <= tau_pro(3502_2019_Mid_Gas_plant) <= +inf
   0 <= tau_pro(3502_2019_Mid_Hydro_plant) <= +inf
   0 <= tau_pro(3502_2019_Mid_Lignite_plant) <= +inf
   0 <= tau_pro(3502_2019_Mid_Photovoltaics) <= +inf
   0 <= tau_pro(3502_2019_Mid_Slack_powerplant) <= +inf
   0 <= tau_pro(3502_2019_Mid_Wind_park) <= +inf
   0 <= tau_pro(3502_2019_North_Biomass_plant) <= +inf
   0 <= tau_pro(3502_2019_North_Coal_plant) <= +inf
   0 <= tau_pro(3502_2019_North_Feed_in) <= +inf
   0 <= tau_pro(3502_2019_North_Gas_plant) <= +inf
   0 <= tau_pro(3502_2019_North_Hydro_plant) <= +inf
   0 <= tau_pro(3502_2019_North_Photovoltaics) <= +inf
   0 <= tau_pro(3502_2019_North_Purchase) <= +inf
   0 <= tau_pro(3502_2019_North_Slack_powerplant) <= +inf
   0 <= tau_pro(3502_2019_North_Wind_park) <= +inf
   0 <= tau_pro(3502_2019_South_Biomass_plant) <= +inf
   0 <= tau_pro(3502_2019_South_Coal_plant) <= +inf
   0 <= tau_pro(3502_2019_South_Feed_in) <= +inf
   0 <= tau_pro(3502_2019_South_Gas_plant) <= +inf
   0 <= tau_pro(3502_2019_South_Hydro_plant) <= +inf
   0 <= tau_pro(3502_2019_South_Photovoltaics) <= +inf
   0 <= tau_pro(3502_2019_South_Purchase) <= +inf
   0 <= tau_pro(3502_2019_South_Slack_powerplant) <= +inf
   0 <= tau_pro(3502_2019_South_Wind_park) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Lignite_plant_Lignite) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3501_2019_Mid_Wind_park_Wind) <= +inf
   0 <= e_pro_in(3501_2019_North_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3501_2019_North_Coal_plant_Coal) <= +inf
   0 <= e_pro_in(3501_2019_North_Feed_in_Elec) <= +inf
   0 <= e_pro_in(3501_2019_North_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3501_2019_North_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3501_2019_North_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3501_2019_North_Purchase_Elec_buy) <= +inf
   0 <= e_pro_in(3501_2019_North_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3501_2019_North_Wind_park_Wind) <= +inf
   0 <= e_pro_in(3501_2019_South_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3501_2019_South_Coal_plant_Coal) <= +inf
   0 <= e_pro_in(3501_2019_South_Feed_in_Elec) <= +inf
   0 <= e_pro_in(3501_2019_South_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3501_2019_South_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3501_2019_South_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3501_2019_South_Purchase_Elec_buy) <= +inf
   0 <= e_pro_in(3501_2019_South_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3501_2019_South_Wind_park_Wind) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Lignite_plant_Lignite) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3502_2019_Mid_Wind_park_Wind) <= +inf
   0 <= e_pro_in(3502_2019_North_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3502_2019_North_Coal_plant_Coal) <= +inf
   0 <= e_pro_in(3502_2019_North_Feed_in_Elec) <= +inf
   0 <= e_pro_in(3502_2019_North_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3502_2019_North_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3502_2019_North_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3502_2019_North_Purchase_Elec_buy) <= +inf
   0 <= e_pro_in(3502_2019_North_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3502_2019_North_Wind_park_Wind) <= +inf
   0 <= e_pro_in(3502_2019_South_Biomass_plant_Biomass) <= +inf
   0 <= e_pro_in(3502_2019_South_Coal_plant_Coal) <= +inf
   0 <= e_pro_in(3502_2019_South_Feed_in_Elec) <= +inf
   0 <= e_pro_in(3502_2019_South_Gas_plant_Gas) <= +inf
   0 <= e_pro_in(3502_2019_South_Hydro_plant_Hydro) <= +inf
   0 <= e_pro_in(3502_2019_South_Photovoltaics_Solar) <= +inf
   0 <= e_pro_in(3502_2019_South_Purchase_Elec_buy) <= +inf
   0 <= e_pro_in(3502_2019_South_Slack_powerplant_Slack) <= +inf
   0 <= e_pro_in(3502_2019_South_Wind_park_Wind) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Lignite_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Lignite_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_Mid_Wind_park_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_North_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Coal_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_North_Coal_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Feed_in_Elec_sell) <= +inf
   0 <= e_pro_out(3501_2019_North_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_North_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Purchase_CO2) <= +inf
   0 <= e_pro_out(3501_2019_North_Purchase_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_North_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_North_Wind_park_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_South_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Coal_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_South_Coal_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Feed_in_Elec_sell) <= +inf
   0 <= e_pro_out(3501_2019_South_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_South_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Purchase_CO2) <= +inf
   0 <= e_pro_out(3501_2019_South_Purchase_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3501_2019_South_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3501_2019_South_Wind_park_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Lignite_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Lignite_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_Mid_Wind_park_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_North_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Coal_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_North_Coal_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Feed_in_Elec_sell) <= +inf
   0 <= e_pro_out(3502_2019_North_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_North_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Purchase_CO2) <= +inf
   0 <= e_pro_out(3502_2019_North_Purchase_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_North_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_North_Wind_park_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Biomass_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_South_Biomass_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Coal_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_South_Coal_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Feed_in_Elec_sell) <= +inf
   0 <= e_pro_out(3502_2019_South_Gas_plant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_South_Gas_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Hydro_plant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Photovoltaics_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Purchase_CO2) <= +inf
   0 <= e_pro_out(3502_2019_South_Purchase_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Slack_powerplant_CO2) <= +inf
   0 <= e_pro_out(3502_2019_South_Slack_powerplant_Elec) <= +inf
   0 <= e_pro_out(3502_2019_South_Wind_park_Elec) <= +inf
   0 <= cap_tra_new(2019_Mid_South_hvac_Elec) <= +inf
   0 <= cap_tra_new(2019_North_Mid_hvac_Elec) <= +inf
   0 <= cap_tra_new(2019_North_South_hvac_Elec) <= +inf
   0 <= cap_tra_new(2019_South_Mid_hvac_Elec) <= +inf
   0 <= cap_tra_new(2019_South_North_hvac_Elec) <= +inf
   0 <= abs_e_tra_dc(3501_2019_North_Mid_hvac_Elec) <= +inf
   0 <= abs_e_tra_dc(3502_2019_North_Mid_hvac_Elec) <= +inf
   0 <= e_tra_in(3501_2019_Mid_South_hvac_Elec) <= +inf
    -inf <= e_tra_in(3501_2019_North_Mid_hvac_Elec) <= +inf
   0 <= e_tra_in(3501_2019_North_South_hvac_Elec) <= +inf
   0 <= e_tra_in(3501_2019_South_Mid_hvac_Elec) <= +inf
   0 <= e_tra_in(3501_2019_South_North_hvac_Elec) <= +inf
   0 <= e_tra_in(3502_2019_Mid_South_hvac_Elec) <= +inf
    -inf <= e_tra_in(3502_2019_North_Mid_hvac_Elec) <= +inf
   0 <= e_tra_in(3502_2019_North_South_hvac_Elec) <= +inf
   0 <= e_tra_in(3502_2019_South_Mid_hvac_Elec) <= +inf
   0 <= e_tra_in(3502_2019_South_North_hvac_Elec) <= +inf
   0 <= e_tra_out(3501_2019_Mid_South_hvac_Elec) <= +inf
    -inf <= e_tra_out(3501_2019_North_Mid_hvac_Elec) <= +inf
   0 <= e_tra_out(3501_2019_North_South_hvac_Elec) <= +inf
   0 <= e_tra_out(3501_2019_South_Mid_hvac_Elec) <= +inf
   0 <= e_tra_out(3501_2019_South_North_hvac_Elec) <= +inf
   0 <= e_tra_out(3502_2019_Mid_South_hvac_Elec) <= +inf
    -inf <= e_tra_out(3502_2019_North_Mid_hvac_Elec) <= +inf
   0 <= e_tra_out(3502_2019_North_South_hvac_Elec) <= +inf
   0 <= e_tra_out(3502_2019_South_Mid_hvac_Elec) <= +inf
   0 <= e_tra_out(3502_2019_South_North_hvac_Elec) <= +inf
    -inf <= phase_angle(3501_2019_Mid) <= +inf
    -inf <= phase_angle(3501_2019_North) <= +inf
    -inf <= phase_angle(3502_2019_Mid) <= +inf
    -inf <= phase_angle(3502_2019_North) <= +inf
   0 <= cap_sto_c_new(2019_Mid_Hydrogen_Elec) <= +inf
   0 <= cap_sto_c_new(2019_Mid_Pump_storage_Elec) <= +inf
   0 <= cap_sto_c_new(2019_North_Hydrogen_Elec) <= +inf
   0 <= cap_sto_c_new(2019_North_Pump_storage_Elec) <= +inf
   0 <= cap_sto_c_new(2019_South_Hydrogen_Elec) <= +inf
   0 <= cap_sto_c_new(2019_South_Pump_storage_Elec) <= +inf
   0 <= cap_sto_p_new(2019_Mid_Hydrogen_Elec) <= +inf
   0 <= cap_sto_p_new(2019_Mid_Pump_storage_Elec) <= +inf
   0 <= cap_sto_p_new(2019_North_Hydrogen_Elec) <= +inf
   0 <= cap_sto_p_new(2019_North_Pump_storage_Elec) <= +inf
   0 <= cap_sto_p_new(2019_South_Hydrogen_Elec) <= +inf
   0 <= cap_sto_p_new(2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3501_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3501_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3501_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3501_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3501_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3501_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3502_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3502_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3502_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3502_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_in(3502_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_in(3502_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3501_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3501_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3501_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3501_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3501_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3501_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3502_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3502_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3502_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3502_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_out(3502_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_out(3502_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3500_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3500_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3500_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3500_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3500_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3500_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3501_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3501_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3501_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3501_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3501_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3501_2019_South_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3502_2019_Mid_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3502_2019_Mid_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3502_2019_North_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3502_2019_North_Pump_storage_Elec) <= +inf
   0 <= e_sto_con(3502_2019_South_Hydrogen_Elec) <= +inf
   0 <= e_sto_con(3502_2019_South_Pump_storage_Elec) <= +inf
   0 <= dsm_up(3501_2019_Mid_Elec) <= +inf
   0 <= dsm_up(3501_2019_North_Elec) <= +inf
   0 <= dsm_up(3501_2019_South_Elec) <= +inf
   0 <= dsm_up(3502_2019_Mid_Elec) <= +inf
   0 <= dsm_up(3502_2019_North_Elec) <= +inf
   0 <= dsm_up(3502_2019_South_Elec) <= +inf
   0 <= dsm_down(3501_3501_2019_Mid_Elec) <= +inf
   0 <= dsm_down(3501_3501_2019_North_Elec) <= +inf
   0 <= dsm_down(3501_3501_2019_South_Elec) <= +inf
   0 <= dsm_down(3501_3502_2019_Mid_Elec) <= +inf
   0 <= dsm_down(3501_3502_2019_North_Elec) <= +inf
   0 <= dsm_down(3501_3502_2019_South_Elec) <= +inf
   0 <= dsm_down(3502_3501_2019_Mid_Elec) <= +inf
   0 <= dsm_down(3502_3501_2019_North_Elec) <= +inf
   0 <= dsm_down(3502_3501_2019_South_Elec) <= +inf
   0 <= dsm_down(3502_3502_2019_Mid_Elec) <= +inf
   0 <= dsm_down(3502_3502_2019_North_Elec) <= +inf
   0 <= dsm_down(3502_3502_2019_South_Elec) <= +inf
   0 <= e_co_sell(3501_2019_North_Elec_sell_Sell) <= +inf
   0 <= e_co_sell(3501_2019_South_Elec_sell_Sell) <= +inf
   0 <= e_co_sell(3502_2019_North_Elec_sell_Sell) <= +inf
   0 <= e_co_sell(3502_2019_South_Elec_sell_Sell) <= +inf
   0 <= e_co_buy(3501_2019_North_Elec_buy_Buy) <= +inf
   0 <= e_co_buy(3501_2019_South_Elec_buy_Buy) <= +inf
   0 <= e_co_buy(3502_2019_North_Elec_buy_Buy) <= +inf
   0 <= e_co_buy(3502_2019_South_Elec_buy_Buy) <= +inf
end
