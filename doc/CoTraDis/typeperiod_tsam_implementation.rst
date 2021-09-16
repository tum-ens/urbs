.. _typeperiod_tsam_implementation:

"tsam" type-period implementation
=================================

A simple type period module in 'urbs', that first has been adapted into the urbs framework by Daniel Zinsmeister,
allows to scale selected periods to represent the entire year. This approach is popular in energy system modeling due to
frequent patterns in design-relevant profiles such as demand curves or solar irradiation timeseries.
For example, typical weeks for summer and winter time can be chosen and scaled with the
corresponding incidence of expected summer/winter weeks. Thereby, economic and environmental impacts such as
system costs or CO2 emissions are scaled appropriately. The challenge by doing so is to choose the most representative
week of a season. The chosen timestep selection must apply for all given timeseries. Considering a single profile, for
instance the solar irradiation curve, and aiming to get only two typical periods for summer and winter, it might be
possible to manually choose the most suitable weeks of the year. However, our model considers approximately 100
distinct profiles, based on several type-weeks to increase accuracy while staying within the available computational limits.
Hence, it is not possible to manually choose the most suitable representative periods and an intelligent automated method is necessary instead.
Therefore, to choose the best fitting typeperiods an open source python package called tsam is used, that applies machine
learning methods and has been developed by Leander Kotzur, Maximilian Hoffmann, Peter Markewitz, Martin Robinius and Detlef Stolten.
To understand the tsam procedure in detail see the provided `tsam documentation <https://tsam.readthedocs.io/en/latest/index.html>`__.

Summarized, a predefined number of type periods with a selected number of hours per period is calculated to optimally represent
the original data for all timeseries simultaneously. This is achieved by optimizing cluster groups with the Root-Mean-Squared-Error
(RMSE) as objective functional value. Thereby, redundant data are reduced, substantially decreasing computational time for energy system models.

Before giving the timeseries data to the tsam algorithm, for all redundant profiles, a 'Python' dictionary is created to
remember the equal profiles which have been handed over. Next all duplicates are deleted.
By doing so the number of input timeseries in our approach could be reduced from 1638 to 95.

::

    def run_tsam(data, noTypicalPeriods, hoursPerPeriod, cross_scenario_data):
        ###bring together all time series data
        time_series_data = pd.concat([data['demand'], data['supim'], data['buy_sell_price'], data['eff_factor']], axis=1, sort=True)
        ### dict which allocates the first equal column of the dataframe to each column before droping duplicates of dataframe
        equal_col_dict = dict()
        for col1 in time_series_data.columns:
            time_series_data2 = time_series_data.drop(columns = col1)
            for col2 in time_series_data2.columns:
                if time_series_data[col1].equals(time_series_data2[col2]):
                    equal_col_dict[col1] = col2
                    break
        ### drop duplicate timeseries
        time_series_data = time_series_data.T.drop_duplicates().T

This dictionary is used after the application of the timeseries aggregation (TSA) to allocate the results to all original profiles.

The basic idea behind the typical periods is to weight cluster periods based on their total occurrence number.
The exact sequence of periods and thus the transition between distinct periods is not considered. On one hand, this
approach is reasonable as the total number of periods to model stays low and by this the computation time is reduced.
On the other hand, it disregards the possibility of energy exchange between periods. Thus, storage components must be
modelled with a cyclicity condition as a conservative constraint between periods. This means, the initial and final states
of charge (SOC) of storages must be equal for all periods. The main disadvantage is that long-term storage solutions
that are essential for RE-dominant energy systems cannot be considered appropriately.
Therefore, we apply a time series aggregation method with typical weeks combined with an additional storage constraint that enables
energy exchange between consecutive, alternating type periods (for instance the type periods A and B). This relaxes
the cyclicity condition within a given type period, i.e. an overall SOC change within a given type period A is allowed.

After the definition of required sets and variables important rules to implement this idea are introduced. These are listed below:

::

    ### SOC rule for each repeating typeperiod
    def res_delta_SOC(m, t_0, t_end, stf, sit, sto, com):
        return ( m.deltaSOC[t_end, stf, sit, sto, com] ==
                 (m.typeperiod_weights[t_end] - 1) * (m.e_sto_con[t_end, stf, sit, sto, com] - m.e_sto_con[t_0, stf, sit, sto, com]))

    ### new storage rule using tsam considering the delta SOC per repeating typeperiod
    def res_typeperiod_deltaSOC_rule(m, t_A, t_B, stf, sit, sto, com):
        return (m.e_sto_con[t_B, stf, sit, sto, com] ==
                m.e_sto_con[t_A, stf, sit, sto, com] + m.deltaSOC[t_A, stf, sit, sto, com])

    ### new ciclycity rule for typeperiods
    def res_storage_state_cyclicity_rule_typeperiod(m, stf, sit, sto, com):
        return (m.e_sto_con[m.t[len(m.t)], stf, sit, sto, com] >=
                m.e_sto_con[m.t[1], stf, sit, sto, com] - m.deltaSOC[m.t[len(m.t)], stf, sit, sto, com])

The basic idea is illustrated below for four typical weeks:

.. image:: graphics/TSA.pdf


