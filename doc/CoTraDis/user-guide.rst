.. _3_user-guide:

CoTraDis user guide
====================

This section serves as a guide for those who would like to use the CoTraDis module.
First the adjusted runme file is introduced. Next, special input parameters to consider are presented.
Finally, the default scenario framework is discussed in order to enable you to define own model scenarios.

.. _runme-section:

run_transdist.py
------------------

The script starts with the specification of the input files. The input folder must be located in the same folder as the ``run_transdist.py`` script.
In this folder the main transmission system file is located including another folder that contains input files for each desired microgrid type.
The desired input files to be imported must be defined at the beginning of the script

::

	input_files = 'Transmission_Level.xlsx'  # for single year file name, for intertemporal folder name
	microgrid_files = ['Microgrid_rural_A.xlsx','Microgrid_urban_A.xlsx']
	
	
Then the result name and the result directory is set

::

	result_name = 'Trans-Dist'
	
Next, the objective function to be minimized by the model is determined (options: 'cost' or 'CO2')

::

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective
	
and the solver to use muste be chosen. Gurobi is our predefined solver - to use it an academic license must be downloaded
at the  `Gurobi website <https://www.gurobi.com/downloads/free-academic-license/>`__ after creating an account.

::

	# Choose Solver (cplex, glpk, gurobi, ...)
	solver = 'gurobi'

To apply time series aggregation methods (tsam) the number of typical periods and the length of the periods must be defined:

::

	# input data for tsam method
	noTypicalPeriods = 4
	hoursPerPeriod = 168
	
Watch out! An increasing number of typeperiods crucially influences the computational load due to the introduced seasonal storage constraint (all subsequent alternating typeperiods must be modeled).
Evidence has shown, that especially at the beginning when increasing the `noTypicalPeriods` parameter, the computational load increases rapidly.
For higher numbers, the constellation of subsequent weeks varies which can even result in lower weeks to model (noTypicalPeriods : modeledWeeks - 2 : 3, 4 : 9, 6 : 14, 8 : 18, 10 : 21, 12 : 20).
These values may change for each individual model with its constellation of timeseries for intermittent resources and demand.

If you don't use tsam you must choose the time range to be modeled (default of 8760 hours for the entire year)

::

	# simulation timesteps
	(offset, length) = (0,8760)  # time step selection



.. _excel-input-section:

Remarks on excel input data
-----------------------------

Tranmission system input file:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sheet "Global":

- `transDist` parameter to concatenate distribution system data: 1 or 0

- `tsam` parameter: 1 or 0

Sheet "Site":

- `microgrid setting` to select desired microgrids per region: list

- `multiplicator` to scale chosen microgrids: list

.. note::
    **Multiplicators must fit to the defined microgrids and the research question**

    The modular definition of the microgrids and the scaling can be freely performed depending on the research topic. The residential quantities such as demand and capacity potentials have been defined for the entire country in only two microgrids with 25 nodes togehter. Obviously, to describe the entire country they must be scaled. The multiplicators must be carefully derived to represent the desired system.
    The default microgrids and the related multiplicators have been derived to include all residential buildings in Germany. We categorized the DS into two possible microgrid modules: Rural and urban areas differ in some aspects such as population density, PV potentials and mobility requirements.


Distribution system input file:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sheet "Site":

- `base voltage` of the distribution system level: value

- `ref-node` to indicate reference node with transformer interface: 1 or 0

- `min/max-voltage` to define permissible voltage range: value

.. note::
    **Permissible voltage range must be adjusted to the length of microgrid branches**

    In our case study for German distribution systems we identified a possible voltage range from 0.95 to 1.03 per unit.
    These values are representative for actual grids which have more nodes that can be modeled.
    Therefore, to get a meaningful voltage constraint, the range is reduced.

Sheet "Commodity":

- commodities must be defined for all nodes that are desired to be constrained by a vertex rule of the commodity (for the transmission of the commodity also if no processes of the commodity are defined)

Sheet "Process":

- the power factor parameter `pf-min`: value
- declare own slack process for better debugging on distribution system level
- if the expansion of distribution system components is intended to be included into the optimization price parameters must be defined (e.g. when comparing two different technologies to cover the heat demand)


Sheet "Transmission":

- the impedance parameters are determining for the power flow model to be applied (resistance, reactance):
    - (#N/A, #N/A) : transport model
    - (#N/A, >0) : DCPF model
    - (>0, >0) : LinDistFlow model

- transmission distribution interface transformer parameter must be chosen carefully (similar approach to voltage range)

Sheet "SupIm":

- timeseries for intermittent ressources are automatically taken from the regions the microgrids are defined in


Remarks on the default scenario approach
------------------------------------------
.. _scenario-comparison-section:

When transmission and distribution demand data are combined, special care must be taken to avoid a double counting.
For instance, the default electricity demand curve per German regions already include the residential electricity consumption.
In the conducted study, a central research question was to analyze the impact of increasing shares of active distgribution grids.
Therefore, when introducing distribution systems with demand curves for households the hourly total distribution system demand within
a region must be substracted from the respective transmission system demand.

To secure comparbility between scenarios, the total demand must be constant. Thus, if the distribution network is only
partly modeled as active grid, the demand must be shifted between both system levels.
For the basic electricity demand, this is implemented in the ``transdist.py`` module with the `shift_demand` function that
subtracts less from the top region demand with decreasing distribution network shares (`transdist_share`).
When multiple scenarios are modeled, it is recommended to run first the 100% active distribution grid scenario,
as thereby the maximum demand for mobility and heat can be stored to be used in subsequent scenarios with lower `transdist_shares`.

::

    ### Shift demand between scenarios for better comparability
    def shift_demand(data, microgrid_data_input, set_number, type_nr, demand_shift, loadprofile_BEV, top_region_name,
                     mobility_transmission_shift, heat_transmission_shift, transdist_eff):
        ### subtract private electricity demand at distribution level (increased by tdi efficiency) from transmission level considering line losses
        data['demand'].iloc[:, set_number] -= demand_shift.loc[:, pd.IndexSlice[:, 'electricity']].sum(axis=1) / transdist_eff

        if data['transdist_share'].values[0] == 1:
            ### store scaled full mobility and heat demand for 100% active distribution network for subsequent scenarios
            mobility_transmission_shift[(top_region_name, type_nr)] = loadprofile_BEV * demand_shift.loc[:, pd.IndexSlice[:, 'mobility']].sum().sum() / transdist_eff
            COP_ts = microgrid_data_input['eff_factor'].loc[:, pd.IndexSlice[:, 'heatpump_air']].iloc[:,0].squeeze() #get COP timeseries to transform hourly heat to electricity demand
            heat_transmission_shift[(top_region_name, type_nr)] = demand_shift.loc[:, pd.IndexSlice[:, 'heat']].sum(axis=1).divide(COP_ts).fillna(0) / transdist_eff
        return data, mobility_transmission_shift, heat_transmission_shift

.. note::
    **Transformer losses at the interface are important for scenario comparability**
    When modeling a fully active distribution grid a higher share of the demand is modeled within the distribution system.
    Having energy flows between both systems and a transformer at the interface that is modeled with losses, the total energy that is required by the energy system increases.
    Therefore, to compare equal energy requirements for all scenarios, these losses are considered with the 'transdis_eff' parameter in the shifting processes.

In comparison, the central demand does not include charging of battery electric vehicles or the widespread application of heatpumps.
Hence, for the mobility and heat demand the scenario module has been extended with a function to consider this.
The `variable_distribution_share` function on one side shifts the inflexible demand curves to the transmission system level.
On the other side, it ensures that the PV-potentials (depending on the distribution grid input parameters) are constant for all scenarios.

::

    def variable_distribution_share(data, cross_scenario_data, transdist_share):
        data['transdist_share'] = pd.Series([transdist_share])  # defined as series to avoid validation error
        if transdist_share < 1:
            # recommended: if TD100 is run first, cross scenario data have been stored and can be automatically used for subsequent scenarios
            if bool(cross_scenario_data):
                # expand cap-up capacities of PV_utility_rooftop for shares < 1 in order to achieve equal maximum PV potentials
                # within all scenarios for better comparability from cross_scenario data
                data['process'].loc[pd.IndexSlice[:, :, 'PV_utility_rooftop'], 'cap-up'] = data['process'].loc[pd.IndexSlice[:, :,'PV_utility_rooftop'], 'cap-up'].values \
                                                                                           + (1 - transdist_share) * cross_scenario_data['PV_cap_shift'].values
                # read additional demand (BEV, Heat) from cross_scenario data
                additional_demand_mobility = cross_scenario_data['mobility_transmission_shift']
                additional_demand_heat = cross_scenario_data['heat_transmission_shift']

            # add additional electricity demand for mobility and heat on transmission level
            for col in data['demand']:
                if col[0] in list(additional_demand_mobility.columns):
                    data['demand'].loc[:, col] += additional_demand_mobility.loc[:, col[0]] * (1 - transdist_share)
                if col[0] in list(additional_demand_heat.columns):
                    data['demand'].loc[:, col] += additional_demand_heat.loc[:, col[0]]  * (1 - transdist_share)
        return data, cross_scenario_data

The responsible `transdist_share` is defined in the scenario module too, by adjusting the respective parameter (e.g. for a 66% active distribution grid):

::

    def transdist66(data, cross_scenario_data):
        data['global_prop'].loc[pd.IndexSlice[:, 'TransDist'], 'value'].iloc[0] = 1
        data, cross_scenario_data = variable_distribution_share(data, cross_scenario_data, 0.66)
        return data, cross_scenario_data


Before using the scenario framework you should answer the following question:
`Do you want to consider different shares for active distribution systems?`

- Yes - Than you need to understand the scenario implementations as described above.

- No - Than you basically need to know that within the default framework normal electricity demand needs to be defined within the transmission system demand timeseries, but additional electricity demand from sector coupling must not be included.

.. _postprocessing:
