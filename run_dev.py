import coopr.environ
import matplotlib.pyplot as plt
import os
import urbs
from coopr.opt.base import SolverFactory
from datetime import datetime
import matplotlib as mpl



# SCENARIOS
def scenario_status_quo(data):
    # change maximum installable capacity: scenario status quo
    pro = data['process']
    pro.loc[('South', 'Photovoltaics'), 'cap-up'] = 0
    pro.loc[('South', 'CHP gas turbine'), 'cap-up'] = 0
    pro.loc[('South', 'CHP gas engine'), 'cap-up'] = 0
    return data

def scenario_optimized(data):
    # do nothing
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


def setup_solver(optim, logfile='solver.log'):
    """ """
    if optim.name == 'gurobi':
        # reference with list of option names
        # http://www.gurobi.com/documentation/5.6/reference-manual/parameters
        optim.set_options("logfile={}".format(logfile))
        optim.set_options("Threads="+str(8))
        # optim.set_options("TimeLimit=7200")  # seconds
        # optim.set_options("MIPGap=5e-4")  # default = 1e-4
    elif optim.name == 'glpk':
        # reference with list of options
        # execute 'glpsol --help'
        optim.set_options("log={}".format(logfile))
        # optim.set_options("tmlim=7200")  # seconds
        # optim.set_options("mipgap=.0005")
    else:
        print("Warning from setup_solver: no options set for solver "
              "'{}'!".format(optim.name))
    return optim


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

    # create model
    model = urbs.create_model(data, timesteps)
    prob = model.create()

    # refresh time stamp string and create filename for logfile
    now = prob.created
    log_filename = os.path.join(result_dir, '{}-{}.log').format(sce, now)

    # solve model and read results
    optim = SolverFactory('gurobi')  # cplex, glpk, gurobi, ...
    optim = setup_solver(optim, logfile=log_filename)
    result = optim.solve(prob, tee=True)
    prob.load(result)

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
        'South': (230, 200, 200),
        'Mid': (200, 230, 200),
        'North': (200, 200, 230)}
    for country, color in my_colors.iteritems():
        urbs.COLORS[country] = color

    my_process_colors = {
        'HAWT': (122, 179, 225),
        'VAWT': (39, 114, 175),
        'CHP gas engine': (94, 58, 28),
        'CHP gas turbine': (191, 121, 57),
        'Gas heating': (136, 0, 21),
        'Feed-in': (181, 230, 29),
        'Feed-in heat': (181, 230, 29),
        'Purchase': (244, 114, 22),
        'Purchase heat': (244, 114, 22),
        'Slack powerplant elec': (163, 74, 130),
        'Slack powerplant heat': (121, 55, 97)}
    for process, color in my_process_colors.iteritems():
        urbs.COLORS[process] = color

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

        # change the figure ylable
        ax0.set_ylabel('Power (kW)')
        ax1 = fig.get_axes()[1]
        ax1.set_ylabel('Energy (kWh)')

        # add decimal point: y axsis - storage
        if ax1.get_ylim()[1] < 5:
            decimal_point = mpl.ticker.FuncFormatter(
                lambda x, pos: '{0:.1f}'.format(x))
            ax1.yaxis.set_major_formatter(decimal_point)

        # save plot to files 
        for ext in ['png', 'pdf']:
            fig_filename = os.path.join(
                result_dir, '{}-{}-{}-{}.{}').format(sce, com, sit, now, ext)
            fig.savefig(fig_filename, bbox_inches='tight')
        plt.close(fig)
    return prob

if __name__ == '__main__':
    input_file = 'development.xlsx'
    result_name = os.path.splitext(input_file)[0]  # cut away file extension
    result_dir = prepare_result_directory(result_name)  # name + time stamp

    (offset, length) = (3999, 10*24)  # time step selection
    timesteps = range(offset, offset+length+1)

    # select scenarios to be run
    scenarios = [
        scenario_status_quo,
        scenario_optimized]
    scenarios = scenarios[1:]  # select by slicing

    for scenario in scenarios:
        prob = run_scenario(input_file, timesteps, scenario, result_dir)
