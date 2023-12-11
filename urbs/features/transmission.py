import math
import pyomo.core as pyomo
import numpy as np

def e_tra_domain_rule1(m, tm, stf, sin, sout, tra, com):
    # assigning e_tra_in and e_tra_out variable domains for transport and DCPF
    if (stf, sin, sout, tra, com) in m.tra_tuples_dc:
        return pyomo.Reals
    elif (stf, sin, sout, tra, com) in m.tra_tuples_tp:
        return pyomo.NonNegativeReals


def e_tra_domain_rule2(m, tm, stf, sin, sout, tra, com):
    # assigning e_tra_in and e_tra_out variable domains for transport, DCPF and ACPF
    if (stf, sin, sout, tra, com) in m.tra_tuples_dc:
        return pyomo.Reals
    elif (stf, sin, sout, tra, com) in m.tra_tuples_ac:
        return pyomo.Reals
    elif (stf, sin, sout, tra, com) in m.tra_tuples_tp:
        return pyomo.NonNegativeReals


def remove_duplicate_transmission(transmission_keys):
    # removing duplicate transmissions for DCPF
    tra_tuple_list = list(transmission_keys)
    tra_tuple_list = sorted(tra_tuple_list, key=lambda x: x[1])
    i = 0
    while i < len(tra_tuple_list):
        for k in range(len(tra_tuple_list)):
            if (tra_tuple_list[i][1] == tra_tuple_list[k][2] and
                    tra_tuple_list[i][2] == tra_tuple_list[k][1] and
                    tra_tuple_list[i][0] == tra_tuple_list[k][0] and
                    tra_tuple_list[i][3] == tra_tuple_list[k][3]):
                del tra_tuple_list[i]
                i -= 1
                break
        i += 1
    return set(tra_tuple_list)


def add_transmission(m):
    # tranmission (e.g. hvac, hvdc, pipeline...)
    indexlist = set()
    for key in m.transmission_dict["eff"]:
        indexlist.add(tuple(key)[3])
    m.tra = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of transmission technologies')

    # transmission tuples
    m.tra_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(m.transmission_dict["eff"].keys()),
        doc='Combinations of possible transmissions, e.g. '
            '(2020,South,Mid,hvac,Elec)')
    m.tra_block_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_block_dict.keys())],
        doc='Transmissions with new block capacities')
    m.tra_decommissionable_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_decom_cap_dict.keys())],
        doc='Transmissions that can be decommissioned')

    if m.mode['int']:
        m.operational_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf * m.stf,
            initialize=[(sit, sit_, tra, com, stf, stf_later)
                        for (sit, sit_, tra, com, stf, stf_later)
                        in op_tra_tuples(m.tra_tuples, m)],
            doc='Transmissions that are still operational through stf_later'
                '(and the relevant years following), if built in stf'
                'in stf.')
        m.inst_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf,
            initialize=[(sit, sit_, tra, com, stf)
                        for (sit, sit_, tra, com, stf)
                        in inst_tra_tuples(m)],
            doc='Installed transmissions that are still operational'
                'through stf')

    # Variables
    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')
    m.cap_tra_decommissioned = pyomo.Var(
        m.tra_decommissionable_tuples,
        within=pyomo.NonNegativeReals,
        doc='Decommissioned transmission capacity (MW)')
    m.cap_tra_unit = pyomo.Var(
        m.tra_block_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='New transmission capacity blocks')

    # transmission capacity as expression object
    m.cap_tra = pyomo.Expression(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity')

    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='Power flow out of transmission line (MW) per timestep')

    # transmission
    m.def_cap_tra_new = pyomo.Constraint(
        m.tra_block_tuples,
        rule=def_cap_tra_new_rule,
        doc='cap_tra_new = tra-block * cap_tra_new')
    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')
    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')
    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')
    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

    return m


# adds the transmission features to model with DCPF model features
def add_transmission_dc(m):
    # defining transmission tuple sets for transport and DCPF model separately
    tra_tuples = set()
    tra_tuples_dc = set()
    for key in m.transmission_dict['reactance']:
        tra_tuples.add(tuple(key))
    for key in m.transmission_dc_dict['reactance']:
        tra_tuples_dc.add(tuple(key))
    tra_tuples_tp = tra_tuples - tra_tuples_dc
    tra_tuples_dc = remove_duplicate_transmission(tra_tuples_dc)
    tra_tuples = tra_tuples_dc | tra_tuples_tp

    # tranmission (e.g. hvac, hvdc, pipeline...)
    indexlist = set()
    for key in m.transmission_dict["eff"]:
        indexlist.add(tuple(key)[3])
    m.tra = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of transmission technologies')

    # Transport and DCPF transmission tuples
    m.tra_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples),
        doc='Combinations of possible transmissions,'
            'without duplicate dc transmissions'
            ' e.g. (2020,South,Mid,hvac,Elec)')
    m.tra_decommissionable_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_decom_cap_dict.keys())],
        doc='Transmissions that can be decommissioned')
    # DCPF transmission tuples
    m.tra_tuples_dc = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_dc),
        doc='Combinations of possible bidirectional dc'
            'transmissions, e.g. (2020,South,Mid,hvac,Elec)')

    m.tra_block_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_block_dict.keys())],
        doc='Transmission with new block capacities')

    # Transport transmission tuples
    m.tra_tuples_tp = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_tp),
        doc='Combinations of possible transport transmissions,'
            'e.g. (2020,South,Mid,hvac,Elec)')

    if m.mode['int']:
        m.operational_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf * m.stf,
            initialize=[(sit, sit_, tra, com, stf, stf_later)
                        for (sit, sit_, tra, com, stf, stf_later)
                        in op_tra_tuples(m.tra_tuples, m)],
            doc='Transmissions that are still operational through stf_later'
                '(and the relevant years following), if built in stf'
                'in stf.')
        m.inst_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf,
            initialize=[(sit, sit_, tra, com, stf)
                        for (sit, sit_, tra, com, stf)
                        in inst_tra_tuples(m)],
            doc='Installed transmissions that are still operational'
                'through stf')

    # Variables
    m.cap_tra_new = pyomo.Var(
        m.tra_tuples,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')
    m.cap_tra_decommissioned = pyomo.Var(
        m.tra_decommissionable_tuples,
        within=pyomo.NonNegativeReals,
        doc='Decommissioned transmission capacity (MW)')
    m.cap_tra_unit = pyomo.Var(
        m.tra_block_tuples,
        within=pyomo.NonNegativeIntegers,
        doc='New transmission capacity blocks')

    # transmission capacity as expression object
    m.cap_tra = pyomo.Expression(
        m.tra_tuples,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity')

    m.e_tra_abs = pyomo.Var(
        m.tm, m.tra_tuples_dc,
        within=pyomo.NonNegativeReals,
        doc='Absolute power flow on transmission line (MW) per timestep')
    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule1,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule1,
        doc='Power flow out of transmission line (MW) per timestep')

    m.voltage_angle = pyomo.Var(
        m.tm, m.stf, m.sit,
        within=pyomo.Reals,
        doc='Voltage angle of a site')

    # transmission
    m.def_cap_tra_new = pyomo.Constraint(
        m.tra_block_tuples,
        rule=def_cap_tra_new_rule,
        doc='cap_tra_new = tra-block * cap_tra_new')
    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')
    m.def_dc_power_flow = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=def_dc_power_flow_rule,
        doc='transmission output = (angle(in)-angle(out))/ 57.2958 '
            '* -1 *(-1/reactance) * (base voltage)^2')
    m.def_angle_limit = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=def_angle_limit_rule,
        doc='-angle limit < angle(in) - angle(out) < angle limit')
    m.def_slackbus_angle = pyomo.Constraint(
        m.tm, m.sit_slackbus,
        rule=def_slackbus_angle_rule,
        doc='(angle_slackbus = 0')
    m.e_tra_abs1 = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=e_tra_abs_rule1,
        doc='transmission dc input <= absolute transmission dc input')
    m.e_tra_abs2 = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=e_tra_abs_rule2,
        doc='-transmission dc input <= absolute transmission dc input')
    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')
    m.res_transmission_dc_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=res_transmission_ac_dc_input_by_capacity_rule,
        doc='-dcpf transmission input <= total transmission capacity')
    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')
    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples_tp,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

    return m


# adds the transmission features to model with ACPF model features
def add_transmission_ac(m, assumelowq):
    # defining transmission tuple sets for transport, DCPF and ACPF model separately
    tra_tuples = set()
    tra_tuples_dc = set()
    tra_tuples_ac = set()
    tra_tuples_kont = set()
    tra_tuples_ront = set()
    tra_tuples_hp = set()
    tra_tuples_bev = set()
    tra_tuples_reac = set()

    for key in m.transmission_dict['reactance']:
        tra_tuples.add(tuple(key))
    for key in m.transmission_dc_dict['reactance']:
        tra_tuples_dc.add(tuple(key))
    for key in m.transmission_ac_dict['resistance']:
        tra_tuples_ac.add(tuple(key))
    for key in m.transmission_kont_dict['resistance']:
        tra_tuples_kont.add(tuple(key))
    for key in m.transmission_ront_dict['resistance']:
        tra_tuples_ront.add(tuple(key))

    for key in m.transmission_dict['cap-lo']:
        if key[4] == 'electricity_hp': # LVDS
            tra_tuples_hp.add(tuple(key))
        if key[4] == 'electricity_bev': # LVDS
            tra_tuples_bev.add(tuple(key))
    for key in m.transmission_dict['resistance']:
        if key[4] == 'electricity-reactive':
            tra_tuples_reac.add(tuple(key))

    tra_tuples_tp = tra_tuples - tra_tuples_ac - tra_tuples_dc
    tra_tuples_ac = remove_duplicate_transmission(tra_tuples_ac)
    tra_tuples_dc = remove_duplicate_transmission(tra_tuples_dc)
    tra_tuples_ac_dc = tra_tuples_ac | tra_tuples_dc
    tra_tuples = tra_tuples_ac | tra_tuples_dc | tra_tuples_tp


    # tranmission (e.g. hvac, hvdc, pipeline...)
    indexlist = set()
    for key in m.transmission_dict["eff"]:
        indexlist.add(tuple(key)[3])
    m.tra = pyomo.Set(
        initialize=indexlist,
        ordered=False,
        doc='Set of transmission technologies')

    # Transport, DCPF and ACPF transmission tuples
    m.tra_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples),
        doc='Combinations of possible transmissions,'
            'without duplicate dc transmissions'
            ' e.g. (2020,South,Mid,hvac,Elec)')
    m.tra_decommissionable_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_decom_cap_dict.keys())],
        doc='Transmissions that can be decommissioned')

    # DCPF transmission tuples
    m.tra_tuples_dc = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_dc),
        doc='Combinations of possible bidirectional dc'
            'transmissions, e.g. (2020,South,Mid,hvac,Elec)')

    # ACPF transmission tuples
    m.tra_tuples_ac = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_ac),
        doc='Combinations of possible bidirectional ac'
            'transmissions, e.g. (2020,node1_A,node2_A,hvac,Elec)')

    # ACPF transmission tuples
    m.tra_tuples_kont = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_kont),
        doc='Combinations of possible conventional ONT'
            'units, e.g. (2020,node1_A,node2_A,hvac,Elec)')

    # ACPF transmission tuples
    m.tra_tuples_ront = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_ront),
        doc='Combinations of possible controllable ONT'
            'units, e.g. (2020,node1_A,node2_A,hvac,Elec)')

    # DCPF & ACPF transmission tuples together
    m.tra_tuples_ac_dc = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_ac_dc),
        doc='Combinations of possible bidirectional ac'
            'transmissions, e.g. (2020,node1_A,node2_A,hvac,Elec)')

    m.tra_block_tuples = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=[(stf, sit, sit_, tra, com)
                    for (stf, sit, sit_, tra, com) in tuple(m.tra_block_dict.keys())],
        doc='Transmission with new block capacities')

    # Transport transmission tuples
    m.tra_tuples_tp = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_tp),
        doc='Combinations of possible transport transmissions,'
            'e.g. (2020,South,Mid,hvac,Elec)')

    if m.mode['14a']: # LVDS: AC transmission tuples for the transport of electricity_hp commodity
        m.tra_tuples_hp = pyomo.Set(
            within=m.stf * m.sit * m.sit * m.tra * m.com,
            initialize=tuple(tra_tuples_hp),
            doc='Combinations of possible transport transmissions that deliver heat pump electricity,'
                'e.g. (2020,South,Mid,hvac,elec_hp)')
    else:#empty set otherwise
        m.tra_tuples_hp = pyomo.Set(
            within=m.stf * m.sit * m.sit * m.tra * m.com,
            doc='Combinations of possible transport transmissions that deliver heat pump electricity,'
                'e.g. (2020,South,Mid,hvac,elec_hp)')

    if m.mode['14a']: # LVDS: AC transmission tuples for the transport of electricity_bev commodity
        m.tra_tuples_bev = pyomo.Set(
            within=m.stf * m.sit * m.sit * m.tra * m.com,
            initialize=tuple(tra_tuples_bev),
            doc='Combinations of possible transport transmissions that deliver BEV electricity,'
                'e.g. (2020,South,Mid,hvac,elec_hp)')
    else: #empty set otherwise
        m.tra_tuples_bev = pyomo.Set(
            within=m.stf * m.sit * m.sit * m.tra * m.com,
            doc='Combinations of possible transport transmissions that deliver heat pump electricity,'
                'e.g. (2020,South,Mid,hvac,elec_hp)')

    # Transmission tuples that deliver reactive power
    m.tra_tuples_reac = pyomo.Set(
        within=m.stf * m.sit * m.sit * m.tra * m.com,
        initialize=tuple(tra_tuples_reac),
        doc='Combinations of possible transport transmissions that deliver reactive power,'
            'e.g. (2020,South,Mid,hvac,elec-reactive)')

    m.sites_ac = pyomo.Set(
        within=m.stf * m.sit * m.sit,
        initialize=set([(stf, sit_in, sit_out)
                    for (stf, sit_in, sit_out, tra, com) in m.tra_tuples_ac]),
        doc='Site pairs connected with AC lines ')

    if m.mode['int']:
        m.operational_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf * m.stf,
            initialize=[(sit, sit_, tra, com, stf, stf_later)
                        for (sit, sit_, tra, com, stf, stf_later)
                        in op_tra_tuples(m.tra_tuples, m)],
            doc='Transmissions that are still operational through stf_later'
                '(and the relevant years following), if built in stf'
                'in stf.')
        m.inst_tra_tuples = pyomo.Set(
            within=m.sit * m.sit * m.tra * m.com * m.stf,
            initialize=[(sit, sit_, tra, com, stf)
                        for (sit, sit_, tra, com, stf)
                        in inst_tra_tuples(m)],
            doc='Installed transmissions that are still operational'
                'through stf')

    # Variables
    m.cap_tra_new = pyomo.Var(
        m.tra_tuples - m.tra_tuples_hp  - m.tra_tuples_bev - m.tra_tuples_reac,
        within=pyomo.NonNegativeReals,
        doc='New transmission capacity (MW)')
    m.cap_tra_decommissioned = pyomo.Var(
        m.tra_decommissionable_tuples - m.tra_tuples_hp- m.tra_tuples_bev - m.tra_tuples_reac,
        within=pyomo.NonNegativeReals,
        doc='Decommissioned transmission capacity (MW)')
    m.cap_tra_unit = pyomo.Var(
        m.tra_block_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        within=pyomo.NonNegativeIntegers,
        doc='New transmission capacity blocks')

    # transmission capacity as expression object
    m.cap_tra = pyomo.Expression(
        m.tra_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=def_transmission_capacity_rule,
        doc='total transmission capacity')

    m.e_tra_abs = pyomo.Var(
        m.tm, m.tra_tuples_dc,
        within=pyomo.NonNegativeReals,
        doc='Absolute power flow on transmission line (MW) per timestep')
    m.e_tra_in = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule2,
        doc='Power flow into transmission line (MW) per timestep')
    m.e_tra_out = pyomo.Var(
        m.tm, m.tra_tuples,
        within=e_tra_domain_rule2,
        doc='Power flow out of transmission line (MW) per timestep')

    m.voltage_angle = pyomo.Var(
        m.tm, m.stf, m.sit,
        within=pyomo.Reals,
        doc='Voltage angle of a site')
    m.voltage_squared = pyomo.Var(
        m.tm, m.sit_tuples_ac,
        within=pyomo.Reals,
        doc='Voltage^2 of a site kV')

    # transmission
    m.def_cap_tra_new = pyomo.Constraint(
        m.tra_block_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=def_cap_tra_new_rule,
        doc='cap_tra_new = tra-block * cap_tra_new')
    m.def_transmission_output = pyomo.Constraint(
        m.tm, m.tra_tuples,
        rule=def_transmission_output_rule,
        doc='transmission output = transmission input * efficiency')

    # Power flow constraint for dc transmission lines
    m.def_dc_power_flow = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=def_dc_power_flow_rule,
        doc='transmission output = (angle(in)-angle(out))/ 57.2958 '
            '* -1 *(-1/reactance) * (base voltage)^2')

    # Power flow constraint for ac transmission lines
    m.def_ac_power_flow = pyomo.Constraint(
        m.tm, m.sites_ac,
        rule=def_ac_power_flow_rule,
        doc='voltage^2(in) = voltage^2(out) + 2 * (resistance(in_out) * Power_active(in_out) + reactance(in_out) * Power_reactive(in_out))')


    m.def_voltage_limit_upper = pyomo.Constraint(  #LVDS: equation 2.65a of Candas dissertation
        m.tm, m.sit_tuples_ac,
        rule=def_voltage_limit_upper_rule,
        doc='V^2 <= (base_voltage * max-voltage)^2. If OLTP (rONT) is built, the limit is raised to 1.1 pu')
    m.def_voltage_limit_lower = pyomo.Constraint( #LVDS: equation 2.65b of Candas dissertation
        m.tm, m.sit_tuples_ac,
        rule=def_voltage_limit_lower_rule,
        doc='(base_voltage * min-voltage)^2 <= V^2 <= If OLTP (rONT) is built, the limit is lowered to 0.9 pu')


    m.def_angle_limit = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=def_angle_limit_rule,
        doc='-angle limit < angle(in) - angle(out) < angle limit')
    m.e_tra_abs1 = pyomo.Constraint(
        m.tm, m.tra_tuples_dc,
        rule=e_tra_abs_rule1,
        doc='transmission ac/dc input <= absolute transmission ac/dc input')
    m.res_transmission_input_by_capacity = pyomo.Constraint(
        m.tm, m.tra_tuples - m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev,
        rule=res_transmission_input_by_capacity_rule,
        doc='transmission input <= total transmission capacity')

    if not assumelowq: #LVDS: equations 2.59 from Candas dissertation, if low Q/P is assumed, the first four constraints
        # are not necessary, simplifying the model.
        m.res_transmission_input_by_apparent_power_diamond_1 = pyomo.Constraint(
            m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
            rule=res_transmission_input_by_apparent_power_diamond_1_rule,
            doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
        m.res_transmission_input_by_apparent_power_diamond_4 = pyomo.Constraint(
            m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
            rule=res_transmission_input_by_apparent_power_diamond_4_rule,
            doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
        m.res_transmission_input_by_apparent_power_diamond_5 = pyomo.Constraint(
            m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
            rule=res_transmission_input_by_apparent_power_diamond_5_rule,
            doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
        m.res_transmission_input_by_apparent_power_diamond_8 = pyomo.Constraint(
            m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
            rule=res_transmission_input_by_apparent_power_diamond_8_rule,
            doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
          
    m.res_transmission_input_by_apparent_power_diamond_2 = pyomo.Constraint(
        m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=res_transmission_input_by_apparent_power_diamond_2_rule,
        doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
    m.res_transmission_input_by_apparent_power_diamond_3 = pyomo.Constraint(
        m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=res_transmission_input_by_apparent_power_diamond_3_rule,
        doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
    m.res_transmission_input_by_apparent_power_diamond_6 = pyomo.Constraint(
        m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=res_transmission_input_by_apparent_power_diamond_6_rule,
        doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
    m.res_transmission_input_by_apparent_power_diamond_7 = pyomo.Constraint(
        m.tm, m.tra_tuples_ac - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=res_transmission_input_by_apparent_power_diamond_7_rule,
        doc='four additional ac line constraints to approximate the quadratic restriction of real/reactive power')
      
    m.def_single_ont = pyomo.Constraint( #LVDS: equation 2.61 of Candas dissertation
        m.sit_slackbus,
        rule=def_single_ont_rule,
        doc='there can be only one ONT built, the existing has to be decommissioned if a new one is built')

    m.def_single_ac_cable = pyomo.Constraint( #LVDS: equation 2.54 of Candas dissertation
        m.tra_tuples_ac - m.tra_tuples_hp- m.tra_tuples_bev - m.tra_tuples_reac,
        rule=def_single_ac_cable_rule,
        doc='for a given AC line section, only one bundle of cable can be built (either single line, double line, -if defined- triple one.')

    m.res_transmission_capacity = pyomo.Constraint(
        m.tra_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac,
        rule=res_transmission_capacity_rule,
        doc='transmission.cap-lo <= total transmission capacity <= '
            'transmission.cap-up')

    m.res_transmission_symmetry = pyomo.Constraint(
        m.tra_tuples_tp - m.tra_tuples_hp- m.tra_tuples_bev,
        rule=res_transmission_symmetry_rule,
        doc='total transmission capacity must be symmetric in both directions')

    return m


# constraints

# transmission capacity (for m.cap_tra expression)
def def_transmission_capacity_rule(m, stf, sin, sout, tra, com):
    if m.mode['int']:
        if (sin, sout, tra, com, stf) in m.inst_tra_tuples:
            # if (min(m.stf), sin, sout, tra, com) in m.tra_const_cap_dict:
            if 0:
                cap_tra = m.transmission_dict['inst-cap'][
                    (min(m.stf), sin, sout, tra, com)]
            else:
                cap_tra = (
                                  sum(m.cap_tra_new[stf_built, sin, sout, tra, com]
                                      for stf_built in m.stf
                                      if (sin, sout, tra, com, stf_built, stf) in
                                      m.operational_tra_tuples) +
                                  m.transmission_dict['inst-cap']
                                  [(min(m.stf), sin, sout, tra, com)]) \
                          - sum(
                    m.cap_tra_decommissioned[stf_dec, sin, sout, tra, com] for stf_dec in m.stf if stf_dec <= stf
                    if (stf_dec, sin, sout, tra, com) in m.tra_decom_cap_dict)
        else:
            cap_tra = (
                    sum(m.cap_tra_new[stf_built, sin, sout, tra, com]
                        for stf_built in m.stf
                        if (sin, sout, tra, com, stf_built, stf) in
                        m.operational_tra_tuples)
                    - sum(
                m.cap_tra_decommissioned[stf_dec, sin, sout, tra, com] for stf_dec in m.stf if stf_dec <= stf
                if (stf_dec, sin, sout, tra, com) in m.tra_decom_cap_dict))
    else:
        if 0:  # (stf, sin, sout, tra, com) in m.tra_const_cap_dict:
            cap_tra = \
                m.transmission_dict['inst-cap'][(stf, sin, sout, tra, com)]
        else:
            cap_tra = (m.cap_tra_new[stf, sin, sout, tra, com] +
                       m.transmission_dict['inst-cap'][
                           (stf, sin, sout, tra, com)] - sum(
                        m.cap_tra_decommissioned[stf_dec, sin, sout, tra, com] for stf_dec in m.stf if stf_dec <= stf
                        if (stf_dec, sin, sout, tra, com) in m.tra_decom_cap_dict))

    return cap_tra


# new capacity built in blocks
def def_cap_tra_new_rule(m, stf, sin, sout, tra, com):
    return (m.cap_tra[stf, sin, sout, tra, com] ==
            m.cap_tra_unit[stf, sin, sout, tra, com] *
            m.transmission_dict['tra-block'][(stf, sin, sout, tra, com)])


# transmission output == transmission input * efficiency
def def_transmission_output_rule(m, tm, stf, sin, sout, tra, com):
    return (m.e_tra_out[tm, stf, sin, sout, tra, com] ==
            m.e_tra_in[tm, stf, sin, sout, tra, com] *
            m.transmission_dict['eff'][(stf, sin, sout, tra, com)])


# power flow rule for DCPF transmissions
def def_dc_power_flow_rule(m, tm, stf, sin, sout, tra, com):
    return (m.e_tra_in[tm, stf, sin, sout, tra, com] ==
            (m.voltage_angle[tm, stf, sin] - m.voltage_angle[tm, stf, sout]) / 57.2958 * -1 *
            (-1 / m.transmission_dict['reactance'][(stf, sin, sout, tra, com)])
            * m.site_dict['base-voltage'][(stf, sin)] ** 2)


# # power flow rule for ACPF transmissions
def def_ac_power_flow_rule(m, tm, stf, sin, sout): #LVDS: equation scaled by 1000 for better numerics
    if m.mode['14a']: #LVDS: 14a enabled: total P flow is sum over electricity, electricity_hp, and electricity_bev commodities
        return ( 1000 * m.voltage_squared[tm, stf, sin] == 1000 * (m.voltage_squared[tm, stf, sout] +
                 2 / 1000 * (sum(m.transmission_dict['resistance'][(st, sit_in, sit_out, tra, 'electricity')]  # P, Q: kW, voltage: kV
                    * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity']
                    for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                    if st == stf and sit_in == sin and sit_out == sout and co == 'electricity')
                            + sum(m.transmission_dict['resistance'][(st, sit_in, sit_out, tra, 'electricity')]  # P, Q: kW, voltage: kV
                                * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity_hp']
                                for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                                if st == stf and sit_in == sin and sit_out == sout and co == 'electricity_hp')
                             + sum(m.transmission_dict['resistance'][
                                       (st, sit_in, sit_out, tra, 'electricity')]  # P, Q: kW, voltage: kV
                                   * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity_bev']
                                   for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                                   if st == stf and sit_in == sin and sit_out == sout and co == 'electricity_bev')
                            + sum(m.transmission_dict['reactance'][(st, sit_in, sit_out, tra, 'electricity')]
                                  * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity-reactive']
                                  for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                                  if st == stf and sit_in == sin and sit_out == sout and co == 'electricity-reactive'))))
    else:
        return ( 1000 * m.voltage_squared[tm, stf, sin] == 1000 * (m.voltage_squared[tm, stf, sout] +
                 2 / 1000 * (sum(m.transmission_dict['resistance'][(st, sit_in, sit_out, tra, 'electricity')]  # P, Q: kW, voltage: kV
                    * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity']
                    for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                    if st == stf and sit_in == sin and sit_out == sout and co == 'electricity')
                            + sum(m.transmission_dict['reactance'][(st, sit_in, sit_out, tra, 'electricity')]
                                  * m.e_tra_in[tm, st, sit_in, sit_out, tra, 'electricity-reactive']
                                  for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                                  if st == stf and sit_in == sin and sit_out == sout and co == 'electricity-reactive'))))


            
def res_transmission_input_by_apparent_power_diamond_1_rule(m, tm, stf, sin, sout, tra, com):
    # LVDS: equation 2.60 from Candas dissertation. Seven more follows below and form the octagon (Figure 2.15)
    if m.mode['14a']: # LVDS: if 14a is enabled, total P flow is summed over electricity, electricity_hp, and electricity_bev commodities
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (  (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            + (round(np.sqrt(2),2) + 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= ((round(np.sqrt(2),2) + 1) * m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_2_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (  (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            + (round(np.sqrt(2),2) - 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= ( m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_3_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (  (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            - (round(np.sqrt(2),2) - 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= (m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_4_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (  -(m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            + (round(np.sqrt(2),2) + 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= ((round(np.sqrt(2),2) + 1) * m.dt * m.cap_tra[stf, sin, sout, tra, com] ))

def res_transmission_input_by_apparent_power_diamond_5_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return ( - (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            - (round(np.sqrt(2),2) + 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= ((round(np.sqrt(2),2) + 1) * m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_6_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (-  (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            - (round(np.sqrt(2),2) - 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= (m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_7_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return (- (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            + (round(np.sqrt(2),2) - 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= (m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


def res_transmission_input_by_apparent_power_diamond_8_rule(m, tm, stf, sin, sout, tra, com):
    if m.mode['14a']:
        hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] \
                    + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
    else:
        hp_bev_el = 0
    return ((m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el)
            - (round(np.sqrt(2),2) + 1) * m.e_tra_in[tm, stf, sin, sout, tra, 'electricity-reactive']
            <= ((round(np.sqrt(2),2) + 1) * m.dt * m.cap_tra[stf, sin, sout, tra, com] ))


# rule to hold voltage within defined permissible range
# def def_voltage_limit_rule(m, tm, stf, sin):
#    return ((m.site_dict['base-voltage'][(stf, sin)] * m.site_dict['min-voltage'][(stf, sin)]) ** 2,
##            m.voltage_squared[tm, stf, sin],
#            (m.site_dict['base-voltage'][(stf, sin)] * m.site_dict['max-voltage'][(stf, sin)]) ** 2)


# determine slackbus voltage level
def def_voltage_limit_upper_rule(m, tm, stf, sit): # LVDS
    if m.mode['transdist']:
        ront_built = sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                         for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                         if sit_in[-5:] == sit[-5:] and st == stf and tra[0:4] == 'ront' and com == 'electricity') / 2
    else:
        ront_built = sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                         for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                         if st == stf and tra[0:4] == 'ront' and com == 'electricity') / 2
    return m.voltage_squared[tm, stf, sit] / m.site_dict['base-voltage'][(stf, sit)] \
           <= (m.site_dict['max-voltage'][(stf, sit)] ** 2 + ront_built * (
            1.21 - m.site_dict['max-voltage'][(stf, sit)] ** 2)) * m.site_dict['base-voltage'][(stf, sit)]


def def_voltage_limit_lower_rule(m, tm, stf, sit): # LVDS
    if m.mode['transdist']:
        ront_built = sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                         for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                         if sit_in[-5:] == sit[-5:] and st == stf and tra[0:4] == 'ront' and com == 'electricity') / 2
    else:
        ront_built = sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                         for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                         if st == stf and tra[0:4] == 'ront' and com == 'electricity') / 2
    return m.voltage_squared[tm, stf, sit] / m.site_dict['base-voltage'][(stf, sit)]  \
            >= (m.site_dict['min-voltage'][(stf, sit)] ** 2 - ront_built * (
            m.site_dict['min-voltage'][(stf, sit)] ** 2 - 0.81)) * m.site_dict['base-voltage'][(stf, sit)]


# reference nodes' voltage angle in subsystems are set to zero (not necessary but for clearness)
def def_slackbus_angle_rule(m, tm, stf, sin):
    return m.voltage_angle[tm, stf, sin] == 0


def def_single_ont_rule(m, stf, sit): # LVDS
    return (sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                if sit_in == sit and st == stf and tra[0:4] == 'ront' and com == 'electricity') +
            sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, com)]
                for (st, sit_in, sit_out, tra, com) in m.tra_tuples
                if sit_in == sit and st == stf and tra[0:4] == 'kont' and com == 'electricity') == 1)


# reference nodes' voltage angle in subsystems are set to zero (not necessary but for clearness)
def def_single_ac_cable_rule(m, stf, sin, sout, tra, com): # LVDS
    return (sum(m.cap_tra_unit[(st, sit_in, sit_out, tra, co)]
                for (st, sit_in, sit_out, tra, co) in m.tra_tuples_ac
                if sit_in == sin and sit_out == sout and stf == st and com == co) == 1)


# voltage angle difference rule for DCPF transmission
def def_angle_limit_rule(m, tm, stf, sin, sout, tra, com):
    return (- m.transmission_dict['difflimit'][(stf, sin, sout, tra, com)],
            (m.voltage_angle[tm, stf, sin] - m.voltage_angle[tm, stf, sout]),
            m.transmission_dict['difflimit'][(stf, sin, sout, tra, com)])


# first rule for creating absolute transmission input
def e_tra_abs_rule1(m, tm, stf, sin, sout, tra, com):
    return (m.e_tra_in[tm, stf, sin, sout, tra, com] <=
            m.e_tra_abs[tm, stf, sin, sout, tra, com])


# second rule for creating absolute transmission input
def e_tra_abs_rule2(m, tm, stf, sin, sout, tra, com):
    return (- m.e_tra_in[tm, stf, sin, sout, tra, com] <=
            m.e_tra_abs[tm, stf, sin, sout, tra, com])


# transmission input <= transmission capacity
def res_transmission_input_by_capacity_rule(m, tm, stf, sin, sout, tra, com):
    if com == 'electricity':
        if m.mode['14a']: # LVDS: 14a enabled, P flows are summed over electricity, electricity_hp and electricity_bev commodities
            hp_bev_el = m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_hp'] + m.e_tra_in[tm, stf, sin, sout, tra, 'electricity_bev']
        else:
            hp_bev_el = 0
        return (m.e_tra_in[tm, stf, sin, sout, tra, 'electricity'] + hp_bev_el <=
                m.dt * m.cap_tra[stf, sin, sout, tra, com])
    else:
        return (m.e_tra_in[tm, stf, sin, sout, tra, com]  <=
                m.dt * m.cap_tra[stf, sin, sout, tra, com])

# - ac_dc transmission input <= transmission capacity
def res_transmission_ac_dc_input_by_capacity_rule(m, tm, stf, sin, sout, tra, com):
    return (- m.e_tra_in[tm, stf, sin, sout, tra, com] <=
            m.dt * m.cap_tra[stf, sin, sout, tra, com])


# lower bound <= transmission capacity <= upper bound
def res_transmission_capacity_rule(m, stf, sin, sout, tra, com):
    return (m.transmission_dict['cap-lo'][(stf, sin, sout, tra, com)],
            m.cap_tra[stf, sin, sout, tra, com],
            m.transmission_dict['cap-up'][(stf, sin, sout, tra, com)])


# transmission capacity from A to B == transmission capacity from B to A
def res_transmission_symmetry_rule(m, stf, sin, sout, tra, com):
    return m.cap_tra[stf, sin, sout, tra, com] == (m.cap_tra[stf, sout, sin, tra, com])

# transmission balance
def transmission_balance(m, tm, stf, sit, com):
    """called in commodity balance
    For a given commodity co and timestep tm, calculate the balance of
    import and export """

    return (sum(m.e_tra_in[(tm, stframe, site_in, site_out,
                            transmission, com)]
                # exports increase balance
                for stframe, site_in, site_out, transmission, commodity
                in m.tra_tuples
                if (site_in == sit and stframe == stf and
                    commodity == com)) -
            sum(m.e_tra_out[(tm, stframe, site_in, site_out,
                             transmission, com)]
                # imports decrease balance
                for stframe, site_in, site_out, transmission, commodity
                in m.tra_tuples
                if (site_out == sit and stframe == stf and
                    commodity == com)))


# transmission cost function
def transmission_cost(m, cost_type):
    """returns transmission cost function for the different cost types"""
    if cost_type == 'Invest':
        cost = sum(m.cap_tra_new[t] *
                   m.transmission_dict['inv-cost'][t] *
                   m.transmission_dict['invcost-factor'][t]
                   for t in m.tra_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac) - sum(
            m.cap_tra_decommissioned[t] *
            m.transmission_dict['decom-saving'][t] * # LVDS
            m.transmission_dict['invcost-factor'][t]
            for t in m.tra_decom_cap_dict - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac)
        if m.mode['int']:
            cost -= sum(m.cap_tra_new[t] *
                        m.transmission_dict['inv-cost'][t] *
                        m.transmission_dict['overpay-factor'][t]
                        for t in m.tra_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac)
            cost += sum(m.cap_tra_decommissioned[t] *
                        m.transmission_dict['decom-saving'][t] * # LVDS
                        m.transmission_dict['overpay-factor'][t]
                        for t in m.tra_decom_cap_dict - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac)
        return cost
    elif cost_type == 'Fixed':
        return sum(m.cap_tra[t] * m.transmission_dict['fix-cost'][t] *
                   m.transmission_dict['cost_factor'][t]
                   for t in m.tra_tuples - m.tra_tuples_hp - m.tra_tuples_bev - m.tra_tuples_reac)
    elif cost_type == 'Variable':
        if m.mode['dcpf']:
            return sum(m.e_tra_in[(tm,) + t] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                       m.transmission_dict['var-cost'][t] *
                       m.transmission_dict['cost_factor'][t]
                       for tm in m.tm
                       for t in m.tra_tuples_tp) + \
                   sum(m.e_tra_abs[(tm,) + t] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                       m.transmission_dict['var-cost'][t] *
                       m.transmission_dict['cost_factor'][t]
                       for tm in m.tm
                       for t in m.tra_tuples_dc)
        if m.mode['acpf']:
            return sum(m.e_tra_in[(tm,) + t] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                       m.transmission_dict['var-cost'][t] *
                       m.transmission_dict['cost_factor'][t]
                       for tm in m.tm
                       for t in m.tra_tuples_tp) + \
                   sum(m.e_tra_abs[(tm,) + t] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                       m.transmission_dict['var-cost'][t] *
                       m.transmission_dict['cost_factor'][t]
                       for tm in m.tm
                       for t in m.tra_tuples_dc)
        else:
            return sum(m.e_tra_in[(tm,) + t] * m.weight * m.typeperiod['weight_typeperiod'][(m.stf_list[0], tm)] *
                       m.transmission_dict['var-cost'][t] *
                       m.transmission_dict['cost_factor'][t]
                       for tm in m.tm
                       for t in m.tra_tuples)


def op_tra_tuples(tra_tuple, m):
    """ s.a. op_pro_tuples
    """
    op_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in tra_tuple:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(sorted_stf):
                if (stf_later +
                        m.global_prop_dict['value'][(max(sorted_stf), 'Weight')] -
                        1 <= stf + m.transmission_dict['depreciation'][
                            (stf, sit1, sit2, tra, com)]):
                    op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            elif (sorted_stf[index_helper + 1] <=
                  stf + m.transmission_dict['depreciation'][
                      (stf, sit1, sit2, tra, com)] and stf <= stf_later):
                op_tra.append((sit1, sit2, tra, com, stf, stf_later))
            else:
                pass

    return op_tra


def inst_tra_tuples(m):
    """ s.a. inst_pro_tuples
    """
    inst_tra = []
    sorted_stf = sorted(list(m.stf))

    for (stf, sit1, sit2, tra, com) in m.inst_tra.index:
        for stf_later in sorted_stf:
            index_helper = sorted_stf.index(stf_later)
            if stf_later == max(m.stf):
                if (stf_later +
                        m.global_prop_dict['value'][(max(sorted_stf), 'Weight')] -
                        1 < min(m.stf) + m.transmission_dict['lifetime'][
                            (stf, sit1, sit2, tra, com)]):
                    inst_tra.append((sit1, sit2, tra, com, stf_later))
            elif (sorted_stf[index_helper + 1] <= min(m.stf) +
                  m.transmission_dict['lifetime'][
                      (stf, sit1, sit2, tra, com)]):
                inst_tra.append((sit1, sit2, tra, com, stf_later))

    return inst_tra
