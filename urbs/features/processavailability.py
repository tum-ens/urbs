import math
import pyomo.core as pyomo
from .modelhelper import commodity_subset


def add_availability(m):


    # Rules
    m.res_process_availability = pyomo.Constraint(m.tm,
        m.pro_output_tuples,
        rule=res_process_availability_rule,
        doc='maximum process output = limited by given full load hours')

    return m


# constraints

#availability rule= max energy output in a year is limited to predefined flh (=availability) + cap_up
def res_process_availability_rule(m,  tm, stf, sit, pro, com):
#
    energy_output_sum=0
    if m.process_dict['availability'][stf, sit, pro] < 8760:
        for tm in m.tm:  
#
            energy_output_sum+=m.e_pro_out[ tm, stf, sit, pro, com] 
        return (energy_output_sum <= m.process_dict['availability'][stf, sit, pro] * m.cap_pro[stf, sit, pro])
    else:
        return pyomo.Constraint.Skip





