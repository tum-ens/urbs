import coopr.environ
import os
import urbs
from coopr.opt.base import SolverFactory
from datetime import datetime


# SCENARIOS
def scenario_base(data):
    # do nothing
    return data


def scenario_stock_prices(data):
    # change stock commodity prices
    co = data['commodity']
    stock_commodities_only = (co.index.get_level_values('Type') == 'Stock')
    co.loc[stock_commodities_only, 'price'] *= 1.5
    return data


def scenario_co2_limit(data):
    # change global CO2 limit
    hacks = data['hacks']
    hacks.loc['Global CO2 limit', 'Value'] = 50000
    return data


def scenario_north_process_caps(data):
    # change maximum installable capacity
    pro = data['process']
    pro.loc[('North', 'Hydro plant'), 'cap-up'] *= 0.5
    pro.loc[('North', 'Biomass plant'), 'cap-up'] *= 0.25
    return data


def scenario_all_together(data):
    # combine all other scenarios
    data = scenario_stock_prices(data)
    data = scenario_co2_limit(data)
    data = scenario_north_process_caps(data)
    return data 


def prepare_result_directory(result_name):
    """ create a time stamped directory within the result folder """
    # timestamp for result directory
    now = datetime.now().strftime('%Y%m%dT%H%M%S')
    
    # create result directory if not existent
    result_dir = os.path.join('result', '{}-{}'.format(result_name, now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        
    return result_dir


def run_scenario(input_file, timesteps, scenario, result_dir):
    """ run an urbs model for given input, time steps and scenario
    
    Args:
        input_file: filename to an Excel spreadsheet for urbs.read_excel
        timesteps: a list of timesteps, e.g. range(0,8761)
        scenario: a scenario function that modifies the input data dict
        result_dir: directory name for result spreadsheet and plots
        
    Returns:
        the urbs model instance
    """
    
    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = urbs.read_excel(input_file)
    data = scenario(data)

    # create model, solve it, read results
    model = urbs.create_model(data, timesteps)
    prob = model.create()
    optim = SolverFactory('glpk')  # cplex, glpk, gurobi, ...
    result = optim.solve(prob, tee=True)
    prob.load(result)
    
    # refresh time stamp string
    now = prob.created
    
    # write report to spreadsheet
    urbs.report(
        prob,
        os.path.join(result_dir, '{}-{}.xlsx').format(sce, now),
        prob.com_demand, prob.sit)

    # store optimisation problem for later re-analysis
    urbs.save(
        prob,
        os.path.join(result_dir, '{}-{}.pgz').format(sce, now))

    # add or change plot colors
    my_colors = {
        'Vled Haven': (230, 200, 200),
        'Stryworf Key': (200, 230, 200),
        'Qlyph Archipelago': (200, 200, 230),
        'Jepid Island': (215,215,215)}
    for country, color in my_colors.iteritems():
        urbs.COLORS[country] = color
    
    # create timeseries plot for each demand (site, commodity) timeseries
    for sit, com in prob.demand.columns:
        # create figure
        fig = urbs.plot(prob, com, sit)
        
        # change the figure title
        ax0 = fig.get_axes()[0]
        nice_sce_name = sce.replace('_', ' ').title()
        new_figure_title = ax0.get_title().replace(
            'Energy balance of ', '{}: '.format(nice_sce_name))
        ax0.set_title(new_figure_title)
        
        # save plot to files 
        for ext in ['png', 'pdf']:
            fig_filename = os.path.join(
                result_dir, '{}-{}-{}-{}.{}').format(sce, com, sit, now, ext)
            fig.savefig(fig_filename, bbox_inches='tight')
    
    return prob            
            
if __name__ == '__main__':
    input_file = 'newsealand.xlsx'
    result_name = os.path.splitext(input_file)[0]  # cut away file extension
    result_dir = prepare_result_directory(result_name)  # name + time stamp

    (offset, length) = (3700, 14*24)  # time step selection
    timesteps = range(offset, offset+length+1)
    
    # select scenarios to be run
    scenarios = [
        scenario_base,
        scenario_co2_limit]
    
    for scenario in scenarios:
        prob = run_scenario(input_file, timesteps, scenario, result_dir)
